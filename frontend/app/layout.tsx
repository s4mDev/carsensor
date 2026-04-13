import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";

const montserrat = Montserrat({
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-montserrat",
});

export const metadata: Metadata = {
  title: "CarSensor — Автомобили из Японии",
  description: "Каталог подержанных автомобилей с CarSensor.net",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className={`${montserrat.variable} font-[family-name:var(--font-montserrat)] min-h-screen bg-neutral-50 text-neutral-900`}>
        {children}
      </body>
    </html>
  );
}
