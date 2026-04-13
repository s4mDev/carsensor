from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    brand: Mapped[str | None] = mapped_column(String, index=True)
    model: Mapped[str | None] = mapped_column(String, index=True)
    year: Mapped[int | None] = mapped_column(Integer, index=True)
    mileage: Mapped[int | None] = mapped_column(Integer)        # км
    price: Mapped[int | None] = mapped_column(Integer, index=True)  # иены (JPY)
    transmission: Mapped[str | None] = mapped_column(String)
    body_type: Mapped[str | None] = mapped_column(String, index=True)
    color: Mapped[str | None] = mapped_column(String)
    engine_volume: Mapped[float | None] = mapped_column(Float)  # литры
    fuel_type: Mapped[str | None] = mapped_column(String)
    inspection_date: Mapped[str | None] = mapped_column(String)
    # ПРИМЕЧАНИЕ: В идеале фото нужно скачивать и хранить в S3 (или аналогичном объектном хранилище).
    # Пока сохраняем оригинальные URL с carsensor.net — они могут протухнуть со временем.
    photos: Mapped[list | None] = mapped_column(JSON, default=list)
    source_url: Mapped[str] = mapped_column(String, unique=True, index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
