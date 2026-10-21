import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  apiClient,
  apiClientWithHeaders,
  apiClientWithMeta,
  apiClientBlob,
  resolveApiUrl,
  generateRequestId,
  ApiError,
} from "./api-client";
import { AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";

describe("api-client and buildHeaders correlation tracing", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("resolves API URL with endpoint prefix", () => {
    const base = import.meta.env.VITE_API_BASE_URL || "";
    const prefix = import.meta.env.VITE_API_PREFIX || "/api/v1";
    expect(resolveApiUrl("/documents")).toBe(`${base}${prefix}/documents`);
    expect(resolveApiUrl("documents")).toBe(`${base}${prefix}/documents`);
  });

  it("automatically generates and attaches X-Request-ID header via crypto.randomUUID", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ success: true, data: { id: "test" }, meta: { request_id: "req-1", timestamp: "" } }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await apiClient<{ id: string }>("/test-endpoint");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const passedOptions = fetchMock.mock.calls[0][1] as RequestInit;
    const headers = passedOptions.headers as Headers;

    expect(headers.has("X-Request-ID")).toBe(true);
    const requestId = headers.get("X-Request-ID");
    expect(requestId).toBeDefined();
    // Valid UUID format (36 chars with dashes)
    expect(requestId).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i);
  });

  it("preserves explicitly passed X-Request-ID in options.headers", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ success: true, data: { id: "test" }, meta: { request_id: "custom-req-id", timestamp: "" } }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await apiClient<{ id: string }>("/test-endpoint", {
      headers: {
        "X-Request-ID": "custom-trace-uuid-12345",
      },
    });

    const passedOptions = fetchMock.mock.calls[0][1] as RequestInit;
    const headers = passedOptions.headers as Headers;
    expect(headers.get("X-Request-ID")).toBe("custom-trace-uuid-12345");
  });

  it("attaches Authorization header when token exists in localStorage", async () => {
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, "test-jwt-token-xyz");

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ success: true, data: "ok", meta: { request_id: "req-1", timestamp: "" } }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await apiClient<string>("/protected-resource");

    const passedOptions = fetchMock.mock.calls[0][1] as RequestInit;
    const headers = passedOptions.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer test-jwt-token-xyz");
  });

  it("throws ApiError with structured details on HTTP error", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      statusText: "Unauthorized",
      json: async () => ({
        success: false,
        error: {
          code: "INVALID_CREDENTIALS",
          message: "Email hoặc mật khẩu không chính xác.",
          field: "password",
        },
        meta: { request_id: "req-err", timestamp: "" },
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiClient("/auth/login")).rejects.toThrow(ApiError);

    try {
      await apiClient("/auth/login");
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      expect(apiErr.code).toBe("INVALID_CREDENTIALS");
      expect(apiErr.field).toBe("password");
      expect(apiErr.status).toBe(401);
    }
  });

  it("apiClientWithHeaders returns data, response headers, and ETag", async () => {
    const mockHeaders = new Headers({
      ETag: '"version-123"',
    });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: mockHeaders,
      json: async () => ({ success: true, data: { name: "Session A" }, meta: { request_id: "req-1", timestamp: "" } }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const res = await apiClientWithHeaders<{ name: string }>("/sessions/1");
    expect(res.data.name).toBe("Session A");
    expect(res.etag).toBe('"version-123"');
  });

  it("apiClientWithMeta returns paginated items and links", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: [{ id: "doc-1" }, { id: "doc-2" }],
        meta: { page: 1, per_page: 10, total: 2, total_pages: 1, request_id: "req-1", timestamp: "" },
        links: { first: "", prev: null, self: "", next: null, last: "" },
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const res = await apiClientWithMeta<{ id: string }>("/documents");
    expect(res.data).toHaveLength(2);
    expect(res.meta.total).toBe(2);
  });

  it("apiClientBlob returns blob response for binary files", async () => {
    const mockBlob = new Blob(["%PDF-1.4 test content"], { type: "application/pdf" });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      blob: async () => mockBlob,
    });
    vi.stubGlobal("fetch", fetchMock);

    const blob = await apiClientBlob("/documents/1/export");
    expect(blob.type).toBe("application/pdf");
  });

  it("generateRequestId returns custom ID if provided or generates valid UUID", () => {
    expect(generateRequestId("custom-id-999")).toBe("custom-id-999");
    const generated = generateRequestId();
    expect(generated).toBeDefined();
    expect(generated).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i);
  });
});
