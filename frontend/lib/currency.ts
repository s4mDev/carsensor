"use client";

export interface ExchangeRates {
  usd: number;  // 1 JPY → USD
  rub: number;  // 1 JPY → RUB
}

// Кэш курсов: не запрашиваем чаще одного раза в 30 минут
let cachedRates: ExchangeRates | null = null;
let cacheTime = 0;
const CACHE_TTL_MS = 30 * 60 * 1000;

export async function getExchangeRates(): Promise<ExchangeRates> {
  const now = Date.now();
  if (cachedRates && now - cacheTime < CACHE_TTL_MS) {
    return cachedRates;
  }

  try {
    // Используем бесплатный API без ключа (обновляется раз в сутки)
    const res = await fetch("https://open.er-api.com/v6/latest/JPY");
    const data = await res.json();

    if (data.result === "success") {
      cachedRates = {
        usd: data.rates["USD"],
        rub: data.rates["RUB"],
      };
      cacheTime = now;
      return cachedRates;
    }
  } catch {
    // Fallback-курсы на случай недоступности API
  }

  // Приблизительные резервные курсы (JPY → USD / RUB)
  return { usd: 0.0066, rub: 0.62 };
}

export function convertPrice(jpy: number, rates: ExchangeRates) {
  return {
    usd: Math.round(jpy * rates.usd),
    rub: Math.round(jpy * rates.rub),
  };
}

export function formatUsd(amount: number): string {
  return amount.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

export function formatRub(amount: number): string {
  return amount.toLocaleString("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 });
}
