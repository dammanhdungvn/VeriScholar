import type { PDFDocumentProxy } from "pdfjs-dist";
import { pdfjsLib } from "./pdfjs-init";

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

  const token = typeof window !== "undefined" ? localStorage.getItem("verischolar_auth_token") : null;
  const loadingTask = pdfjsLib.getDocument({
    url,
    httpHeaders: token ? { Authorization: `Bearer ${token}` } : {},
    withCredentials: false,
  });

  const promise = loadingTask.promise;
  docCache.set(url, promise);

  // If loading fails, evict from cache so retry can succeed
  promise.catch(() => {
    docCache.delete(url);
  });

  return promise;
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
}

/**
 * Concurrency-Limited Render Queue for PDF.js HTML5 Canvas Rendering.
 * Guarantees that at most MAX_CONCURRENT_RENDERS (2) canvases render simultaneously.
 * Prevents UI thread saturation and eliminates scroll jank/stuttering.
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
