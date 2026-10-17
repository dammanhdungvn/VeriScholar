import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { AssociativeMemoryCard } from "./AssociativeMemoryCard";

describe("AssociativeMemoryCard Component", () => {
  it("renders card with suggestion message matching prompt specification", () => {
    render(
      <AssociativeMemoryCard
        title="Attention Is All You Need"
        page={4}
        noteSnippet="Cơ chế Self-Attention loại bỏ hoàn toàn recurrence."
        similarityScore={0.92}
      />
    );

    // Checks header & label
    expect(screen.getByRole("region", { name: "Gợi ý liên kết tri thức" })).toBeInTheDocument();
    expect(screen.getByText(/Proactive Associative Memory/i)).toBeInTheDocument();

    // Checks message matching: "💡 Gợi ý liên kết: Đoạn này tương đồng với ghi chú tại bài {title} (Trang {page})"
    expect(screen.getByText(/💡 Gợi ý liên kết: Đoạn này tương đồng với ghi chú tại bài/i)).toBeInTheDocument();
    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText(/\(Trang 4\)/i)).toBeInTheDocument();

    // Checks snippet & similarity
    expect(screen.getByText(/Cơ chế Self-Attention/i)).toBeInTheDocument();
    expect(screen.getByText("92%")).toBeInTheDocument();

    // Checks action buttons
    expect(screen.getByRole("button", { name: /Chèn trích dẫn/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Xem ghi chú/i })).toBeInTheDocument();
  });

  it("handles [Chèn trích dẫn] click and displays confirmation", () => {
    const onInsert = vi.fn();
    render(
      <AssociativeMemoryCard
        title="FlashAttention"
        page={2}
        citationKey="dao2022flashattention"
        onInsertCitation={onInsert}
      />
    );

    const insertBtn = screen.getByRole("button", { name: /Chèn trích dẫn/i });
    fireEvent.click(insertBtn);

    expect(onInsert).toHaveBeenCalledWith("dao2022flashattention");
    expect(screen.getByText(/Đã chèn/i)).toBeInTheDocument();
  });

  it("handles [Xem ghi chú] click with noteId", () => {
    const onView = vi.fn();
    render(
      <AssociativeMemoryCard
        title="BERT: Pre-training of Deep Bidirectional Transformers"
        page={3}
        noteId="note-bert-01"
        onViewNote={onView}
      />
    );

    const viewBtn = screen.getByRole("button", { name: /Xem ghi chú/i });
    fireEvent.click(viewBtn);

    expect(onView).toHaveBeenCalledWith("note-bert-01");
  });

  it("calls onDismiss when close button is clicked", () => {
    const onDismiss = vi.fn();
    render(
      <AssociativeMemoryCard
        title="LoRA"
        page={1}
        onDismiss={onDismiss}
      />
    );

    const closeBtn = screen.getByRole("button", { name: "Đóng gợi ý" });
    fireEvent.click(closeBtn);

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("derives effectiveCitationKey from title when citationKey is missing/undefined", () => {
    const onInsert = vi.fn();
    render(
      <AssociativeMemoryCard
        title="Attention Is All You Need"
        onInsertCitation={onInsert}
      />
    );

    const insertBtn = screen.getByTestId("insert-citation-btn");
    expect(insertBtn).toBeInTheDocument();
    fireEvent.click(insertBtn);

    expect(onInsert).toHaveBeenCalledWith("attentionisallyo");
    expect(screen.getByText("Đã chèn")).toBeInTheDocument();
  });

  it("handles title with special characters and symbols when citationKey is missing", () => {
    const onInsert = vi.fn();
    render(
      <AssociativeMemoryCard
        title="[Survey 2024] Transformer & LLM: What's Next?!"
        onInsertCitation={onInsert}
      />
    );

    const insertBtn = screen.getByTestId("insert-citation-btn");
    fireEvent.click(insertBtn);

    expect(onInsert).toHaveBeenCalledWith("survey2024transf");
  });

  it("handles empty title or title with only symbols without throwing runtime error", () => {
    const onInsert = vi.fn();
    render(
      <AssociativeMemoryCard
        title="???###!!!"
        onInsertCitation={onInsert}
      />
    );

    const insertBtn = screen.getByTestId("insert-citation-btn");
    expect(() => fireEvent.click(insertBtn)).not.toThrow();
    expect(onInsert).toHaveBeenCalledWith("");
  });

  it("prioritizes explicit citationKey over derived title key", () => {
    const onInsert = vi.fn();
    render(
      <AssociativeMemoryCard
        title="Some Random Title"
        citationKey="vaswani2017attention"
        onInsertCitation={onInsert}
      />
    );

    const insertBtn = screen.getByTestId("insert-citation-btn");
    fireEvent.click(insertBtn);

    expect(onInsert).toHaveBeenCalledWith("vaswani2017attention");
  });

  it("safely handles omission of all optional props (page, noteSnippet, similarityScore, onDismiss, onViewNote)", () => {
    render(<AssociativeMemoryCard title="Minimal Card" />);

    expect(screen.getByText(/\(Trang 1\)/i)).toBeInTheDocument();
    expect(screen.queryByText(/“/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Độ tương quan ngữ nghĩa/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Đóng gợi ý" })).not.toBeInTheDocument();

    const viewBtn = screen.getByTestId("view-note-btn");
    expect(() => fireEvent.click(viewBtn)).not.toThrow();
  });

  it("renders similarity score correctly when similarityScore is 0.0 or 1.0", () => {
    const { rerender } = render(
      <AssociativeMemoryCard title="Zero Similarity" similarityScore={0.0} />
    );
    expect(screen.getByText("0%")).toBeInTheDocument();

    rerender(
      <AssociativeMemoryCard title="Perfect Similarity" similarityScore={1.0} />
    );
    expect(screen.getByText("100%")).toBeInTheDocument();
  });
});
