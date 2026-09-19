import type { SingleResponse, ErrorResponse } from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_PREFIX = import.meta.env.VITE_API_PREFIX || "/api/v1";

export class ApiError extends Error {
  readonly code: string;
  readonly field?: string | null;
  readonly action?: string | null;

  constructor(message: string, code: string, field?: string | null, action?: string | null) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.field = field;
    this.action = action;
  }
}

/**
 * Base JSON fetcher with standard Envelope unwrapping
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${API_PREFIX}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
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

    throw new ApiError(message, code, field, action);
  }

  const json = (await response.json()) as SingleResponse<T>;
  return json.data;
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
