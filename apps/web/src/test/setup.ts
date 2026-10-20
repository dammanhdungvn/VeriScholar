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

// Polyfill Map.prototype.getOrInsertComputed and getOrInsert
if (typeof Map !== "undefined" && typeof (Map.prototype as unknown as { getOrInsertComputed?: unknown }).getOrInsertComputed !== "function") {
  (Map.prototype as unknown as { getOrInsertComputed: (key: unknown, callback: (key: unknown) => unknown) => unknown }).getOrInsertComputed = function(this: Map<unknown, unknown>, key: unknown, callback: (key: unknown) => unknown) {
    if (this.has(key)) return this.get(key);
    const value = callback(key);
    this.set(key, value);
    return value;
  };
}
if (typeof Map !== "undefined" && typeof (Map.prototype as unknown as { getOrInsert?: unknown }).getOrInsert !== "function") {
  (Map.prototype as unknown as { getOrInsert: (key: unknown, defaultValue: unknown) => unknown }).getOrInsert = function(this: Map<unknown, unknown>, key: unknown, defaultValue: unknown) {
    if (this.has(key)) return this.get(key);
    this.set(key, defaultValue);
    return defaultValue;
  };
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

// Mock ResizeObserver for jsdom
if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

