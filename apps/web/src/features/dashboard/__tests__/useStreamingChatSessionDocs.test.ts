import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useStreamingChat } from "../hooks/useStreamingChat";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";

vi.mock("@/features/sessions/api/sessionsApi", () => ({
  sessionsApi: {
    createSession: vi.fn(),
    addDocumentToSession: vi.fn(),
    listSessionMessages: vi.fn().mockResolvedValue({ data: [] }),
    deleteSessionMessage: vi.fn(),
  },
}));

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn(),
}));

describe("useStreamingChat Session Document Isolation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useReaderStore.setState({
      openDocumentIds: ["doc-stale-attention"],
      activeDocumentId: "doc-stale-attention",
    });
  });

  it("does NOT automatically attach stale openDocumentIds when creating a session from a plain-text prompt", async () => {
    vi.mocked(sessionsApi.createSession).mockResolvedValue({
      data: { id: "new-session-123", title: "Nghiên cứu: hello" } as any,
      headers: new Headers(),
      etag: null,
    });

    const { result } = renderHook(() =>
      useStreamingChat({
        activeSessionId: undefined,
      })
    );

    await act(async () => {
      result.current.sendMessage("hello");
    });

    expect(sessionsApi.createSession).toHaveBeenCalledWith({
      title: "Nghiên cứu: hello",
    });
    // Stale documents in reader store must NOT be attached to new session!
    expect(sessionsApi.addDocumentToSession).not.toHaveBeenCalled();
  });
});
