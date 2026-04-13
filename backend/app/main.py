from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, cars


# Создаём все таблицы при старте приложения
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CarSensor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить доменом фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cars.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
