import type { PDFDocumentProxy } from "pdfjs-dist";
import { pdfjsLib } from "./pdfjs-init";
import { useAuthStore, AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";

export const PDF_CACHE_NAME = "verischolar-pdfs-v1";

/**
 * Retrieve or download and cache PDF binary using the browser CacheStorage API.
 * Provides 0ms instant reload across browser sessions, tabs, and page reloads.
 */
export async function loadPdfBinaryWithCache(
  url: string,
  token?: string | null
): Promise<Uint8Array | null> {
  if (typeof window === "undefined" || !("caches" in window)) {
    return null;
  }

  // CacheStorage only supports http and https requests (skip blob:, data:, etc.)
  if (!url.startsWith("http://") && !url.startsWith("https://") && !url.startsWith("/")) {
    return null;
  }

  try {
    const cache = await window.caches.open(PDF_CACHE_NAME);
    const cachedResponse = await cache.match(url);
    if (cachedResponse) {
      const buffer = await cachedResponse.arrayBuffer();
      return new Uint8Array(buffer);
    }

    // First download: fetch binary from network and store in cache
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url, { headers });
    if (response.ok) {
      try {
        await cache.put(url, response.clone());
      } catch (cachePutErr) {
        console.warn("[CacheStorage] Failed storing PDF in cache:", cachePutErr);
      }
      const buffer = await response.arrayBuffer();
      return new Uint8Array(buffer);
    }
  } catch (err) {
    console.warn("[CacheStorage] Error in loadPdfBinaryWithCache:", err);
  }

  return null;
}

/**
 * In-memory document proxy cache to eliminate duplicate network transfers
 * and re-parsing across component mounts, re-renders, and document tab switches.
 */
const docCache = new Map<string, Promise<PDFDocumentProxy>>();

export function getCachedPdfDocument(url: string): Promise<PDFDocumentProxy> {
  const existing = docCache.get(url);
  if (existing) {
    return existing;
  }

  const storedToken =
    typeof window !== "undefined" ? localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) : null;
  const token = storedToken || useAuthStore.getState().token;

  const docPromise = (async () => {
    // 1. Try browser CacheStorage for 0ms instant reload
    const cachedBinary = await loadPdfBinaryWithCache(url, token);
    if (cachedBinary) {
      const loadingTask = pdfjsLib.getDocument({
        data: cachedBinary,
      });
      return await loadingTask.promise;
    }

    // 2. Direct network / streaming PDF.js loader fallback
    const loadingTask = pdfjsLib.getDocument({
      url,
      httpHeaders: token ? { Authorization: `Bearer ${token}` } : {},
      withCredentials: false,
    });
    return await loadingTask.promise;
  })();

  docCache.set(url, docPromise);

  // If loading fails, evict from cache so retry can succeed
  docPromise.catch(() => {
    docCache.delete(url);
  });

  return docPromise;
}

export function clearCachedPdfDocument(url: string): void {
  const existing = docCache.get(url);
  if (existing) {
    existing.then((doc) => {
      try {
        if ("destroy" in doc && typeof (doc as { destroy?: () => void }).destroy === "function") {
          (doc as { destroy: () => void }).destroy();
        }
      } catch {
        // ignore
      }
    }).catch(() => {});
    docCache.delete(url);
  }

  // Also purge from CacheStorage
  if (typeof window !== "undefined" && "caches" in window) {
    window.caches
      .open(PDF_CACHE_NAME)
      .then((cache) => cache.delete(url))
      .catch(() => {});
  }
}

/**
 * Concurrency-Limited Render Queue for PDF.js HTML5 Canvas Rendering.
 * Guarantees that at most MAX_CONCURRENT_RENDERS (2) canvases render simultaneously.
 * Prevents UI thread saturation while ensuring smooth page rendering.
 */
const MAX_CONCURRENT_RENDERS = 2;

interface QueuedRenderItem {
  id: string; // e.g. "docId-pageNumber-zoomRatio"
  priority: number; // lower number = higher priority
  execute: () => Promise<void>;
  cancelTask?: () => void;
  resolve: () => void;
  reject: (err: unknown) => void;
}

class PdfRenderQueue {
  private runningCount = 0;
  private queue: QueuedRenderItem[] = [];
  private activeItems = new Map<string, QueuedRenderItem>();

  /**
   * Enqueue a page canvas render task.
   */
  public enqueue(
    id: string,
    priority: number,
    renderFn: (setCancelHandler: (cancel: () => void) => void) => Promise<void>
  ): Promise<void> {
    // If a task for this id is already waiting in queue, update its priority
    const existing = this.queue.find((item) => item.id === id);
    if (existing) {
      existing.priority = priority;
      this.sortQueue();
      return new Promise<void>((res, rej) => {
        const origResolve = existing.resolve;
        const origReject = existing.reject;
        existing.resolve = () => {
          origResolve();
          res();
        };
        existing.reject = (e) => {
          origReject(e);
          rej(e);
        };
      });
    }

    return new Promise<void>((resolve, reject) => {
      const item: QueuedRenderItem = {
        id,
        priority,
        execute: async () => {
          await renderFn((cancelFn) => {
            item.cancelTask = cancelFn;
          });
        },
        resolve,
        reject,
      };

      this.queue.push(item);
      this.sortQueue();
      this.processNext();
    });
  }

  /**
   * Cancel an in-progress or queued render task for a given id.
   */
  public cancel(id: string): void {
    // 1. If in waiting queue, remove and reject with cancelled error
    const queueIdx = this.queue.findIndex((item) => item.id === id);
    if (queueIdx !== -1) {
      const [item] = this.queue.splice(queueIdx, 1);
      const cancelErr = new Error("RenderingCancelledException");
      cancelErr.name = "RenderingCancelledException";
      item.reject(cancelErr);
      return;
    }

    // 2. If actively executing, call the cancel callback
    const active = this.activeItems.get(id);
    if (active?.cancelTask) {
      try {
        active.cancelTask();
      } catch {
        // ignore
      }
    }
  }

  private sortQueue(): void {
    this.queue.sort((a, b) => a.priority - b.priority);
  }

  private async processNext(): Promise<void> {
    if (this.runningCount >= MAX_CONCURRENT_RENDERS || this.queue.length === 0) {
      return;
    }

    const item = this.queue.shift();
    if (!item) return;

    this.runningCount++;
    this.activeItems.set(item.id, item);

    try {
      await item.execute();
      item.resolve();
    } catch (err: unknown) {
      item.reject(err);
    } finally {
      this.activeItems.delete(item.id);
      this.runningCount--;
      this.processNext();
    }
  }
}

export const pdfRenderQueue = new PdfRenderQueue();

/**
 * Schedule low-priority work when browser is idle (used for TextLayer DOM injection)
 */
export function runWhenIdle(callback: () => void, timeoutMs = 150): () => void {
  if (typeof window !== "undefined" && "requestIdleCallback" in window) {
    const handle = (window as unknown as {
      requestIdleCallback: (cb: () => void, opts: { timeout: number }) => number;
      cancelIdleCallback: (h: number) => void;
    }).requestIdleCallback(callback, { timeout: timeoutMs });

    return () => {
      (window as unknown as { cancelIdleCallback: (h: number) => void }).cancelIdleCallback(handle);
    };
  }

  const timer = setTimeout(callback, 50);
  return () => clearTimeout(timer);
}
