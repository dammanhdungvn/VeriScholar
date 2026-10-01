import type { SingleResponse, PaginatedResponse, ErrorResponse, PaginatedMeta, PaginationLinks } from "@/types/api";
import { AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_PREFIX = import.meta.env.VITE_API_PREFIX || "/api/v1";

export class ApiError extends Error {
  readonly code: string;
  readonly field?: string | null;
  readonly action?: string | null;
  readonly status: number;

  constructor(message: string, code: string, field?: string | null, action?: string | null, status = 400) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.field = field;
    this.action = action;
    this.status = status;
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

function buildHeaders(options: RequestInit = {}): Headers {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
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

  throw new ApiError(message, code, field, action, response.status);
}

/**
 * Base JSON fetcher with standard Envelope unwrapping and JWT injection
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = resolveApiUrl(endpoint);
  const headers = buildHeaders(options);

  const response = await fetch(url, {
    ...options,
    headers,
  });

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
