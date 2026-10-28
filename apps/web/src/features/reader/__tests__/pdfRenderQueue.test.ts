import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  PDF_CACHE_NAME,
  loadPdfBinaryWithCache,
  clearCachedPdfDocument,
} from "../lib/pdfRenderQueue";

describe("pdfRenderQueue CacheStorage integration", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("verifies PDF_CACHE_NAME constant", () => {
    expect(PDF_CACHE_NAME).toBe("verischolar-pdfs-v1");
  });

  it("returns null when window.caches is not available", async () => {
    const originalCaches = (window as any).caches;
    delete (window as any).caches;

    const result = await loadPdfBinaryWithCache("https://example.com/test.pdf");
    expect(result).toBeNull();

    if (originalCaches) {
      (window as any).caches = originalCaches;
    }
  });

  it("loads and returns Uint8Array from CacheStorage when cached", async () => {
    const fakeData = new Uint8Array([1, 2, 3, 4]);
    const mockArrayBuffer = fakeData.buffer;

    const mockMatch = vi.fn().mockResolvedValue({
      arrayBuffer: () => Promise.resolve(mockArrayBuffer),
    });

    const mockCache = {
      match: mockMatch,
      put: vi.fn(),
      delete: vi.fn(),
    };

    (window as any).caches = {
      open: vi.fn().mockResolvedValue(mockCache),
    };

    const result = await loadPdfBinaryWithCache("https://example.com/test.pdf");
    expect((window as any).caches.open).toHaveBeenCalledWith("verischolar-pdfs-v1");
    expect(mockMatch).toHaveBeenCalledWith("https://example.com/test.pdf");
    expect(result).toBeInstanceOf(Uint8Array);
    expect(result?.length).toBe(4);

    delete (window as any).caches;
  });

  it("fetches and caches PDF binary on first download", async () => {
    const fakeData = new Uint8Array([5, 6, 7, 8]);
    const mockMatch = vi.fn().mockResolvedValue(null);
    const mockPut = vi.fn().mockResolvedValue(undefined);

    const mockCache = {
      match: mockMatch,
      put: mockPut,
      delete: vi.fn(),
    };

    (window as any).caches = {
      open: vi.fn().mockResolvedValue(mockCache),
    };

    const mockResponse = {
      ok: true,
      clone: () => mockResponse,
      arrayBuffer: () => Promise.resolve(fakeData.buffer),
    };

    globalThis.fetch = vi.fn().mockResolvedValue(mockResponse) as any;

    const result = await loadPdfBinaryWithCache("https://example.com/download.pdf", "test-token");
    expect(globalThis.fetch).toHaveBeenCalledWith("https://example.com/download.pdf", {
      headers: { Authorization: "Bearer test-token" },
    });
    expect(mockPut).toHaveBeenCalled();
    expect(result).toBeInstanceOf(Uint8Array);

    delete (window as any).caches;
  });

  it("deletes from CacheStorage upon clearCachedPdfDocument", async () => {
    const mockDelete = vi.fn().mockResolvedValue(true);
    const mockCache = {
      delete: mockDelete,
    };

    (window as any).caches = {
      open: vi.fn().mockResolvedValue(mockCache),
    };

    clearCachedPdfDocument("https://example.com/clear-test.pdf");
    expect((window as any).caches.open).toHaveBeenCalledWith("verischolar-pdfs-v1");

    delete (window as any).caches;
  });
});
