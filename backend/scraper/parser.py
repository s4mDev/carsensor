"""
Скрапер carsensor.net на основе Playwright (Chromium headless).

Почему Playwright, а не обычный httpx?
  carsensor.net частично рендерит UI через JavaScript и может вернуть
  страницу с Cloudflare-проверкой при запросах от обычного HTTP-клиента.
  Playwright запускает настоящий браузер, поэтому обходит JS-рендеринг
  и большинство антибот-фильтров автоматически.

Если структура HTML на сайте изменится — обновите селекторы.
Для удобного поиска актуальных селекторов запустите локально:
  playwright codegen https://www.carsensor.net/
"""

import logging
import re
from dataclasses import dataclass, field

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

from scraper.translations import (
    translate_brand,
    translate_model,
    translate_body_type,
    translate_transmission,
    translate_fuel_type,
    translate_color,
    parse_year,
    parse_mileage_km,
    parse_price_jpy,
    parse_engine_volume_litres,
    parse_inspection_date,
)


logger = logging.getLogger(__name__)

# ── URL-адреса ────────────────────────────────────────────────────────────────
BASE_URL = "https://www.carsensor.net"

# sort=ND — сортировка по дате добавления (新着順 = новые первыми).
# Важно: sort=NEW — это специальная "витрина новинок" (~30 объявлений без пагинации).
# sort=ND — полноценный поиск по всему каталогу с реальной пагинацией.
SEARCH_URL = "https://www.carsensor.net/usedcar/search.php?sort=ND"

# Количество страниц листинга за один запуск (≈ 30 машин на странице).
# 4 страницы = ~120 объявлений — достаточно для покрытия новинок за час.
MAX_LISTING_PAGES = 4

# Каждые N машин браузер перезапускается чтобы освободить накопленную память.
# Playwright/Chromium при долгой работе расходует ~500MB+, что приводит к OOM Kill.
BROWSER_RESTART_EVERY = 15

# Пауза между запросами (сек) — чтобы не перегружать сервер сайта
REQUEST_DELAY = 1.5


@dataclass
class CarData:
    source_url: str
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    mileage: int | None = None
    price: int | None = None
    transmission: str | None = None
    body_type: str | None = None
    color: str | None = None
    engine_volume: float | None = None
    fuel_type: str | None = None
    inspection_date: str | None = None
    photos: list[str] = field(default_factory=list)


async def _safe_text(page: Page, selector: str) -> str | None:
    """Возвращает innerText первого найденного элемента или None."""
    try:
        element = await page.query_selector(selector)
        if element:
            return (await element.inner_text()).strip()
    except Exception:
        pass
    return None


def _extract_car_urls_from_page(hrefs: list[str]) -> list[str]:
    """Из списка href-ов отбирает только ссылки на страницы объявлений."""
    car_urls = []
    for href in hrefs:
        if href and re.search(r"/usedcar/detail/[A-Z0-9]+/", href):
            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url not in car_urls:
                car_urls.append(full_url)
    return car_urls


async def _get_hrefs(page: Page) -> list[str]:
    """Возвращает все href со страницы."""
    return await page.eval_on_selector_all(
        "a[href]",
        "elements => elements.map(el => el.getAttribute('href'))",
    )


async def _collect_all_listing_urls(page: Page, max_pages: int) -> list[str]:
    """
    Открывает страницу поиска и собирает URL объявлений с нескольких страниц
    через клик на кнопку «следующая страница».

    Почему не pg= параметр:
      carsensor.net игнорирует параметр pg= в search.php и всегда
      возвращает одни и те же 30 результатов. Единственный надёжный способ
      перейти на следующую страницу — кликнуть на ссылку пагинации на самой странице.
    """
    try:
        await page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=30_000)
        # Ждём чуть дольше чтобы JS успел отрендерить список машин и кнопку пагинации
        await page.wait_for_timeout(3_000)
    except PlaywrightTimeoutError:
        logger.warning("Таймаут при загрузке страницы поиска: %s", SEARCH_URL)
        return []

    logger.info("Листинг загружен, URL: %s", page.url)

    all_car_urls: list[str] = []
    current_page_url = SEARCH_URL

    for page_number in range(1, max_pages + 1):
        hrefs = await _get_hrefs(page)
        car_urls = _extract_car_urls_from_page(hrefs)
        new_on_page = [u for u in car_urls if u not in all_car_urls]
        all_car_urls.extend(new_on_page)

        logger.info(
            "Стр.%d (%s): найдено %d объявлений, новых %d",
            page_number, current_page_url, len(car_urls), len(new_on_page),
        )

        if page_number >= max_pages:
            break

        # Кнопка «次へ» на carsensor.net — это JS-кнопка без href.
        # Класс: pager__btn__next js-carListTopPagerBtn
        # Кликаем на неё и ждём обновления списка машин.
        next_btn = await page.query_selector("button.pager__btn__next:not(.is-disabled)")
        if not next_btn:
            logger.info("Кнопка '次へ' не найдена или задизейблена — конец листинга.")
            break

        try:
            await next_btn.click()
            # Ждём пока список обновится (новые карточки загрузятся через AJAX)
            await page.wait_for_timeout(REQUEST_DELAY * 1000 + 1000)
            current_page_url = page.url
        except Exception as exc:
            logger.warning("Ошибка при клике '次へ': %s", exc)
            break

    logger.info("Сбор URL завершён. Всего уникальных объявлений: %d", len(all_car_urls))
    return all_car_urls


def _extract_brand_and_model(title_text: str) -> tuple[str | None, str | None]:
    """
    Разбирает заголовок объявления на carsensor.net.

    Форматы H1 на сайте:
      Однословная марка:  «スバル\u00a0レガシィB4\n2.5 4WD…»
      Двусловная марка:   «アルファ ロメオ\u00a0ジュリア\n2.0…»
      Только латиница:    «MINI\u00a0ミニ\n...»

    Алгоритм:
      1. Берём первую строку (до \n).
      2. Пробуем найти марку — сначала по двум токенам, затем по одному — в словаре BRANDS.
      3. Остаток первой строки после марки — кандидат на модель.
    """
    from scraper.translations import BRANDS  # локальный импорт, чтобы не было цикла

    # Нормализуем: неразрывный и полноширинный пробелы → обычный
    title_text = title_text.replace("\u00a0", " ").replace("\u3000", " ").strip()

    # Берём только первую строку — остальное описание комплектации
    first_line = title_text.split("\n")[0].strip()
    tokens = first_line.split()

    if not tokens:
        return None, None

    brand: str | None = None
    model_tokens_start: int = 1  # индекс первого токена модели

    # Сначала проверяем двусловную марку (напр. «アルファ ロメオ»)
    if len(tokens) >= 2:
        two_word_key = f"{tokens[0]} {tokens[1]}"
        if two_word_key in BRANDS:
            brand = BRANDS[two_word_key]
            model_tokens_start = 2

    # Если двусловная не нашлась — пробуем однословную
    if brand is None:
        brand = translate_brand(tokens[0])
        model_tokens_start = 1

    # Модель — следующий токен после марки (если не выглядит как объём/привод)
    model: str | None = None
    if len(tokens) > model_tokens_start:
        candidate = tokens[model_tokens_start]
        # Пропускаем токены вида «2.5», «4WD», «FF» — это не название модели
        if not re.match(r"^[\dF]", candidate):
            model = candidate

    return brand, model


async def _build_spec_dict(page: Page) -> dict[str, str]:
    """
    Собирает словарь {метка: значение} из таблицы характеристик страницы.

    carsensor.net использует разные структуры в зависимости от раздела:
    - dl > dt + dd  (основная таблица характеристик)
    - table > tr > th + td  (дополнительные блоки)
    Пробуем оба варианта и объединяем результаты.
    """
    spec: dict[str, str] = {}

    # ── Вариант 1: dl / dt / dd ───────────────────────────────────────────────
    # Итерируемся по каждому <dl>, чтобы правильно связать dt с dd
    # (простой zip всех dt и dd со страницы даёт неправильные пары)
    try:
        dl_elements = await page.query_selector_all("dl")
        for dl in dl_elements:
            dt_els = await dl.query_selector_all("dt")
            dd_els = await dl.query_selector_all("dd")
            for dt_el, dd_el in zip(dt_els, dd_els):
                label = (await dt_el.inner_text()).strip()
                value = (await dd_el.inner_text()).strip()
                if label and value:
                    spec[label] = value
    except Exception as exc:
        logger.debug("Ошибка при извлечении dl/dt/dd: %s", exc)

    # ── Вариант 2: table > tr > th + td ──────────────────────────────────────
    try:
        rows = await page.query_selector_all("table tr")
        for row in rows:
            ths = await row.query_selector_all("th")
            tds = await row.query_selector_all("td")
            for th, td in zip(ths, tds):
                label = (await th.inner_text()).strip()
                value = (await td.inner_text()).strip()
                if label and value:
                    spec.setdefault(label, value)  # dl/dt/dd приоритетнее
    except Exception as exc:
        logger.debug("Ошибка при извлечении table th/td: %s", exc)

    return spec


async def _extract_price(page: Page, spec: dict[str, str]) -> int | None:
    """
    Ищет цену на странице, перебирая несколько возможных селекторов и ключей таблицы.
    На carsensor.net цена обычно отображается как «258万円» в крупном элементе.
    """
    # Сначала пробуем таблицу характеристик
    for key in ("価格", "本体価格", "支払総額", "総額"):
        if key in spec:
            price = parse_price_jpy(spec[key])
            if price:
                return price

    # Затем — характерные CSS-классы и теги на странице
    price_selectors = [
        ".cs-price",
        "[class*='price']",
        "[class*='Price']",
        "[class*='kakaku']",
        "strong",
    ]
    for selector in price_selectors:
        try:
            elements = await page.query_selector_all(selector)
            for el in elements:
                text = (await el.inner_text()).strip()
                if "万" in text or "円" in text:
                    price = parse_price_jpy(text)
                    if price and price > 10_000:  # Отсеиваем случайные маленькие числа
                        return price
        except Exception:
            continue

    return None


async def _parse_detail_page(page: Page, url: str) -> CarData | None:
    """
    Открывает страницу конкретного автомобиля и извлекает все нужные поля.
    Возвращает None, если страница не загрузилась или выглядит некорректно.
    """
    try:
        # "load" вместо "domcontentloaded" — ждём выполнения JS-рендеринга таблицы характеристик
        await page.goto(url, wait_until="load", timeout=40_000)
        await page.wait_for_timeout(REQUEST_DELAY * 1000)
    except PlaywrightTimeoutError:
        logger.warning("Таймаут при загрузке страницы объявления: %s", url)
        return None

    car = CarData(source_url=url)

    # ── Марка и модель ────────────────────────────────────────────────────────
    title_text = await _safe_text(page, "h1") or await _safe_text(page, ".cs-carName") or ""
    if title_text:
        brand_raw, model_raw = _extract_brand_and_model(title_text)
        car.brand = brand_raw
        # Переводим модель через словарь; если не найдена — остаётся оригинал
        car.model = translate_model(model_raw) if model_raw else None

    # ── Таблица характеристик ─────────────────────────────────────────────────
    spec = await _build_spec_dict(page)
    logger.debug("Найдено пар в таблице характеристик: %d — %s", len(spec), list(spec.keys())[:8])

    # Год выпуска — пробуем несколько меток таблицы, затем ищем год в URL или заголовке
    year_raw = (
        spec.get("年式")
        or spec.get("初度登録年月")
        or spec.get("モデル年式")
        or ""
    )
    if not year_raw:
        # Запасной вариант: ищем 4-значный год прямо на странице (напр. «2023年式»)
        page_text = await _safe_text(page, "body") or ""
        year_match = re.search(r"(20\d{2}|19\d{2})[年\s]", page_text)
        year_raw = year_match.group(1) if year_match else ""
    car.year = parse_year(year_raw)

    # Пробег
    mileage_raw = spec.get("走行距離") or ""
    car.mileage = parse_mileage_km(mileage_raw)

    # Цвет кузова
    color_raw = spec.get("車体色") or spec.get("ボディカラー") or ""
    car.color = translate_color(color_raw) if color_raw else None

    # КПП
    trans_raw = spec.get("ミッション") or spec.get("トランスミッション") or ""
    car.transmission = translate_transmission(trans_raw) if trans_raw else None

    # Объём двигателя
    engine_raw = spec.get("排気量") or ""
    car.engine_volume = parse_engine_volume_litres(engine_raw)

    # Тип топлива (сайт использует разные метки в зависимости от раздела)
    fuel_raw = spec.get("燃料") or spec.get("使用燃料") or spec.get("燃料種別") or ""
    car.fuel_type = translate_fuel_type(fuel_raw) if fuel_raw else None

    # Тип кузова
    body_raw = spec.get("ボディタイプ") or spec.get("車体タイプ") or spec.get("ボディ") or ""
    car.body_type = translate_body_type(body_raw) if body_raw else None

    # Технический осмотр (車検) — нормализуем дату или статус
    inspection_raw = spec.get("車検") or spec.get("車検有効期限") or ""
    car.inspection_date = parse_inspection_date(inspection_raw)

    # ── Цена ─────────────────────────────────────────────────────────────────
    car.price = await _extract_price(page, spec)

    # ── Фотографии ────────────────────────────────────────────────────────────
    # ПРИМЕЧАНИЕ: Мы сохраняем оригинальные URL фото с carsensor.net.
    # В продакшене фото нужно скачивать и хранить в S3 (или аналоге),
    # потому что ссылки на carsensor.net со временем протухают.
    img_srcs = await page.eval_on_selector_all(
        "img[src]",
        "els => els.map(e => e.src)",
    )
    # Оставляем только URL, похожие на фото автомобиля — отсеиваем иконки и логотипы.
    # Исключаем маленькие превью с суффиксом _NNNs.JPG (например _001S.JPG) —
    # на carsensor.net такие URL ведут на низкокачественные миниатюры.
    photo_urls = [
        src for src in img_srcs
        if src
        and ("photo" in src.lower() or "CSphoto" in src or "/img/" in src.lower())
        and not src.endswith(".gif")
        and "logo" not in src.lower()
        and "icon" not in src.lower()
        and src.startswith("http")
        and not re.search(r"_\d+S\.(jpg|JPG)$", src)  # убираем маленькие превью (_001S.JPG)
    ]
    # Дедупликация, максимум 20 фото
    car.photos = list(dict.fromkeys(photo_urls))[:20]

    logger.info(
        "Автомобиль: %s %s | год=%s | пробег=%s | цена=%s | характеристик=%d",
        car.brand, car.model, car.year, car.mileage, car.price, len(spec),
    )
    return car


async def _make_browser(pw):
    """
    Запускает браузер с минимальным потреблением памяти.
    Вынесено в отдельную функцию — используется при старте и перезапуске.
    """
    browser = await pw.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            # Снижаем потребление памяти рендерером
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--single-process",
        ],
    )
    context = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        locale="ja-JP",
        viewport={"width": 1280, "height": 900},
    )
    return browser, context


async def scrape_new_cars_iter(urls_in_db: set[str]):
    """
    Генераторная версия: отдаёт CarData по одной сразу после парсинга.
    Воркер сохраняет каждую машину в БД немедленно, не дожидаясь конца запуска.

    Пагинация работает через клик «следующая страница», а не через URL-параметры,
    потому что carsensor.net игнорирует параметр pg= в search.php.

    Браузер перезапускается каждые BROWSER_RESTART_EVERY машин чтобы освободить
    накопленную Chromium-ом память и избежать OOM Kill на хостинге.
    """
    urls_scraped_this_run: set[str] = set()

    async with async_playwright() as pw:
        browser, context = await _make_browser(pw)
        found = 0

        # Сначала собираем ВСЕ URL листинга одним проходом (без парсинга деталей).
        # Для сбора URL нужен отдельный экземпляр браузера, который закроем после сбора,
        # чтобы освободить память перед началом парсинга деталей.
        listing_page = await context.new_page()
        all_listing_urls = await _collect_all_listing_urls(listing_page, MAX_LISTING_PAGES)
        await browser.close()
        logger.info("Сбор URL завершён, браузер закрыт. Начинаем парсинг деталей.")

        # Фильтруем: оставляем только новые URL
        urls_to_parse = [
            u for u in all_listing_urls
            if u not in urls_in_db and u not in urls_scraped_this_run
        ]
        logger.info("Новых машин для парсинга: %d", len(urls_to_parse))

        # Открываем свежий браузер для парсинга деталей
        browser, context = await _make_browser(pw)
        detail_page = await context.new_page()

        for idx, car_url in enumerate(urls_to_parse):
            # Перезапускаем браузер каждые BROWSER_RESTART_EVERY машин
            if idx > 0 and idx % BROWSER_RESTART_EVERY == 0:
                logger.info(
                    "Перезапуск браузера после %d машин (освобождаем память)...", idx
                )
                await browser.close()
                browser, context = await _make_browser(pw)
                detail_page = await context.new_page()

            car_data = await _parse_detail_page(detail_page, car_url)
            if car_data:
                urls_scraped_this_run.add(car_url)
                found += 1
                yield car_data

        await browser.close()
        logger.info("Генератор завершён. Всего найдено: %d.", found)
