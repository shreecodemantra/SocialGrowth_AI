import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

const ACCESS_TOKEN_KEY = "sga_access_token";
const REFRESH_TOKEN_KEY = "sga_refresh_token";

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

export const apiClient = axios.create({
  baseURL: "/api/v1",
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshInFlight: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) throw new Error("No refresh token available");

  const { data } = await axios.post("/api/v1/auth/refresh", { refresh_token: refreshToken });
  tokenStorage.setTokens(data.access_token, data.refresh_token);
  return data.access_token as string;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retried) {
      originalRequest._retried = true;
      try {
        refreshInFlight = refreshInFlight ?? refreshAccessToken();
        const newAccessToken = await refreshInFlight;
        refreshInFlight = null;
        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        refreshInFlight = null;
        tokenStorage.clear();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export function extractErrorMessage(error: unknown, fallback = "Something went wrong."): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.error?.message ?? error.response?.data?.detail?.error?.message;
    if (typeof detail === "string") return detail;
  }
  return fallback;
}
