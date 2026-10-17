import * as pdfjsLib from "pdfjs-dist";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import "pdfjs-dist/web/pdf_viewer.css";

// Configure worker URL with Uint8Array.prototype.toHex polyfill for worker thread
if (typeof window !== "undefined" && !pdfjsLib.GlobalWorkerOptions.workerSrc) {
  try {
    const fullWorkerUrl = new URL(pdfjsWorker, window.location.href).href;
    const workerBlob = new Blob(
      [
        `if (typeof Uint8Array !== "undefined" && typeof Uint8Array.prototype.toHex !== "function") {
  Uint8Array.prototype.toHex = function() {
    return Array.from(this).map(function(b) { return b.toString(16).padStart(2, "0"); }).join("");
  };
}
import("${fullWorkerUrl}");`,
      ],
      { type: "text/javascript" }
    );
    pdfjsLib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(workerBlob);
  } catch {
    pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;
  }
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
