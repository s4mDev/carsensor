from datetime import datetime
from pydantic import BaseModel


class CarBase(BaseModel):
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
    photos: list[str] = []
    source_url: str


class CarCreate(CarBase):
    pass


class CarResponse(CarBase):
    id: int
    scraped_at: datetime

    model_config = {"from_attributes": True}


class CarListResponse(BaseModel):
    items: list[CarResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
