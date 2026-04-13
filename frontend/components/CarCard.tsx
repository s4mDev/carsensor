import Link from "next/link";
import type { Car } from "@/lib/api";
import PriceBlock from "@/components/PriceBlock";

interface CarCardProps {
  car: Car;
}

function formatMileage(mileage: number | null): string {
  if (mileage === null) return "—";
  return `${mileage.toLocaleString("ru-RU")} км`;
}

export default function CarCard({ car }: CarCardProps) {
  const photoUrl = car.photos?.[0] || null;
  const title = [car.brand, car.model].filter(Boolean).join(" ") || "Неизвестный автомобиль";

  return (
    <Link href={`/cars/${car.id}`} className="group block">
      <div className="bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
        {/* Фото */}
        <div className="aspect-video bg-neutral-100 overflow-hidden">
          {photoUrl ? (
            // Используем <img> вместо next/image, чтобы не настраивать все домены CDN carsensor.net
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={photoUrl}
              alt={title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-neutral-400 text-sm">
              Фото отсутствует
            </div>
          )}
        </div>

        {/* Информация */}
        <div className="p-5">
          <h3 className="font-semibold text-base leading-tight mb-2 line-clamp-1">{title}</h3>

          <div className="flex flex-wrap gap-2 mb-3">
            {car.year && (
              <span className="text-xs bg-neutral-100 text-neutral-600 rounded-full px-2.5 py-1 font-medium">
                {car.year} г.
              </span>
            )}
            {car.mileage !== null && (
              <span className="text-xs bg-neutral-100 text-neutral-600 rounded-full px-2.5 py-1 font-medium">
                {formatMileage(car.mileage)}
              </span>
            )}
            {car.transmission && (
              <span className="text-xs bg-neutral-100 text-neutral-600 rounded-full px-2.5 py-1 font-medium">
                {car.transmission}
              </span>
            )}
          </div>

          <div className="flex items-end justify-between gap-2">
            {car.price ? (
              <PriceBlock priceJpy={car.price} layout="card" />
            ) : (
              <span className="text-neutral-400 text-sm">Цена не указана</span>
            )}
            {car.body_type && (
              <span
                className="text-xs rounded-xl px-2.5 py-1 font-semibold flex-shrink-0"
                style={{ backgroundColor: "#FDF8EE", color: "var(--gold)" }}
              >
                {car.body_type}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
