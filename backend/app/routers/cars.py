import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Car
from app.schemas import CarResponse, CarListResponse


router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("", response_model=CarListResponse)
def get_cars(
    brand: Optional[str] = Query(None, description="Фильтр по марке"),
    model: Optional[str] = Query(None, description="Фильтр по модели"),
    year_min: Optional[int] = Query(None, description="Год выпуска от"),
    year_max: Optional[int] = Query(None, description="Год выпуска до"),
    price_min: Optional[int] = Query(None, description="Цена от (иены)"),
    price_max: Optional[int] = Query(None, description="Цена до (иены)"),
    mileage_max: Optional[int] = Query(None, description="Максимальный пробег (км)"),
    transmission: Optional[str] = Query(None, description="Тип КПП"),
    body_type: Optional[str] = Query(None, description="Тип кузова"),
    fuel_type: Optional[str] = Query(None, description="Тип топлива"),
    sort_by: str = Query("scraped_at", description="Поле сортировки: price, year, mileage, scraped_at"),
    sort_order: str = Query("desc", description="Порядок сортировки: asc или desc"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db),
    _current_user: str = Depends(get_current_user),
):
    filters = []

    if brand:
        filters.append(Car.brand.ilike(f"%{brand}%"))
    if model:
        filters.append(Car.model.ilike(f"%{model}%"))
    if year_min is not None:
        filters.append(Car.year >= year_min)
    if year_max is not None:
        filters.append(Car.year <= year_max)
    if price_min is not None:
        filters.append(Car.price >= price_min)
    if price_max is not None:
        filters.append(Car.price <= price_max)
    if mileage_max is not None:
        filters.append(Car.mileage <= mileage_max)
    if transmission:
        filters.append(Car.transmission.ilike(f"%{transmission}%"))
    if body_type:
        filters.append(Car.body_type.ilike(f"%{body_type}%"))
    if fuel_type:
        filters.append(Car.fuel_type.ilike(f"%{fuel_type}%"))

    where_clause = and_(*filters) if filters else True

    total = db.execute(select(func.count()).select_from(Car).where(where_clause)).scalar()

    # Защита от произвольных имён полей в sort_by
    allowed_sort_fields = {"price", "year", "mileage", "scraped_at"}
    order_column = getattr(Car, sort_by if sort_by in allowed_sort_fields else "scraped_at")
    order_expr = order_column.desc() if sort_order == "desc" else order_column.asc()

    offset = (page - 1) * page_size
    cars = db.execute(
        select(Car).where(where_clause).order_by(order_expr).offset(offset).limit(page_size)
    ).scalars().all()

    return CarListResponse(
        items=cars,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{car_id}", response_model=CarResponse)
def get_car(
    car_id: int,
    db: Session = Depends(get_db),
    _current_user: str = Depends(get_current_user),
):
    car = db.get(Car, car_id)
    if car is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")
    return car
