import { describe, it, expect, beforeEach } from "vitest";
import { useWorkspaceStore } from "./useWorkspaceStore";

describe("useWorkspaceStore (Lazy Session & Ingestion State)", () => {
  beforeEach(() => {
    useWorkspaceStore.getState().resetWorkspace();
  });

  it("initializes with default standby state and no active session (Zero DB Junk)", () => {
    const state = useWorkspaceStore.getState();
    expect(state.isStandby).toBe(true);
    expect(state.activeSessionId).toBeNull();
    expect(state.activeDocumentId).toBeNull();
    expect(state.documentStatus).toBe("idle");
    expect(state.uploadProgress).toBe(0);
    expect(state.errorMessage).toBeNull();
  });

  it("initNewStandbyChat resets state to standby without creating sessions", () => {
    useWorkspaceStore.getState().setSession("sess-123");
    useWorkspaceStore.getState().setDocument("doc-456", "Paper Title");
    useWorkspaceStore.getState().setStatus("completed", 100);

    useWorkspaceStore.getState().initNewStandbyChat();

    const state = useWorkspaceStore.getState();
    expect(state.isStandby).toBe(true);
    expect(state.activeSessionId).toBeNull();
    expect(state.activeDocumentId).toBeNull();
    expect(state.documentStatus).toBe("idle");
    expect(state.uploadProgress).toBe(0);
  });

  it("tracks ingestion progression through stages", () => {
    useWorkspaceStore.getState().setStatus("uploading", 15, "Đang tải tệp lên máy chủ an toàn...");
    expect(useWorkspaceStore.getState().documentStatus).toBe("uploading");
    expect(useWorkspaceStore.getState().uploadProgress).toBe(15);
    expect(useWorkspaceStore.getState().statusStage).toBe("Đang tải tệp lên máy chủ an toàn...");

    useWorkspaceStore.getState().setStatus("validating", 35, "Đang thẩm định cấu trúc học thuật...");
    expect(useWorkspaceStore.getState().documentStatus).toBe("validating");
    expect(useWorkspaceStore.getState().uploadProgress).toBe(35);

    useWorkspaceStore.getState().setStatus("parsing", 75, "Đang phân tích layout...");
    expect(useWorkspaceStore.getState().documentStatus).toBe("parsing");
    expect(useWorkspaceStore.getState().uploadProgress).toBe(75);

    useWorkspaceStore.getState().setStatus("completed", 100);
    expect(useWorkspaceStore.getState().documentStatus).toBe("completed");
    expect(useWorkspaceStore.getState().uploadProgress).toBe(100);
    expect(useWorkspaceStore.getState().isStandby).toBe(false);
  });

  it("handles errors and updates error state", () => {
    useWorkspaceStore.getState().setError("Tệp tải lên không có cấu trúc bài báo nghiên cứu khoa học.");
    const state = useWorkspaceStore.getState();
    expect(state.documentStatus).toBe("error");
    expect(state.errorMessage).toBe("Tệp tải lên không có cấu trúc bài báo nghiên cứu khoa học.");
  });
});
