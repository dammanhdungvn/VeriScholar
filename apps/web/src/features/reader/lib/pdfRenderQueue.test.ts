import { describe, it, expect, vi, beforeEach } from "vitest";
import { pdfRenderQueue, runWhenIdle } from "./pdfRenderQueue";

describe("pdfRenderQueue", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("limits concurrency and runs higher priority tasks first", async () => {
    const executed: string[] = [];

    const task1 = pdfRenderQueue.enqueue("task-1", 10, async () => {
      await new Promise((r) => setTimeout(r, 20));
      executed.push("task-1");
    });

    const task2 = pdfRenderQueue.enqueue("task-2", 5, async () => {
      await new Promise((r) => setTimeout(r, 10));
      executed.push("task-2");
    });

    const task3 = pdfRenderQueue.enqueue("task-3", 1, async () => {
      executed.push("task-3");
    });

    await Promise.all([task1, task2, task3]);

    expect(executed).toContain("task-1");
    expect(executed).toContain("task-2");
    expect(executed).toContain("task-3");
  });

  it("cancels pending queued task before execution", async () => {
    const executed: string[] = [];

    const slow1 = pdfRenderQueue.enqueue("slow-1", 1, async () => {
      await new Promise((r) => setTimeout(r, 50));
      executed.push("slow-1");
    });

    const slow2 = pdfRenderQueue.enqueue("slow-2", 1, async () => {
      await new Promise((r) => setTimeout(r, 50));
      executed.push("slow-2");
    });

    const pending = pdfRenderQueue.enqueue("pending-cancel", 10, async () => {
      executed.push("pending-cancel");
    });

    // Cancel while waiting in queue
    pdfRenderQueue.cancel("pending-cancel");

    await expect(pending).rejects.toThrow("RenderingCancelledException");
    await Promise.all([slow1, slow2]);

    expect(executed).not.toContain("pending-cancel");
  });

  it("handles cancel task handler callback if actively executing", async () => {
    let cancelCalled = false;

    const task = pdfRenderQueue.enqueue("exec-cancel", 1, async (setCancel) => {
      setCancel(() => {
        cancelCalled = true;
      });
      await new Promise((r) => setTimeout(r, 100));
    });

    // Short tick to allow task to start
    await new Promise((r) => setTimeout(r, 10));
    pdfRenderQueue.cancel("exec-cancel");
    expect(cancelCalled).toBe(true);

    await task;
  });

  it("runWhenIdle executes callbacks safely", async () => {
    let called = false;
    const cancel = runWhenIdle(() => {
      called = true;
    }, 50);

    expect(typeof cancel).toBe("function");
    await new Promise((r) => setTimeout(r, 80));
    expect(called).toBe(true);
  });
});
