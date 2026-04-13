"use client";

import { useEffect, useState } from "react";
import { getExchangeRates, convertPrice, formatUsd, formatRub, type ExchangeRates } from "@/lib/currency";

interface PriceBlockProps {
  priceJpy: number;
  layout?: "card" | "detail";
}

export default function PriceBlock({ priceJpy, layout = "detail" }: PriceBlockProps) {
  const [rates, setRates] = useState<ExchangeRates | null>(null);

  useEffect(() => {
    getExchangeRates().then(setRates);
  }, []);

  const jpy = `¥${(priceJpy / 10000).toFixed(1)} тыс.`;

  if (layout === "card") {
    return (
      <div>
        <div className="font-bold text-lg" style={{ color: "var(--gold)" }}>{jpy}</div>
        {rates && (() => {
          const { usd, rub } = convertPrice(priceJpy, rates);
          return (
            <div className="text-xs text-neutral-400 mt-0.5 space-x-1">
              <span>{formatUsd(usd)}</span>
              <span>·</span>
              <span>{formatRub(rub)}</span>
            </div>
          );
        })()}
      </div>
    );
  }

  const converted = rates ? convertPrice(priceJpy, rates) : null;

  return (
    <div>
      <div className="text-3xl font-bold" style={{ color: "var(--gold)" }}>{jpy}</div>
      {converted && (
        <div className="mt-1 flex gap-3 text-sm text-neutral-500">
          <span>{formatUsd(converted.usd)}</span>
          <span>·</span>
          <span>{formatRub(converted.rub)}</span>
        </div>
      )}
      {!converted && <div className="mt-1 text-xs text-neutral-400">Загрузка курсов...</div>}
      <div className="mt-1 text-xs text-neutral-400">Курс обновляется раз в 30 мин</div>
    </div>
  );
}
