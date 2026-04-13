"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import PriceBlock from "@/components/PriceBlock";
import { getCarById } from "@/lib/api";
import type { Car } from "@/lib/api";

function formatMileage(mileage: number | null): string {
  if (mileage === null) return "—";
  return `${mileage.toLocaleString("ru-RU")} км`;
}

interface SpecRowProps {
  label: string;
  value: string | number | null | undefined;
}

function SpecRow({ label, value }: SpecRowProps) {
  if (value === null || value === undefined || value === "") return null;
  return (
    <div className="flex py-3.5 border-b border-neutral-100 last:border-0">
      <span className="w-48 flex-shrink-0 text-sm text-neutral-400 font-medium">{label}</span>
      <span className="text-sm font-semibold text-neutral-800">{String(value)}</span>
    </div>
  );
}

export default function CarDetailPage() {
  const params = useParams();
  const router = useRouter();
  const carId = parseInt(params.id as string);

  const [car, setCar] = useState<Car | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activePhoto, setActivePhoto] = useState(0);

  useEffect(() => {
    async function loadCar() {
      try {
        const data = await getCarById(carId);
        setCar(data);
      } catch {
        setError("Автомобиль не найден.");
      } finally {
        setLoading(false);
      }
    }
    loadCar();
  }, [carId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8 animate-pulse space-y-4">
          <div className="h-72 bg-neutral-200 rounded-3xl" />
          <div className="h-6 bg-neutral-200 rounded-full w-1/2" />
          <div className="h-4 bg-neutral-200 rounded-full w-1/4" />
        </div>
      </div>
    );
  }

  if (error || !car) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Navbar />
        <div className="text-center py-24 text-neutral-500">
          <p className="mb-4">{error || "Автомобиль не найден."}</p>
          <Link
            href="/cars"
            className="text-sm font-semibold px-5 py-2 rounded-xl"
            style={{ backgroundColor: "var(--gold)", color: "#111" }}
          >
            Вернуться к каталогу
          </Link>
        </div>
      </div>
    );
  }

  const title = [car.brand, car.model].filter(Boolean).join(" ") || "Неизвестный автомобиль";
  const photos = car.photos || [];

  return (
    <div className="min-h-screen bg-neutral-50">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Хлебные крошки */}
        <nav className="text-sm text-neutral-400 mb-5 flex items-center gap-2">
          <Link href="/cars" className="hover:text-neutral-700 transition-colors font-medium">
            Каталог
          </Link>
          <span>/</span>
          <span className="text-neutral-700 font-medium truncate">{title}</span>
        </nav>

        <div className="bg-white rounded-3xl shadow-sm overflow-hidden">
          {/* Галерея фотографий */}
          {photos.length > 0 ? (
            <div>
              {/* Главное фото */}
              <div className="aspect-video bg-neutral-100 overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={photos[activePhoto]}
                  alt={`${title} — фото ${activePhoto + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Миниатюры */}
              {photos.length > 1 && (
                <div className="flex gap-2 p-3 overflow-x-auto bg-neutral-50">
                  {photos.map((src, i) => (
                    <button
                      key={i}
                      onClick={() => setActivePhoto(i)}
                      className="flex-shrink-0 w-16 h-12 rounded-xl overflow-hidden border-2 transition-all"
                      style={{
                        borderColor: i === activePhoto ? "var(--gold)" : "transparent",
                        opacity: i === activePhoto ? 1 : 0.65,
                      }}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={src} alt="" className="w-full h-full object-cover" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="aspect-video bg-neutral-100 flex items-center justify-center text-neutral-400 text-sm">
              Фотографии отсутствуют
            </div>
          )}

          {/* Данные автомобиля */}
          <div className="p-6 sm:p-8">
            {/* Заголовок и цена */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
              <div>
                <h1 className="text-2xl font-bold text-neutral-900">{title}</h1>
                {car.body_type && (
                  <span
                    className="inline-block mt-2 text-xs rounded-xl px-3 py-1 font-semibold"
                    style={{ backgroundColor: "#FDF8EE", color: "var(--gold)" }}
                  >
                    {car.body_type}
                  </span>
                )}
              </div>
              <div className="sm:text-right flex-shrink-0">
                {car.price ? (
                  <PriceBlock priceJpy={car.price} layout="detail" />
                ) : (
                  <span className="text-neutral-400 text-sm">Цена не указана</span>
                )}
              </div>
            </div>

            {/* Таблица характеристик */}
            <div className="divide-y divide-neutral-100">
              <SpecRow label="Марка" value={car.brand} />
              <SpecRow label="Модель" value={car.model} />
              <SpecRow label="Год выпуска" value={car.year ? `${car.year} г.` : null} />
              <SpecRow label="Пробег" value={formatMileage(car.mileage)} />
              <SpecRow label="КПП" value={car.transmission} />
              <SpecRow label="Тип кузова" value={car.body_type} />
              <SpecRow label="Цвет" value={car.color} />
              <SpecRow label="Объём двигателя" value={car.engine_volume ? `${car.engine_volume} л` : null} />
              <SpecRow label="Тип топлива" value={car.fuel_type} />
              <SpecRow label="Технический осмотр" value={car.inspection_date} />
            </div>

            {/* Ссылка на оригинал и кнопка назад */}
            <div className="mt-8 pt-6 border-t border-neutral-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <a
                href={car.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-semibold px-5 py-2.5 rounded-xl transition-opacity hover:opacity-80"
                style={{ backgroundColor: "var(--gold)", color: "#111" }}
              >
                Смотреть на CarSensor.net →
              </a>

              <button
                onClick={() => router.back()}
                className="text-sm text-neutral-400 hover:text-neutral-700 transition-colors font-medium"
              >
                ← Назад к каталогу
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
