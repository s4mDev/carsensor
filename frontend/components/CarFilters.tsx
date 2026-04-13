"use client";

import { useState } from "react";
import type { CarFilters } from "@/lib/api";

interface CarFiltersProps {
  filters: CarFilters;
  onFiltersChange: (filters: CarFilters) => void;
}

const TRANSMISSIONS = ["Автомат", "Механика", "Вариатор", "Роботизированная КПП", "Двойное сцепление (DCT)"];
const BODY_TYPES = [
  "Седан", "Хэтчбек", "Компакт", "Кей-кар", "Минивэн",
  "Универсал", "Внедорожник", "Кроссовер", "Купе", "Кабриолет", "Пикап",
];
const FUEL_TYPES = ["Бензин", "Дизель", "Гибрид", "Подключаемый гибрид", "Электро"];
const SORT_OPTIONS = [
  { value: "scraped_at", label: "Сначала новые" },
  { value: "price_asc", label: "Цена: по возрастанию" },
  { value: "price_desc", label: "Цена: по убыванию" },
  { value: "year_desc", label: "Год: новее" },
  { value: "mileage_asc", label: "Пробег: меньше" },
];

const inputClass =
  "w-full bg-neutral-50 border border-neutral-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-[#CFB87C] transition-colors";

const labelClass = "block text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-1.5";

export default function CarFiltersPanel({ filters, onFiltersChange }: CarFiltersProps) {
  const [isOpen, setIsOpen] = useState(false);

  function handleChange(key: keyof CarFilters, value: string | number | undefined) {
    onFiltersChange({ ...filters, [key]: value || undefined, page: 1 });
  }

  function handleSort(value: string) {
    const [sort_by, sort_order] = value.includes("_asc")
      ? [value.replace("_asc", ""), "asc"]
      : value.includes("_desc")
      ? [value.replace("_desc", ""), "desc"]
      : ["scraped_at", "desc"];
    onFiltersChange({ ...filters, sort_by, sort_order, page: 1 });
  }

  function getCurrentSortValue(): string {
    if (!filters.sort_by || filters.sort_by === "scraped_at") return "scraped_at";
    return `${filters.sort_by}_${filters.sort_order || "desc"}`;
  }

  function handleReset() {
    onFiltersChange({ page: 1, page_size: filters.page_size });
  }

  const filtersContent = (
    <div className="space-y-5">
      <div>
        <label className={labelClass}>Сортировка</label>
        <select value={getCurrentSortValue()} onChange={(e) => handleSort(e.target.value)} className={inputClass}>
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <div>
        <label className={labelClass}>Марка</label>
        <input
          type="text"
          placeholder="Например, Toyota"
          value={filters.brand || ""}
          onChange={(e) => handleChange("brand", e.target.value)}
          className={inputClass}
        />
      </div>

      <div>
        <label className={labelClass}>Модель</label>
        <input
          type="text"
          placeholder="Например, Prius"
          value={filters.model || ""}
          onChange={(e) => handleChange("model", e.target.value)}
          className={inputClass}
        />
      </div>

      <div>
        <label className={labelClass}>Год выпуска</label>
        <div className="flex gap-2">
          <input
            type="number"
            placeholder="От"
            min={1990}
            max={2030}
            value={filters.year_min || ""}
            onChange={(e) => handleChange("year_min", e.target.value ? parseInt(e.target.value) : undefined)}
            className={inputClass}
          />
          <input
            type="number"
            placeholder="До"
            min={1990}
            max={2030}
            value={filters.year_max || ""}
            onChange={(e) => handleChange("year_max", e.target.value ? parseInt(e.target.value) : undefined)}
            className={inputClass}
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>Цена (тыс. ¥)</label>
        <div className="flex gap-2">
          <input
            type="number"
            placeholder="От"
            value={filters.price_min ? filters.price_min / 10000 : ""}
            onChange={(e) => handleChange("price_min", e.target.value ? parseInt(e.target.value) * 10000 : undefined)}
            className={inputClass}
          />
          <input
            type="number"
            placeholder="До"
            value={filters.price_max ? filters.price_max / 10000 : ""}
            onChange={(e) => handleChange("price_max", e.target.value ? parseInt(e.target.value) * 10000 : undefined)}
            className={inputClass}
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>Пробег до (тыс. км)</label>
        <input
          type="number"
          placeholder="Например, 50"
          value={filters.mileage_max ? filters.mileage_max / 1000 : ""}
          onChange={(e) => handleChange("mileage_max", e.target.value ? parseInt(e.target.value) * 1000 : undefined)}
          className={inputClass}
        />
      </div>

      <div>
        <label className={labelClass}>КПП</label>
        <select
          value={filters.transmission || ""}
          onChange={(e) => handleChange("transmission", e.target.value)}
          className={inputClass}
        >
          <option value="">Любая</option>
          {TRANSMISSIONS.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      <div>
        <label className={labelClass}>Тип кузова</label>
        <select
          value={filters.body_type || ""}
          onChange={(e) => handleChange("body_type", e.target.value)}
          className={inputClass}
        >
          <option value="">Любой</option>
          {BODY_TYPES.map((b) => <option key={b} value={b}>{b}</option>)}
        </select>
      </div>

      <div>
        <label className={labelClass}>Тип топлива</label>
        <select
          value={filters.fuel_type || ""}
          onChange={(e) => handleChange("fuel_type", e.target.value)}
          className={inputClass}
        >
          <option value="">Любое</option>
          {FUEL_TYPES.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
      </div>

      <button
        onClick={handleReset}
        className="w-full rounded-xl py-2.5 text-sm font-semibold border border-neutral-200 text-neutral-500 hover:border-neutral-400 hover:text-neutral-700 transition-colors"
      >
        Сбросить фильтры
      </button>
    </div>
  );

  return (
    <>
      {/* Кнопка фильтров на мобильных */}
      <div className="lg:hidden mb-4">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full rounded-xl py-3 text-sm font-semibold transition-colors"
          style={
            isOpen
              ? { backgroundColor: "var(--gold)", color: "#111" }
              : { border: "1px solid #e5e5e5", color: "#404040" }
          }
        >
          {isOpen ? "Скрыть фильтры ↑" : "Фильтры ↓"}
        </button>
        {isOpen && <div className="mt-4 bg-white rounded-3xl p-5 shadow-sm">{filtersContent}</div>}
      </div>

      {/* Боковая панель на десктопе */}
      <aside className="hidden lg:block w-64 flex-shrink-0">
        <div className="bg-white rounded-3xl p-6 shadow-sm sticky top-24">
          <h2 className="font-bold text-sm uppercase tracking-wider text-neutral-400 mb-5">Фильтры</h2>
          {filtersContent}
        </div>
      </aside>
    </>
  );
}
