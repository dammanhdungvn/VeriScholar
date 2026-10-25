import type { SingleResponse, PaginatedResponse, ErrorResponse, PaginatedMeta, PaginationLinks } from "@/types/api";
import {
  AUTH_TOKEN_STORAGE_KEY,
  AUTH_REFRESH_TOKEN_STORAGE_KEY,
  useAuthStore,
} from "@/features/auth/stores/useAuthStore";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
const API_PREFIX = import.meta.env.VITE_API_PREFIX || "/api/v1";

let isRefreshing = false;
let refreshSubscribers: Array<{
  resolve: (newToken: string) => void;
  reject: (err: unknown) => void;
}> = [];

function notifyRefreshSubscribers(newToken: string): void {
  const queue = refreshSubscribers;
  refreshSubscribers = [];
  for (const sub of queue) {
    sub.resolve(newToken);
  }
}

function rejectRefreshSubscribers(err: unknown): void {
  const queue = refreshSubscribers;
  refreshSubscribers = [];
  for (const sub of queue) {
    sub.reject(err);
  }
}

function isPublicAuthEndpoint(endpoint: string): boolean {
  const clean = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return (
    clean.startsWith("/auth/login") ||
    clean.startsWith("/auth/register") ||
    clean.startsWith("/auth/refresh") ||
    clean.startsWith("/auth/forgot-password") ||
    clean.startsWith("/auth/reset-password") ||
    clean.startsWith("/auth/verify-email")
  );
}

/**
 * Single-flight token refresh queue: ensures concurrent 401 responses trigger
 * only a single POST /api/v1/auth/refresh request and distribute the new token
 * to all waiting callers.
 */
export async function refreshAccessTokenQueued(): Promise<string | null> {
  let refreshToken: string | null = null;
  try {
    refreshToken =
      (typeof window !== "undefined"
        ? localStorage.getItem(AUTH_REFRESH_TOKEN_STORAGE_KEY)
        : null) || useAuthStore.getState().refreshToken;
  } catch {
    refreshToken = useAuthStore.getState().refreshToken;
  }

  if (!refreshToken) {
    return null;
  }

  if (isRefreshing) {
    return new Promise<string>((resolve, reject) => {
      refreshSubscribers.push({ resolve, reject });
    });
  }

  isRefreshing = true;
  try {
    const refreshUrl = resolveApiUrl("/auth/refresh");
    const res = await fetch(refreshUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Request-ID": generateRequestId(),
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) {
      throw new Error(`Refresh failed with status ${res.status}`);
    }

    const body = (await res.json()) as SingleResponse<{
      access_token?: string;
      refresh_token?: string;
      tokens?: { access_token: string; refresh_token?: string };
    }>;
    const payload = body?.data;
    const newAccessToken = payload?.access_token || payload?.tokens?.access_token;
    const newRefreshToken = payload?.refresh_token || payload?.tokens?.refresh_token;

    if (!newAccessToken) {
      throw new Error("Missing access_token in refresh response");
    }

    try {
      localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, newAccessToken);
      if (newRefreshToken) {
        localStorage.setItem(AUTH_REFRESH_TOKEN_STORAGE_KEY, newRefreshToken);
      }
    } catch {
      // Ignore storage write issues
    }

    const currentUser = useAuthStore.getState().user;
    if (currentUser) {
      useAuthStore.getState().setAuth(currentUser, newAccessToken, newRefreshToken);
    }

    notifyRefreshSubscribers(newAccessToken);
    return newAccessToken;
  } catch (err) {
    rejectRefreshSubscribers(err);
    useAuthStore.getState().clearAuth();
    return null;
  } finally {
    isRefreshing = false;
  }
}

async function fetchWithAuthRetry(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const url = resolveApiUrl(endpoint);
  const headers = buildHeaders(options);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401 && !isPublicAuthEndpoint(endpoint)) {
    const newToken = await refreshAccessTokenQueued().catch(() => null);
    if (newToken) {
      const retryHeaders = new Headers(headers);
      retryHeaders.set("Authorization", `Bearer ${newToken}`);
      return fetch(url, {
        ...options,
        headers: retryHeaders,
      });
    }
  }

  return response;
}

export class ApiError extends Error {
  readonly code: string;
  readonly field?: string | null;
  readonly action?: string | null;
  readonly status: number;
  readonly requestId?: string | null;
  readonly traceId?: string | null;

  constructor(
    message: string,
    code: string,
    field?: string | null,
    action?: string | null,
    status = 400,
    requestId?: string | null,
    traceId?: string | null
  ) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.field = field;
    this.action = action;
    this.status = status;
    this.requestId = requestId;
    this.traceId = traceId;
  }
}

export interface ApiResponseWithHeaders<T> {
  data: T;
  headers: Headers;
  etag: string | null;
}

export interface ApiPaginatedResult<T> {
  data: T[];
  meta: PaginatedMeta;
  links: PaginationLinks;
}

export function resolveApiUrl(endpoint: string): string {
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${API_PREFIX}${cleanEndpoint}`;
}

export function generateRequestId(customId?: string): string {
  if (customId) return customId;
  return typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

function buildHeaders(options: RequestInit = {}): Headers {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (!headers.has("X-Request-ID")) {
    headers.set("X-Request-ID", generateRequestId());
  }

  if (typeof window !== "undefined") {
    try {
      const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
      if (token && !headers.has("Authorization")) {
        headers.set("Authorization", `Bearer ${token}`);
      }
    } catch {
      // Ignore localStorage access issues
    }
  }

  return headers;
}


async function handleResponseError(response: Response): Promise<never> {
  let errorDetail: ErrorResponse | null = null;
  try {
    errorDetail = (await response.json()) as ErrorResponse;
  } catch {
    // Non-JSON response
  }

  const code = errorDetail?.error?.code || `HTTP_${response.status}`;
  const message = errorDetail?.error?.message || response.statusText || "Request failed";
  const field = errorDetail?.error?.field;
  const action = errorDetail?.error?.action;
  const requestId =
    errorDetail?.meta?.request_id ||
    response.headers.get("x-request-id") ||
    response.headers.get("X-Request-ID");
  const traceId = errorDetail?.meta?.trace_id;

  throw new ApiError(message, code, field, action, response.status, requestId, traceId);
}

/**
 * Base JSON fetcher with standard Envelope unwrapping and JWT injection
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetchWithAuthRetry(endpoint, options);

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    await handleResponseError(response);
  }

  const json = (await response.json()) as SingleResponse<T>;
  return json.data;
}

/**
 * Fetcher returning data, response headers, and ETag for OCC operations
 */
export async function apiClientWithHeaders<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponseWithHeaders<T>> {
  const url = resolveApiUrl(endpoint);
  const headers = buildHeaders(options);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return {
      data: undefined as T,
      headers: response.headers,
      etag: response.headers.get("ETag"),
    };
  }

  if (!response.ok) {
    await handleResponseError(response);
  }

  const json = (await response.json()) as SingleResponse<T>;
  return {
    data: json.data,
    headers: response.headers,
    etag: response.headers.get("ETag"),
  };
}

/**
 * Paginated collection fetcher returning items and RFC 8288 metadata
 */
export async function apiClientWithMeta<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiPaginatedResult<T>> {
  const url = resolveApiUrl(endpoint);
  const headers = buildHeaders(options);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  const json = (await response.json()) as PaginatedResponse<T>;
  return {
    data: json.data,
    meta: json.meta,
    links: json.links,
  };
}

/**
 * Binary blob fetcher (PDF streams, partial content, export bundles)
 */
export async function apiClientBlob(
  endpoint: string,
  options: RequestInit = {}
): Promise<Blob> {
  const url = resolveApiUrl(endpoint);
  const headers = buildHeaders(options);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.blob();
}

export interface UploadDocumentResponse {
  id: string;
  filename: string;
  [key: string]: unknown;
}

/**
 * Upload Document Helper (Multipart/form-data)
 */
export async function uploadDocumentApi(file: File, sessionId?: string): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  return apiClient<UploadDocumentResponse>("/documents", {
    method: "POST",
    body: formData,
  });
}
