import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { DraftCommentsPane } from "./DraftCommentsPane";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import type { DraftComment } from "../types";

vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    getComments: vi.fn(),
    createComment: vi.fn(),
    updateComment: vi.fn(),
    deleteComment: vi.fn(),
  },
}));

describe("DraftCommentsPane", () => {
  const mockComment: DraftComment = {
    id: "comm-1",
    draft_id: "draft-101",
    author_id: "user-1",
    author_name: "Alan Turing",
    start_offset: 12,
    end_offset: 28,
    selected_text: "self-attention",
    comment_text: "Should we compare computational complexity here?",
    is_resolved: false,
    created_at: "2026-10-15T10:00:00Z",
    updated_at: "2026-10-15T10:00:00Z",
    replies: [
      {
        id: "reply-1",
        draft_id: "draft-101",
        author_id: "user-2",
        author_name: "Ada Lovelace",
        start_offset: 12,
        end_offset: 28,
        selected_text: "self-attention",
        comment_text: "Yes, refer to Table 1.",
        parent_id: "comm-1",
        is_resolved: false,
        created_at: "2026-10-15T10:30:00Z",
        updated_at: "2026-10-15T10:30:00Z",
      },
    ],
  };

  const mockResolvedComment: DraftComment = {
    id: "comm-2",
    draft_id: "draft-101",
    author_id: "user-3",
    author_name: "Claude Shannon",
    start_offset: 50,
    end_offset: 70,
    selected_text: "entropy calculations",
    comment_text: "Verified citation formatting.",
    is_resolved: true,
    created_at: "2026-10-15T09:00:00Z",
    updated_at: "2026-10-15T09:15:00Z",
    replies: [],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    useWritingStore.getState().reset();
    useWritingStore.getState().setDraft({
      id: "draft-101",
      user_id: "user-1",
      title: "Paper Title",
      content: "Intro section on self-attention and entropy calculations.",
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });
    useWritingStore.getState().setComments([mockComment, mockResolvedComment]);
  });

  it("renders header, filter tabs with badges, and active comment card", () => {
    render(<DraftCommentsPane />);

    expect(screen.getByText("Phản Biện & Nhận Xét")).toBeInTheDocument();
    expect(screen.getByText("Chưa xử lý")).toBeInTheDocument();
    expect(screen.getByText("Đã giải quyết")).toBeInTheDocument();

    // Active comment should be visible in active tab
    expect(screen.getByText("Alan Turing")).toBeInTheDocument();
    expect(screen.getByText('"self-attention"')).toBeInTheDocument();
    expect(
      screen.getByText("Should we compare computational complexity here?")
    ).toBeInTheDocument();

    // Threaded reply should be visible
    expect(screen.getByText("Ada Lovelace")).toBeInTheDocument();
    expect(screen.getByText("Yes, refer to Table 1.")).toBeInTheDocument();

    // Resolved comment shouldn't be visible in active tab
    expect(screen.queryByText("Claude Shannon")).toBeNull();
  });

  it("switches to resolved tab and shows resolved comments", () => {
    render(<DraftCommentsPane />);

    const resolvedTabBtn = screen.getByTestId("filter-resolved-comments-btn");
    fireEvent.click(resolvedTabBtn);

    // Resolved comment is now visible
    expect(screen.getByText("Claude Shannon")).toBeInTheDocument();
    expect(screen.getByText("Verified citation formatting.")).toBeInTheDocument();
    expect(screen.getByText("Đã xong")).toBeInTheDocument();

    // Active comment is hidden
    expect(screen.queryByText("Alan Turing")).toBeNull();
  });

  it("toggles resolve and unresolve status", async () => {
    vi.mocked(draftsApi.updateComment).mockResolvedValueOnce({
      ...mockComment,
      is_resolved: true,
    });

    render(<DraftCommentsPane />);

    const resolveBtn = screen.getByTestId("resolve-comment-btn-comm-1");
    await act(async () => {
      fireEvent.click(resolveBtn);
    });

    expect(draftsApi.updateComment).toHaveBeenCalledWith("draft-101", "comm-1", {
      is_resolved: true,
    });

    // Switch to resolved tab to verify unresolve button
    const resolvedTabBtn = screen.getByTestId("filter-resolved-comments-btn");
    fireEvent.click(resolvedTabBtn);

    vi.mocked(draftsApi.updateComment).mockResolvedValueOnce({
      ...mockComment,
      is_resolved: false,
    });

    const reopenBtn = screen.getByTestId("resolve-comment-btn-comm-1");
    expect(reopenBtn).toHaveTextContent("Mở lại");

    await act(async () => {
      fireEvent.click(reopenBtn);
    });

    expect(draftsApi.updateComment).toHaveBeenCalledWith("draft-101", "comm-1", {
      is_resolved: false,
    });
  });

  it("deletes a comment when delete button is clicked", async () => {
    vi.mocked(draftsApi.deleteComment).mockResolvedValueOnce();

    render(<DraftCommentsPane />);

    const deleteBtn = screen.getByTestId("delete-comment-btn-comm-1");
    await act(async () => {
      fireEvent.click(deleteBtn);
    });

    expect(draftsApi.deleteComment).toHaveBeenCalledWith("draft-101", "comm-1");
    expect(useWritingStore.getState().comments.some((c) => c.id === "comm-1")).toBe(
      false
    );
  });

  it("submits a new top-level comment", async () => {
    const newComment: DraftComment = {
      id: "comm-new",
      draft_id: "draft-101",
      author_id: "user-1",
      author_name: "You",
      start_offset: 0,
      end_offset: 5,
      selected_text: "Intro",
      comment_text: "Need a stronger hook here.",
      is_resolved: false,
      created_at: "2026-10-15T11:00:00Z",
      updated_at: "2026-10-15T11:00:00Z",
      replies: [],
    };
    vi.mocked(draftsApi.createComment).mockResolvedValueOnce(newComment);

    useWritingStore.getState().setSelectionRange({ start: 0, end: 5 });

    render(<DraftCommentsPane />);

    const input = screen.getByTestId("new-comment-input");
    fireEvent.change(input, { target: { value: "Need a stronger hook here." } });

    const submitBtn = screen.getByTestId("submit-new-comment-btn");
    await act(async () => {
      fireEvent.click(submitBtn);
    });

    expect(draftsApi.createComment).toHaveBeenCalledWith("draft-101", {
      start_offset: 0,
      end_offset: 5,
      selected_text: "Intro",
      comment_text: "Need a stronger hook here.",
    });

    expect(useWritingStore.getState().comments).toContainEqual(newComment);
    expect(input).toHaveValue("");
  });

  it("sends a threaded reply to an existing comment", async () => {
    const createdReply: DraftComment = {
      id: "reply-2",
      draft_id: "draft-101",
      author_id: "user-1",
      author_name: "Alan Turing",
      start_offset: 12,
      end_offset: 28,
      selected_text: "self-attention",
      comment_text: "Good point, updating now.",
      parent_id: "comm-1",
      is_resolved: false,
      created_at: "2026-10-15T10:45:00Z",
      updated_at: "2026-10-15T10:45:00Z",
    };
    vi.mocked(draftsApi.createComment).mockResolvedValueOnce(createdReply);

    render(<DraftCommentsPane />);

    // Click reply button to reveal input box
    const replyToggleBtn = screen.getByTestId("reply-comment-btn-comm-1");
    fireEvent.click(replyToggleBtn);

    const replyInput = screen.getByTestId("reply-input-comm-1");
    fireEvent.change(replyInput, { target: { value: "Good point, updating now." } });

    const sendReplyBtn = screen.getByTestId("send-reply-btn-comm-1");
    await act(async () => {
      fireEvent.click(sendReplyBtn);
    });

    expect(draftsApi.createComment).toHaveBeenCalledWith("draft-101", {
      start_offset: 12,
      end_offset: 28,
      selected_text: "self-attention",
      comment_text: "Good point, updating now.",
      parent_id: "comm-1",
    });

    const parent = useWritingStore
      .getState()
      .comments.find((c) => c.id === "comm-1");
    expect(parent?.replies).toContainEqual(createdReply);
  });

  it("calls onClose or closes pane via store when close button is clicked", () => {
    const onClose = vi.fn();
    render(<DraftCommentsPane onClose={onClose} />);

    const closeBtn = screen.getByTestId("close-comments-pane-btn");
    fireEvent.click(closeBtn);

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
