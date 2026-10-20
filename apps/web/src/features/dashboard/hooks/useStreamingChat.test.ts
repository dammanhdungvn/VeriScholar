import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useStreamingChat } from "./useStreamingChat";
import * as fetchEventSourceModule from "@microsoft/fetch-event-source";

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn(),
}));

describe("useStreamingChat hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("initializes with idle state (isGenerating: false, empty messages)", () => {
    const { result } = renderHook(() => useStreamingChat({ activeSessionId: "s1" }));

    expect(result.current.isGenerating).toBe(false);
    expect(result.current.messages).toEqual([]);
    expect(result.current.inputText).toBe("");
  });

  it("stopGeneration resets isGenerating to false and marks messages is_streaming: false", async () => {
    // Mock fetchEventSource to stay open until aborted
    vi.mocked(fetchEventSourceModule.fetchEventSource).mockImplementation(
      (_url, options) => {
        return new Promise((_resolve, reject) => {
          options.signal?.addEventListener("abort", () => {
            reject(new Error("Aborted"));
          });
        });
      }
    );

    const { result } = renderHook(() => useStreamingChat({ activeSessionId: "s1" }));

    act(() => {
      result.current.setInputText("Hello Socratic");
    });

    // Start generation
    await act(async () => {
      void result.current.sendMessage();
      await Promise.resolve();
    });

    expect(result.current.isGenerating).toBe(true);
    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[1].is_streaming).toBe(true);

    // Call stopGeneration
    act(() => {
      result.current.stopGeneration();
    });

    expect(result.current.isGenerating).toBe(false);
    expect(result.current.messages[1].is_streaming).toBe(false);
  });

  it("try/finally ensures isGenerating is always false after stream finishes normally", async () => {
    vi.mocked(fetchEventSourceModule.fetchEventSource).mockImplementation(
      async (_url, options) => {
        // Simulate message with token and then done
        options.onmessage?.({
          id: "1",
          event: "message",
          data: JSON.stringify({ type: "token", token: "Xin chào!" }),
        });
        options.onmessage?.({
          id: "2",
          event: "done",
          data: "[DONE]",
        });
        await options.onclose?.();
      }
    );

    const { result } = renderHook(() => useStreamingChat({ activeSessionId: "s1" }));

    act(() => {
      result.current.setInputText("Chào bạn");
    });

    await act(async () => {
      await result.current.sendMessage();
    });

    expect(result.current.isGenerating).toBe(false);
    expect(result.current.messages[1].is_streaming).toBe(false);
  });

  it("try/finally ensures isGenerating is reset to false on network error", async () => {
    vi.mocked(fetchEventSourceModule.fetchEventSource).mockImplementation(
      async () => {
        throw new Error("Network offline");
      }
    );

    const { result } = renderHook(() => useStreamingChat({ activeSessionId: "s1" }));

    act(() => {
      result.current.setInputText("Test error");
    });

    await act(async () => {
      await result.current.sendMessage();
    });

    // Must never stay stuck in isGenerating
    expect(result.current.isGenerating).toBe(false);
    expect(result.current.messages[1].is_streaming).toBe(false);
    expect(result.current.messages[1].content).toContain("Lỗi kết nối");
  });

  it("normalizes backend citation events with bounding_boxes and document_id to CitationBadgeData", async () => {
    vi.mocked(fetchEventSourceModule.fetchEventSource).mockImplementation(
      async (_url, options) => {
        options.onmessage?.({
          id: "cit-1",
          event: "message",
          data: JSON.stringify({
            type: "citations",
            citations: [
              {
                citation_id: "cit_1",
                document_id: "doc-abc",
                document_title: "Attention Paper",
                page_number: 3,
                bounding_boxes: [[0.1, 0.2, 0.8, 0.5, 3]],
                score: 0.95,
              },
            ],
          }),
        });
        options.onmessage?.({
          id: "done-1",
          event: "done",
          data: "[DONE]",
        });
        await options.onclose?.();
      }
    );

    const { result } = renderHook(() => useStreamingChat({ activeSessionId: "s1" }));

    act(() => {
      result.current.setInputText("Trích dẫn tài liệu");
    });

    await act(async () => {
      await result.current.sendMessage();
    });

    expect(result.current.isGenerating).toBe(false);
    const asstMsg = result.current.messages[1];
    expect(asstMsg.citations).toBeDefined();
    expect(asstMsg.citations?.length).toBe(1);
    expect(asstMsg.citations?.[0]).toEqual({
      citation_id: "cit_1",
      paper_id: "doc-abc",
      paper_title: "Attention Paper",
      page: 3,
      bbox: [0.1, 0.2, 0.8, 0.5, 3],
    });
  });
});
