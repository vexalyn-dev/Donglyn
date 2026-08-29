// Donglyn API Client
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
    credentials: "include",
  });
  if (!response.ok) throw new Error(`API Error: ${response.status}`);
  return response.json() as Promise<T>;
}

export const api = {
  // Auth
  getMe: () => apiRequest<{ logged_in: boolean; user: any }>("/api/auth/me"),
  login: (d: any) => apiRequest<any>("/api/auth/login", { method: "POST", body: JSON.stringify(d) }),
  register: (d: any) => apiRequest<any>("/api/auth/register", { method: "POST", body: JSON.stringify(d) }),
  logout: () => apiRequest<any>("/api/auth/logout", { method: "POST" }),
  sendOtp: (d: any) => apiRequest<any>("/api/auth/send-otp", { method: "POST", body: JSON.stringify(d) }),
  verifyPhone: (d: any) => apiRequest<any>("/api/auth/verify-phone", { method: "POST", body: JSON.stringify(d) }),
  forgotPassword: (d: any) => apiRequest<any>("/api/auth/forgot-password", { method: "POST", body: JSON.stringify(d) }),
  resetPassword: (d: any) => apiRequest<any>("/api/auth/reset-password", { method: "POST", body: JSON.stringify(d) }),
  updateProfile: (d: any) => apiRequest<any>("/api/auth/update-profile", { method: "POST", body: JSON.stringify(d) }),
  uploadAvatar: (fd: FormData) =>
    fetch(`${BASE_URL}/api/auth/upload-avatar`, { method: "POST", body: fd, credentials: "include" }).then((r) => r.json()),

  // Home
  getHome: () => apiRequest<any>("/api/home"),
  getBanner: () => apiRequest<any>("/api/banner"),
  getSchedule: () => apiRequest<any>("/api/schedule"),
  getGenres: () => apiRequest<any>("/api/genres"),
  getTerbaru: () => apiRequest<any>("/api/terbaru"),
  loadMore: (url: string) => apiRequest<any>("/api/load-more", { method: "POST", body: JSON.stringify({ url }) }),

  // Search
  search: (q: string) => apiRequest<any>("/api/search", { method: "POST", body: JSON.stringify({ q }) }),

  // Detail
  getDetail: (url: string) => apiRequest<any>("/api/detail-data", { method: "POST", body: JSON.stringify({ url }) }),

  // Bookmarks
  getBookmarks: () => apiRequest<any>("/api/bookmarks"),
  addBookmark: (d: any) => apiRequest<any>("/api/bookmarks", { method: "POST", body: JSON.stringify(d) }),
  removeBookmark: (d: any) => apiRequest<any>("/api/bookmarks", { method: "DELETE", body: JSON.stringify(d) }),

  // History
  getHistory: () => apiRequest<any>("/api/history"),
  addHistory: (d: any) => apiRequest<any>("/api/history", { method: "POST", body: JSON.stringify(d) }),
  clearHistory: () => apiRequest<any>("/api/history", { method: "DELETE" }),
  deleteHistoryItem: (d: any) => apiRequest<any>("/api/history", { method: "DELETE", body: JSON.stringify(d) }),

  // Dev
  devLogin: (d: any) => apiRequest<any>("/api/dev/login", { method: "POST", body: JSON.stringify(d) }),
  devLogout: () => apiRequest<any>("/api/dev/logout", { method: "POST" }),
  devStats: () => apiRequest<any>("/api/dev/stats"),
  devClearCache: () => apiRequest<any>("/api/dev/clear-cache", { method: "POST" }),
  devRefreshScraper: () => apiRequest<any>("/api/dev/refresh-scraper", { method: "POST" }),
  devSyncAll: () => apiRequest<any>("/api/dev/sync-all", { method: "POST" }),
  devLogs: (p?: any) => apiRequest<any>(`/api/dev/logs${p ? `?limit=${p.limit}` : ""}`),
  devClearLogs: () => apiRequest<any>("/api/dev/logs/clear", { method: "POST" }),
  devUsers: () => apiRequest<any>("/api/dev/users"),
  devDeleteUser: (id: number) => apiRequest<any>(`/api/dev/users/${id}`, { method: "DELETE" }),

  // Genre
  getGenre: (slug: string) => apiRequest<any>(`/api/genre/${encodeURIComponent(slug)}`),
};
