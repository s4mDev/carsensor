"""
Словари для перевода и нормализации данных с carsensor.net (японский → русский).

Ключи — строки точно в том виде, в каком они встречаются на сайте.
Значения — нормализованные русскоязычные эквиваленты, которые сохраняются в БД.
"""

import re

# ── Типы кузова ───────────────────────────────────────────────────────────────
BODY_TYPES: dict[str, str] = {
    "セダン": "Седан",
    "ハッチバック": "Хэтчбек",
    "コンパクト": "Компакт",
    "軽自動車": "Кей-кар",
    "軽ワゴン": "Кей-вэгон",
    "軽トラック": "Кей-грузовик",
    "軽バン": "Кей-фургон",
    "ミニバン": "Минивэн",
    "ワゴン": "Универсал",
    "SUV": "Внедорожник",
    "ＳＵＶ": "Внедорожник",
    "クロスカントリー": "Кроссовер",
    "クロカン": "Внедорожник",
    "クロカン・ＳＵＶ": "Внедорожник/SUV",
    "クーペ": "Купе",
    "オープン": "Кабриолет",
    "ピックアップトラック": "Пикап",
    "トラック": "Грузовик",
    "バン": "Фургон",
    "バス": "Автобус",
}

# ── Типы топлива ──────────────────────────────────────────────────────────────
FUEL_TYPES: dict[str, str] = {
    # Полные формы
    "ガソリン": "Бензин",
    "無鉛プレミアム": "Бензин (АИ-98)",
    "無鉛レギュラー": "Бензин (АИ-92)",
    "ハイオク": "Бензин (АИ-98)",
    "ディーゼル": "Дизель",
    "ハイブリッド": "Гибрид",
    "プラグインハイブリッド": "Подключаемый гибрид",
    "電気": "Электро",
    "電気自動車": "Электро",
    "LPG": "Газ (LPG)",
    "水素": "Водород",
    "その他": "Другое",
    # Краткие формы, которые реально встречаются на carsensor.net
    "レギュラー": "Бензин (АИ-92)",
    "プレミアム": "Бензин (АИ-98)",
    "軽油": "Дизель",
}

# ── Цвета ─────────────────────────────────────────────────────────────────────
COLORS: dict[str, str] = {
    "ホワイト": "Белый",
    "白": "Белый",
    "パールホワイト": "Белый перламутр",
    "ホワイトパール": "Белый перламутр",
    "クリムゾンレッド・パール": "Тёмно-красный перламутр",
    "ブラック": "Чёрный",
    "黒": "Чёрный",
    "シルバー": "Серебристый",
    "銀": "Серебристый",
    "レッド": "Красный",
    "赤": "Красный",
    "ブルー": "Синий",
    "青": "Синий",
    "ネイビー": "Тёмно-синий",
    "グレー": "Серый",
    "グレイ": "Серый",
    "灰": "Серый",
    "グリーン": "Зелёный",
    "緑": "Зелёный",
    "ゴールド": "Золотой",
    "金": "Золотой",
    "ブラウン": "Коричневый",
    "茶": "Коричневый",
    "ベージュ": "Бежевый",
    "オレンジ": "Оранжевый",
    "イエロー": "Жёлтый",
    "黄": "Жёлтый",
    "パープル": "Фиолетовый",
    "紫": "Фиолетовый",
    "ピンク": "Розовый",
    "その他": "Другое",
}

# ── Марки ─────────────────────────────────────────────────────────────────────
BRANDS: dict[str, str] = {
    "トヨタ": "Toyota",
    "ホンダ": "Honda",
    "日産": "Nissan",
    "スバル": "Subaru",
    "マツダ": "Mazda",
    "スズキ": "Suzuki",
    "三菱": "Mitsubishi",
    "ダイハツ": "Daihatsu",
    "レクサス": "Lexus",
    "いすゞ": "Isuzu",
    "日野": "Hino",
    "三菱ふそう": "Mitsubishi Fuso",
    "スマート": "Smart",
    # Иностранные марки в катакане
    "BMW": "BMW",
    "アルファロメオ": "Alfa Romeo",
    "アルファ ロメオ": "Alfa Romeo",    # На сайте пишут с пробелом
    "アルファ・ロメオ": "Alfa Romeo",
    "メルセデス・ベンツ": "Mercedes-Benz",
    "ベンツ": "Mercedes-Benz",
    "フォルクスワーゲン": "Volkswagen",
    "アウディ": "Audi",
    "ボルボ": "Volvo",
    "ポルシェ": "Porsche",
    "フェラーリ": "Ferrari",
    "ランボルギーニ": "Lamborghini",
    "マセラティ": "Maserati",
    "ジャガー": "Jaguar",
    "ランドローバー": "Land Rover",
    "フォード": "Ford",
    "シボレー": "Chevrolet",
    "ジープ": "Jeep",
    "クライスラー": "Chrysler",
    "キャデラック": "Cadillac",
    "テスラ": "Tesla",
    "ヒュンダイ": "Hyundai",
    "キア": "Kia",
    "プジョー": "Peugeot",
    "ルノー": "Renault",
    "アルファロメオ": "Alfa Romeo",
    "フィアット": "Fiat",
    "ミニ": "MINI",
    "ベントレー": "Bentley",
    "ロールスロイス": "Rolls-Royce",
    "アストンマーティン": "Aston Martin",
    "マクラーレン": "McLaren",
}

# ── Модели (японское название → латиница/транслит) ────────────────────────────
MODELS: dict[str, str] = {
    # Toyota
    "プリウス": "Prius",
    "クラウン": "Crown",
    "ハリアー": "Harrier",
    "アクア": "Aqua",
    "マークX": "Mark X",
    "アルファード": "Alphard",
    "ヴェルファイア": "Vellfire",
    "ヴォクシー": "Voxy",
    "ノア": "Noah",
    "カムリ": "Camry",
    "ランドクルーザー": "Land Cruiser",
    "ランクル": "Land Cruiser",
    "ヤリス": "Yaris",
    "ライズ": "Raize",
    "ルーミー": "Roomy",
    "シエンタ": "Sienta",
    "エスティマ": "Estima",
    "カローラ": "Corolla",
    "スープラ": "Supra",
    "86": "86",
    "GR86": "GR86",
    "C-HR": "C-HR",
    "RAV4": "RAV4",
    # Nissan
    "セレナ": "Serena",
    "エルグランド": "Elgrand",
    "スカイライン": "Skyline",
    "フーガ": "Fuga",
    "ティアナ": "Teana",
    "エクストレイル": "X-Trail",
    "ジューク": "Juke",
    "デイズ": "Dayz",
    "ノート": "Note",
    "リーフ": "Leaf",
    "GT-R": "GT-R",
    "フェアレディZ": "Fairlady Z",
    "キューブ": "Cube",
    "マーチ": "March",
    "NV200バネットバン": "NV200 Vanette Van",
    "NV200バネット": "NV200 Vanette",
    "キャラバン": "Caravan",
    # Honda
    "フィット": "Fit",
    "ヴェゼル": "Vezel",
    "フリード": "Freed",
    "ステップワゴン": "Stepwgn",
    "オデッセイ": "Odyssey",
    "CR-V": "CR-V",
    "バモス": "Vamos",
    "N-BOX": "N-BOX",
    "N-ONE": "N-ONE",
    "N-WGN": "N-WGN",
    "シビック": "Civic",
    "アコード": "Accord",
    "レジェンド": "Legend",
    "S660": "S660",
    "ZR-V": "ZR-V",
    # Mazda
    "アテンザ": "Atenza",
    "アクセラ": "Axela",
    "デミオ": "Demio",
    "CX-5": "CX-5",
    "CX-3": "CX-3",
    "CX-8": "CX-8",
    "CX-30": "CX-30",
    "ロードスター": "Roadster",
    "RX-7": "RX-7",
    "RX-8": "RX-8",
    "マツダ3": "Mazda3",
    "マツダ6": "Mazda6",
    # Subaru
    "レガシィB4": "Legacy B4",
    "レガシィ": "Legacy",
    "インプレッサ": "Impreza",
    "フォレスター": "Forester",
    "アウトバック": "Outback",
    "BRZ": "BRZ",
    "WRX": "WRX",
    "XV": "XV",
    "クロストレック": "Crosstrek",
    # Suzuki
    "ジムニー": "Jimny",
    "ジムニーシエラ": "Jimny Sierra",
    "スイフト": "Swift",
    "ソリオ": "Solio",
    "ハスラー": "Hustler",
    "エブリイ": "Every",
    "ワゴンR": "Wagon R",
    "アルト": "Alto",
    "スペーシア": "Spacia",
    "イグニス": "Ignis",
    "クロスビー": "Crossby",
    # Daihatsu
    "タント": "Tanto",
    "ムーヴ": "Move",
    "ミライース": "Mira e:S",
    "タフト": "Taft",
    "ロッキー": "Rocky",
    "コペン": "Copen",
    "ハイゼット": "Hijet",
    "キャスト": "Cast",
    # Mitsubishi
    "アウトランダー": "Outlander",
    "エクリプスクロス": "Eclipse Cross",
    "デリカ": "Delica",
    "パジェロ": "Pajero",
    "ランサー": "Lancer",
    "i-MiEV": "i-MiEV",
    # Smart
    "フォーフォー": "Forfour",
    "フォーツー": "Fortwo",
    # MINI (ミニ как модель — это сам MINI Cooper, без дубля бренда)
    "ミニ": "Cooper",
    "クーパー": "Cooper",
    "クーパーS": "Cooper S",
    "クーパーSE": "Cooper SE",
    "クロスオーバー": "Crossover",
    "クラブマン": "Clubman",
    "コンバーチブル": "Convertible",
    "ペースマン": "Paceman",
    "カントリーマン": "Countryman",
    # Alfa Romeo
    "ジュリア": "Giulia",
    "ジュリエッタ": "Giulietta",
    "ステルヴィオ": "Stelvio",
    "ミト": "MiTo",
    "スパイダー": "Spider",
    # Mitsubishi (дополнение)
    "eKワゴン": "eK Wagon",
    "eKクロス": "eK Cross",
    "eKスペース": "eK Space",
    "eKスポーツ": "eK Sport",
    # Subaru (дополнение)
    "レヴォーグ": "Levorg",
    "エクシーガ": "Exiga",
    "エクシーガクロスオーバー7": "Exiga Crossover 7",
    # Lexus
    "RX": "RX",
    "NX": "NX",
    "IS": "IS",
    "GS": "GS",
    "LS": "LS",
    "LX": "LX",
    "UX": "UX",
    "LC": "LC",
}

# Метки из таблицы характеристик на carsensor.net → названия полей нашей модели
SPEC_LABELS: dict[str, str] = {
    "年式": "year",
    "走行距離": "mileage",
    "車体色": "color",
    "ボディカラー": "color",
    "ミッション": "transmission",
    "トランスミッション": "transmission",
    "排気量": "engine_volume",
    "燃料": "fuel_type",
    "使用燃料": "fuel_type",
    "車検": "inspection_date",
    "ボディタイプ": "body_type",
    "車体タイプ": "body_type",
}

# ── Функции перевода ──────────────────────────────────────────────────────────

def translate_body_type(raw: str) -> str:
    raw = raw.strip()
    if raw in BODY_TYPES:
        return BODY_TYPES[raw]
    # Частичный матчинг: проверяем, содержит ли строка известный тип
    for jp, ru in BODY_TYPES.items():
        if jp in raw:
            return ru
    return raw


def translate_transmission(raw: str) -> str:
    """
    Переводит обозначение КПП.
    Примеры с сайта: 'フロア5MT', 'インパネCVT', 'フロアMTモード付6AT', 'コラムAT'
    """
    raw = raw.strip()
    raw_upper = raw.upper()

    # Точное совпадение по базовым кодам
    for code, name in [("CVT", "Вариатор"), ("DCT", "Двойное сцепление (DCT)"), ("AMT", "Роботизированная КПП")]:
        if code in raw_upper:
            return name

    # Ищем «цифра + AT» или «цифра + MT»
    speed_match = re.search(r"(\d+)\s*(AT|MT)", raw_upper)
    if speed_match:
        speeds = speed_match.group(1)
        kind = speed_match.group(2)
        suffix = f" {speeds} ст."
        if kind == "AT":
            manual_mode = "МТ-режим付" in raw or "MTモード" in raw
            return ("Автомат" + suffix + (" (ручной режим)" if manual_mode else ""))
        if kind == "MT":
            return "Механика" + suffix

    # Без числа
    if "AT" in raw_upper:
        return "Автомат"
    if "MT" in raw_upper:
        return "Механика"

    return raw


def translate_fuel_type(raw: str) -> str:
    raw = raw.strip()
    return FUEL_TYPES.get(raw, raw)


def translate_color(raw: str) -> str:
    raw = raw.strip()
    if raw in COLORS:
        return COLORS[raw]
    for jp, ru in COLORS.items():
        if jp in raw:
            return ru
    return raw


def translate_brand(raw: str) -> str:
    raw = raw.strip()
    return BRANDS.get(raw, raw)


def translate_model(raw: str) -> str:
    """Переводит/транслитерирует японское название модели."""
    raw = raw.strip()
    if raw in MODELS:
        return MODELS[raw]
    # Частичный матчинг — на случай если название содержит доп. символы
    for jp, en in MODELS.items():
        if jp in raw:
            return en
    return raw  # Если модель не в словаре — оставляем как есть


def parse_inspection_date(raw: str) -> str | None:
    """
    Нормализует дату техосмотра.

    Примеры:
      '2028(R10)年3月'              → 'мар. 2028 г.'
      '2027(R09)年5月'              → 'май 2027 г.'
      '車検残：無（購入時に新規取得）...'  → 'Без ТО (оформляется при покупке)'
      '車検整備付'                   → 'ТО включено'
    """
    if not raw:
        return None

    MONTHS_RU = ["янв.", "фев.", "мар.", "апр.", "май", "июн.",
                 "июл.", "авг.", "сен.", "окт.", "ноя.", "дек."]

    # «2028(R10)年3月» или «2028年3月»
    m = re.search(r"(\d{4})[（(（]?[Rr]?\d*[）)）]?[年]\s*(\d+)[月]", raw)
    if m:
        year = m.group(1)
        month_num = int(m.group(2))
        month_name = MONTHS_RU[month_num - 1] if 1 <= month_num <= 12 else str(month_num)
        return f"{month_name} {year} г."

    if "車検残：無" in raw or "車検なし" in raw or "新規取得" in raw:
        return "Без ТО (оформляется при покупке)"
    if "車検整備付" in raw:
        return "ТО включено"
    if "継続車検" in raw:
        return "ТО продлён"

    return raw  # Не удалось распознать — возвращаем оригинал


# ── Числовые парсеры ──────────────────────────────────────────────────────────

def parse_mileage_km(raw: str) -> int | None:
    """
    Преобразует строки вида «1.5万km», «25,000km», «---» в целое число (км).
    Возвращает None, если значение не удаётся распарсить.
    """
    raw = raw.strip().replace(",", "").replace("km", "").replace("Km", "").replace("KM", "")
    if "万" in raw:
        number_part = raw.replace("万", "").strip()
        try:
            return int(float(number_part) * 10_000)
        except ValueError:
            return None
    match = re.search(r"\d+", raw)
    if match:
        return int(match.group())
    return None


def parse_price_jpy(raw: str) -> int | None:
    """
    Преобразует строки вида «258万円», «2,580,000円», «---» в целое число (иены).
    Возвращает None, если значение не удаётся распарсить.
    """
    raw = raw.strip().replace(",", "").replace("円", "")
    if "万" in raw:
        number_part = raw.replace("万", "").strip()
        try:
            return int(float(number_part) * 10_000)
        except ValueError:
            return None
    match = re.search(r"\d+", raw)
    if match:
        return int(match.group())
    return None


def parse_year(raw: str) -> int | None:
    """
    Преобразует строки вида «2020年», «H31/2019年», «2019» в целый год.
    """
    match = re.search(r"(20\d{2}|19\d{2})", raw)
    if match:
        return int(match.group())
    return None


def parse_engine_volume_litres(raw: str) -> float | None:
    """
    Преобразует строки вида «1500cc», «2.0L» в объём в литрах (float).
    """
    raw = raw.strip().lower()
    if "cc" in raw:
        match = re.search(r"(\d+)", raw)
        if match:
            return round(int(match.group()) / 1000, 1)
    if "l" in raw:
        match = re.search(r"([\d.]+)", raw)
        if match:
            return float(match.group())
    return None
