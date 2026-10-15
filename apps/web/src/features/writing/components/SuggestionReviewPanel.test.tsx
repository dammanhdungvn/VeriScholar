import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SuggestionReviewPanel } from "./SuggestionReviewPanel";
import { useWritingStore } from "../stores/useWritingStore";
import type { PendingSuggestion } from "../types";

describe("SuggestionReviewPanel", () => {
  const mockSuggestion: PendingSuggestion = {
    id: "sugg-101",
    draft_id: "draft-abc",
    prompt: "Viết thêm phần thảo luận về attention",
    original_text: "Previous work used recurrence.",
    suggested_text: "Previous work used recurrence.\nRecent work leverages multi-head attention.",
    explanation: "Đã làm nổi bật bước chuyển dịch từ RNN sang Multi-head Attention.",
    confidence_score: 0.95,
    cursor_start: 10,
    cursor_end: 40,
    expected_version: 3,
    created_at: "2026-10-15T10:30:00Z",
  };

  beforeEach(() => {
    useWritingStore.getState().reset();
  });

  it("does not render when isOpen is false", () => {
    render(
      <SuggestionReviewPanel
        isOpen={false}
        suggestion={mockSuggestion}
      />
    );
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("does not render when suggestion is null", () => {
    render(<SuggestionReviewPanel isOpen={true} suggestion={null} />);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("renders suggestion details, confidence badge, and visual diff lines", () => {
    render(
      <SuggestionReviewPanel
        isOpen={true}
        suggestion={mockSuggestion}
      />
    );

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Xem xét đề xuất AI Assistant")).toBeInTheDocument();
    expect(screen.getByText("95% tin cậy")).toBeInTheDocument();
    expect(
      screen.getByText(`"${mockSuggestion.prompt}"`)
    ).toBeInTheDocument();
    expect(
      screen.getByText(mockSuggestion.explanation!)
    ).toBeInTheDocument();

    // Check Diff container
    const diffContainer = screen.getByTestId("diff-container");
    expect(diffContainer).toBeInTheDocument();
    expect(
      screen.getByText("Recent work leverages multi-head attention.")
    ).toBeInTheDocument();
  });

  it("switches to clean text view tab", () => {
    render(
      <SuggestionReviewPanel
        isOpen={true}
        suggestion={mockSuggestion}
      />
    );

    const cleanTab = screen.getByRole("button", {
      name: "Văn bản đề xuất hoàn chỉnh",
    });
    fireEvent.click(cleanTab);

    const cleanContainer = screen.getByTestId("clean-text-container");
    expect(cleanContainer).toBeInTheDocument();
    expect(cleanContainer.textContent).toContain(
      "Recent work leverages multi-head attention."
    );
  });

  it("triggers onAccept when accept button is clicked", async () => {
    const handleAccept = vi.fn().mockResolvedValue(undefined);
    render(
      <SuggestionReviewPanel
        isOpen={true}
        suggestion={mockSuggestion}
        onAccept={handleAccept}
      />
    );

    const acceptBtn = screen.getByTestId("accept-suggestion-btn");
    fireEvent.click(acceptBtn);

    expect(handleAccept).toHaveBeenCalledTimes(1);
    expect(handleAccept).toHaveBeenCalledWith(mockSuggestion);
  });

  it("triggers onReject when reject button is clicked", () => {
    const handleReject = vi.fn();
    render(
      <SuggestionReviewPanel
        isOpen={true}
        suggestion={mockSuggestion}
        onReject={handleReject}
      />
    );

    const rejectBtn = screen.getByTestId("reject-suggestion-btn");
    fireEvent.click(rejectBtn);

    expect(handleReject).toHaveBeenCalledTimes(1);
    expect(handleReject).toHaveBeenCalledWith(mockSuggestion);
  });

  it("closes/rejects on Escape key press", () => {
    const handleReject = vi.fn();
    render(
      <SuggestionReviewPanel
        isOpen={true}
        suggestion={mockSuggestion}
        onReject={handleReject}
      />
    );

    fireEvent.keyDown(window, { key: "Escape" });
    expect(handleReject).toHaveBeenCalledTimes(1);
  });

  it("disables buttons and indicates loading when isSaving is true", () => {
    render(
      <SuggestionReviewPanel
        isOpen={true}
        suggestion={mockSuggestion}
        isSaving={true}
      />
    );

    const acceptBtn = screen.getByTestId("accept-suggestion-btn");
    expect(acceptBtn).toBeDisabled();
    expect(screen.getByText("Đang lưu bản nháp...")).toBeInTheDocument();

    const rejectBtn = screen.getByTestId("reject-suggestion-btn");
    expect(rejectBtn).toBeDisabled();
  });
});
