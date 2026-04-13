"use client";

export function saveToken(token: string) {
  localStorage.setItem("token", token);
  // Также сохраняем в cookie, чтобы middleware Next.js мог его прочитать на сервере
  document.cookie = `token=${token}; path=/; max-age=${60 * 60 * 24}; SameSite=Lax`;
}

export function clearToken() {
  localStorage.removeItem("token");
  document.cookie = "token=; path=/; max-age=0";
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function isLoggedIn(): boolean {
  return !!getToken();
}
