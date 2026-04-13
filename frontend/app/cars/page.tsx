"use client";

import { useEffect, useState, useCallback } from "react";
import Navbar from "@/components/Navbar";
import CarCard from "@/components/CarCard";
import CarFiltersPanel from "@/components/CarFilters";
import Pagination from "@/components/Pagination";
import { getCars } from "@/lib/api";
import type { Car, CarFilters, CarListResponse } from "@/lib/api";

const DEFAULT_FILTERS: CarFilters = {
  sort_by: "scraped_at",
  sort_order: "desc",
  page: 1,
  page_size: 20,
};

export default function CarsPage() {
  const [filters, setFilters] = useState<CarFilters>(DEFAULT_FILTERS);
  const [result, setResult] = useState<CarListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchCars = useCallback(async (currentFilters: CarFilters) => {
    setLoading(true);
    setError("");
    try {
      const data = await getCars(currentFilters);
      setResult(data);
    } catch {
      setError("Не удалось загрузить список автомобилей. Попробуйте ещё раз.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCars(filters);
  }, [filters, fetchCars]);

  function handleFiltersChange(newFilters: CarFilters) {
    setFilters(newFilters);
  }

  function handlePageChange(page: number) {
    setFilters((prev) => ({ ...prev, page }));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <Navbar />

      {/* Hero-заголовок */}
      <div className="bg-neutral-900 text-white py-10 px-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl font-bold mb-1">
            Автомобили{" "}
            <span style={{ color: "var(--gold)" }}>из Японии</span>
          </h1>
          <p className="text-neutral-400 text-sm mt-2">
            Актуальный каталог с CarSensor.net · обновляется каждый час
          </p>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-7">
          <CarFiltersPanel filters={filters} onFiltersChange={handleFiltersChange} />

          <div className="flex-1 min-w-0">
            {/* Счётчик результатов */}
            {result && !loading && (
              <div className="flex items-center justify-between mb-5">
                <span className="text-sm text-neutral-500">
                  Найдено:{" "}
                  <span className="font-semibold text-neutral-800">
                    {result.total.toLocaleString("ru-RU")}
                  </span>
                </span>
              </div>
            )}

            {/* Скелетон загрузки */}
            {loading && (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="bg-white rounded-3xl overflow-hidden shadow-sm animate-pulse">
                    <div className="aspect-video bg-neutral-200" />
                    <div className="p-5 space-y-3">
                      <div className="h-4 bg-neutral-200 rounded-full w-3/4" />
                      <div className="h-3 bg-neutral-200 rounded-full w-1/2" />
                      <div className="h-5 bg-neutral-200 rounded-full w-1/3 mt-4" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {error && (
              <div className="text-center py-16 text-red-500 text-sm">{error}</div>
            )}

            {!loading && !error && result?.items.length === 0 && (
              <div className="text-center py-20">
                <p className="text-neutral-400 text-sm">Автомобили по выбранным фильтрам не найдены.</p>
              </div>
            )}

            {!loading && !error && result && result.items.length > 0 && (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                  {result.items.map((car: Car) => (
                    <CarCard key={car.id} car={car} />
                  ))}
                </div>

                <Pagination
                  page={result.page}
                  totalPages={result.total_pages}
                  onPageChange={handlePageChange}
                />
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
