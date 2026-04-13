"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { clearToken } from "@/lib/auth";

export default function Navbar() {
  const router = useRouter();

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  return (
    <header className="bg-neutral-900 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link
          href="/cars"
          className="text-xl font-bold tracking-wide"
          style={{ color: "var(--gold)" }}
        >
          CARSENSOR
        </Link>

        <nav className="flex items-center gap-6">
          <Link
            href="/cars"
            className="text-sm text-neutral-300 hover:text-white transition-colors font-medium"
          >
            Каталог
          </Link>
          <button
            onClick={handleLogout}
            className="text-sm font-semibold px-4 py-1.5 rounded-lg border transition-colors"
            style={{ borderColor: "var(--gold)", color: "var(--gold)" }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--gold)";
              (e.currentTarget as HTMLButtonElement).style.color = "#111";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
              (e.currentTarget as HTMLButtonElement).style.color = "var(--gold)";
            }}
          >
            Выйти
          </button>
        </nav>
      </div>
    </header>
  );
}
