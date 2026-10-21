import * as pdfjsLib from "pdfjs-dist";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import "pdfjs-dist/web/pdf_viewer.css";

// Configure worker URL with Promise.try and Uint8Array.prototype.toHex polyfill for worker thread
if (typeof window !== "undefined" && !pdfjsLib.GlobalWorkerOptions.workerSrc) {
  try {
    const fullWorkerUrl = new URL(pdfjsWorker, window.location.href).href;
    const workerBlob = new Blob(
      [
        `if (typeof Promise !== "undefined" && typeof Promise.try !== "function") {
  Promise.try = function(fn, ...args) {
    return new Promise(function(resolve) { resolve(fn(...args)); });
  };
}
if (typeof Map !== "undefined" && typeof Map.prototype.getOrInsertComputed !== "function") {
  Map.prototype.getOrInsertComputed = function(key, callback) {
    if (this.has(key)) return this.get(key);
    var val = callback(key);
    this.set(key, val);
    return val;
  };
}
if (typeof Map !== "undefined" && typeof Map.prototype.getOrInsert !== "function") {
  Map.prototype.getOrInsert = function(key, defaultValue) {
    if (this.has(key)) return this.get(key);
    this.set(key, defaultValue);
    return defaultValue;
  };
}
if (typeof Uint8Array !== "undefined" && typeof Uint8Array.prototype.toHex !== "function") {
  Uint8Array.prototype.toHex = function() {
    return Array.from(this).map(function(b) { return b.toString(16).padStart(2, "0"); }).join("");
  };
}
await import("${fullWorkerUrl}");`,
      ],
      { type: "text/javascript" }
    );
    pdfjsLib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(workerBlob);
  } catch {
    pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;
  }
}

// Polyfill Map.prototype.getOrInsertComputed for pdfjs-dist
if (
  typeof Map !== "undefined" &&
  typeof (Map.prototype as unknown as { getOrInsertComputed?: unknown }).getOrInsertComputed !== "function"
) {
  (
    Map.prototype as unknown as {
      getOrInsertComputed: (key: unknown, callback: (key: unknown) => unknown) => unknown;
    }
  ).getOrInsertComputed = function (this: Map<unknown, unknown>, key: unknown, callback: (key: unknown) => unknown) {
    if (this.has(key)) return this.get(key);
    const value = callback(key);
    this.set(key, value);
    return value;
  };
}

if (
  typeof Map !== "undefined" &&
  typeof (Map.prototype as unknown as { getOrInsert?: unknown }).getOrInsert !== "function"
) {
  (
    Map.prototype as unknown as {
      getOrInsert: (key: unknown, defaultValue: unknown) => unknown;
    }
  ).getOrInsert = function (this: Map<unknown, unknown>, key: unknown, defaultValue: unknown) {
    if (this.has(key)) return this.get(key);
    this.set(key, defaultValue);
    return defaultValue;
  };
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
// Polyfill Uint8Array.prototype.toHex for browser environments lacking Stage 3 proposal
if (
  typeof Uint8Array !== "undefined" &&
  typeof (Uint8Array.prototype as unknown as { toHex?: () => string }).toHex !== "function"
) {
  (Uint8Array.prototype as unknown as { toHex: () => string }).toHex = function (
    this: Uint8Array
  ): string {
    return Array.from(this)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  };
}

export { pdfjsLib };
