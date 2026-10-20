import { describe, it, expect, vi, beforeEach } from "vitest";
import { useAuthStore, AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";

const mockGetDocument = vi.fn();

vi.mock("./pdfjs-init", () => ({
  pdfjsLib: {
    getDocument: (...args: unknown[]) => mockGetDocument(...args),
  },
}));

import { getCachedPdfDocument, clearCachedPdfDocument } from "./pdfRenderQueue";

describe("getCachedPdfDocument", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("uses token from localStorage if available", async () => {
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, "test-local-token");
    useAuthStore.setState({ token: null });
    mockGetDocument.mockReturnValue({
      promise: Promise.resolve({ numPages: 5 }),
    });

    await getCachedPdfDocument("https://example.com/paper1.pdf");
    expect(mockGetDocument).toHaveBeenCalledWith(
      expect.objectContaining({
        url: "https://example.com/paper1.pdf",
        httpHeaders: { Authorization: "Bearer test-local-token" },
      })
    );
    clearCachedPdfDocument("https://example.com/paper1.pdf");
    localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
  });

  it("falls back to useAuthStore.getState().token if localStorage is empty", async () => {
    localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
    useAuthStore.setState({ token: "test-auth-store-token" });
    mockGetDocument.mockReturnValue({
      promise: Promise.resolve({ numPages: 3 }),
    });

    await getCachedPdfDocument("https://example.com/paper2.pdf");
    expect(mockGetDocument).toHaveBeenCalledWith(
      expect.objectContaining({
        url: "https://example.com/paper2.pdf",
        httpHeaders: { Authorization: "Bearer test-auth-store-token" },
      })
    );
    clearCachedPdfDocument("https://example.com/paper2.pdf");
    useAuthStore.setState({ token: null });
  });
});
