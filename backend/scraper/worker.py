"""
Воркер скрапера.

Запускается сразу при старте контейнера, затем повторяется каждый час
с помощью APScheduler. Каждый запуск собирает новые машины с carsensor.net
и сохраняет их в базу данных.
"""

import asyncio
import logging
import sys
import os
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.orm import Session

# Добавляем корневой каталог backend в sys.path, чтобы пакеты импортировались корректно
# при прямом запуске этого скрипта (python scraper/worker.py)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Car


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s  %(message)s",
)
logger = logging.getLogger("scraper.worker")

SCRAPE_INTERVAL_MINUTES = 60


def _get_known_urls(db: Session) -> set[str]:
    """Возвращает множество source_url всех машин, уже сохранённых в БД."""
    rows = db.query(Car.source_url).all()
    return {row[0] for row in rows}


def _save_cars(db: Session, cars) -> int:
    """Сохраняет список новых машин в БД. Возвращает количество реально добавленных записей."""
    saved = 0
    for car_data in cars:
        # Повторная проверка уникальности внутри сессии (защита от гонки)
        exists = db.query(Car).filter(Car.source_url == car_data.source_url).first()
        if exists:
            continue

        car = Car(
            brand=car_data.brand,
            model=car_data.model,
            year=car_data.year,
            mileage=car_data.mileage,
            price=car_data.price,
            transmission=car_data.transmission,
            body_type=car_data.body_type,
            color=car_data.color,
            engine_volume=car_data.engine_volume,
            fuel_type=car_data.fuel_type,
            inspection_date=car_data.inspection_date,
            photos=car_data.photos,
            source_url=car_data.source_url,
        )
        db.add(car)
        saved += 1

    db.commit()
    return saved


def run_scrape_job():
    """Основная задача: собирает новые машины и сохраняет каждую сразу в БД."""
    logger.info("Запуск задачи скрапинга...")
    db = SessionLocal()
    total_saved = 0
    try:
        known_urls = _get_known_urls(db)
        logger.info("Машин в БД: %d", len(known_urls))

        # Сохраняем каждую машину сразу, не дожидаясь конца полного прохода.
        # Так данные появляются во фронтенде по мере парсинга, а не в самом конце.
        async def scrape_and_save():
            nonlocal total_saved
            from scraper.parser import scrape_new_cars_iter
            async for car_data in scrape_new_cars_iter(known_urls):
                saved = _save_cars(db, [car_data])
                total_saved += saved

        asyncio.run(scrape_and_save())
        logger.info("Задача завершена. Добавлено новых машин: %d.", total_saved)
    except Exception as exc:
        logger.exception("Ошибка во время скрапинга: %s", exc)
    finally:
        db.close()


def wait_for_db(max_retries: int = 10, delay: int = 5):
    """Ожидает готовности базы данных перед стартом воркера."""
    from sqlalchemy import text
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Соединение с базой данных установлено.")
            return
        except Exception as exc:
            logger.warning("БД не готова (попытка %d/%d): %s", attempt, max_retries, exc)
            time.sleep(delay)
    raise RuntimeError("Не удалось подключиться к БД после нескольких попыток.")


if __name__ == "__main__":
    wait_for_db()

    # Создаём таблицы, если их ещё нет (API делает то же самое, но воркер может стартовать раньше)
    Base.metadata.create_all(bind=engine)

    # Первый запуск сразу — не ждём полный час
    run_scrape_job()

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_scrape_job,
        trigger="interval",
        minutes=SCRAPE_INTERVAL_MINUTES,
        id="scrape_carsensor",
    )
    logger.info("Планировщик запущен. Следующий запуск через %d минут.", SCRAPE_INTERVAL_MINUTES)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Воркер скрапера остановлен.")
