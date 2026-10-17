import "@testing-library/jest-dom/vitest";

// Polyfill globalThis.Iterator for environments lacking Iterator (pdfjs-dist requirement)
if (typeof (globalThis as unknown as { Iterator?: unknown }).Iterator === "undefined") {
  (globalThis as unknown as { Iterator: unknown }).Iterator = class Iterator {};
}
if (typeof window !== "undefined" && typeof (window as unknown as { Iterator?: unknown }).Iterator === "undefined") {
  (window as unknown as { Iterator: unknown }).Iterator = class Iterator {};
}

// Polyfill Promise.try for environments lacking ECMAScript Promise.try (pdfjs-dist requirement)
if (typeof (Promise as unknown as { try?: unknown }).try !== "function") {
  (Promise as unknown as { try: (fn: (...args: unknown[]) => unknown, ...args: unknown[]) => Promise<unknown> }).try = function (fn, ...args) {
    return new Promise((resolve) => resolve(fn(...args)));
  };
}
if (typeof window !== "undefined" && typeof (window as unknown as { Promise?: { try?: unknown } }).Promise?.try !== "function") {
  (window as unknown as { Promise: { try: unknown } }).Promise.try = (Promise as unknown as { try: unknown }).try;
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

