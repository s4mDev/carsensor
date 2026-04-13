import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_URL,
});

// Добавляем JWT-токен из localStorage в заголовок каждого запроса
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// При получении 401 — очищаем токен и редиректим на страницу входа
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      document.cookie = "token=; path=/; max-age=0";
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export interface Car {
  id: number;
  brand: string | null;
  model: string | null;
  year: number | null;
  mileage: number | null;
  price: number | null;
  transmission: string | null;
  body_type: string | null;
  color: string | null;
  engine_volume: number | null;
  fuel_type: string | null;
  inspection_date: string | null;
  photos: string[];
  source_url: string;
  scraped_at: string;
}

export interface CarListResponse {
  items: Car[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CarFilters {
  brand?: string;
  model?: string;
  year_min?: number;
  year_max?: number;
  price_min?: number;
  price_max?: number;
  mileage_max?: number;
  transmission?: string;
  body_type?: string;
  fuel_type?: string;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}

export async function getCars(filters: CarFilters = {}): Promise<CarListResponse> {
  // Убираем пустые значения, чтобы не передавать лишние параметры в URL
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== undefined && v !== "")
  );
  const response = await apiClient.get<CarListResponse>("/cars", { params });
  return response.data;
}

export async function getCarById(id: number): Promise<Car> {
  const response = await apiClient.get<Car>(`/cars/${id}`);
  return response.data;
}

export async function login(username: string, password: string): Promise<string> {
  const response = await apiClient.post<{ access_token: string }>("/auth/login", {
    username,
    password,
  });
  return response.data.access_token;
}
