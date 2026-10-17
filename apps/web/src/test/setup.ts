import "@testing-library/jest-dom/vitest";

// Polyfill globalThis.Iterator for Node < 22 / non-supporting DOM test runners (pdfjs-dist requirement)
if (typeof (globalThis as unknown as { Iterator?: unknown }).Iterator === "undefined") {
  (globalThis as unknown as { Iterator: unknown }).Iterator = class Iterator {};
}
if (typeof global !== "undefined" && typeof (global as unknown as { Iterator?: unknown }).Iterator === "undefined") {
  (global as unknown as { Iterator: unknown }).Iterator = class Iterator {};
}
if (typeof window !== "undefined" && typeof (window as unknown as { Iterator?: unknown }).Iterator === "undefined") {
  (window as unknown as { Iterator: unknown }).Iterator = class Iterator {};
}

// Mock matchMedia for jsdom
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Mock scrollIntoView for jsdom
window.HTMLElement.prototype.scrollIntoView = function () {};

