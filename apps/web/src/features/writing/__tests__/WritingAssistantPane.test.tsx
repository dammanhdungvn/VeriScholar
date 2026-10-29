import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { WritingAssistantPane } from "../components/WritingAssistantPane";
import { draftsApi } from "../api/draftsApi";
import { useWritingStore } from "../stores/useWritingStore";

vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    undoDraft: vi.fn(),
    streamDraftChat: vi.fn(),
  },
}));

describe("WritingAssistantPane", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useWritingStore.getState().reset();
    useWritingStore.setState({ activeDraftId: "draft-123" });
  });

  it("renders single clean icon without duplicate emoji and shows 'Hoàn tác' when undo snapshot is available", () => {
    useWritingStore.setState({
      draft: {
        id: "draft-123",
        user_id: "u-1",
        title: "Test Draft",
        content: "New content",
        format: "latex",
        version: 2,
        created_at: "2026-10-29T00:00:00Z",
        updated_at: "2026-10-29T00:00:00Z",
        previous_snapshot: {
          undo: {
            content: "Old content",
            version: 1,
            saved_at: "2026-10-29T00:00:00Z",
          },
          redo: null,
        },
      },
    });

    render(<WritingAssistantPane />);

    const undoBtn = screen.getByTestId("undo-draft-btn");
    expect(undoBtn).toBeInTheDocument();
    expect(undoBtn).not.toBeDisabled();
    expect(undoBtn.textContent).toBe("Hoàn tác");
    expect(undoBtn.textContent).not.toContain("↩️");
  });

  it("dynamically shows 'Khôi phục (Redo)' when redo snapshot is available", () => {
    useWritingStore.setState({
      draft: {
        id: "draft-123",
        user_id: "u-1",
        title: "Test Draft",
        content: "Old content restored",
        format: "latex",
        version: 3,
        created_at: "2026-10-29T00:00:00Z",
        updated_at: "2026-10-29T00:00:00Z",
        previous_snapshot: {
          undo: null,
          redo: {
            content: "AI generated content",
            version: 2,
            saved_at: "2026-10-29T00:00:00Z",
          },
        },
      },
    });

    render(<WritingAssistantPane />);

    const redoBtn = screen.getByTestId("undo-draft-btn");
    expect(redoBtn).toBeInTheDocument();
    expect(redoBtn.textContent).toBe("Khôi phục (Redo)");
  });

  it("calls draftsApi.undoDraft when clicked", async () => {
    useWritingStore.setState({
      draft: {
        id: "draft-123",
        user_id: "u-1",
        title: "Test Draft",
        content: "New content",
        format: "latex",
        version: 2,
        created_at: "2026-10-29T00:00:00Z",
        updated_at: "2026-10-29T00:00:00Z",
        previous_snapshot: {
          undo: { content: "Old content" },
        },
      },
    });

    vi.mocked(draftsApi.undoDraft).mockResolvedValue({
      id: "draft-123",
      user_id: "u-1",
      title: "Test Draft",
      content: "Old content",
      format: "latex",
      version: 3,
      created_at: "2026-10-29T00:00:00Z",
      updated_at: "2026-10-29T00:00:00Z",
      previous_snapshot: {
        undo: null,
        redo: { content: "New content" },
      },
    });

    render(<WritingAssistantPane />);

    const undoBtn = screen.getByTestId("undo-draft-btn");
    fireEvent.click(undoBtn);

    expect(draftsApi.undoDraft).toHaveBeenCalledWith("draft-123");
  });
});
