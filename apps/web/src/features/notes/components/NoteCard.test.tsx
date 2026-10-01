import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { NoteCard } from "./NoteCard";
import type { NoteResponse } from "@/types/note";

describe("NoteCard Component", () => {
  const mockNote: NoteResponse = {
    id: "note-1",
    selected_text: "Attention is all you need for sequence modeling.",
    page_number: 3,
    bounding_boxes: [[[0.1, 0.2, 0.8, 0.4, 3]] as unknown as [number, number, number, number, number]],
    user_note: "Nhận định quan trọng của nhóm nghiên cứu.",
    tags: ["core", "nlp"],
    frozen_snapshot: {},
    is_source_detached: false,
    version: 1,
    created_at: "2026-09-21T00:00:00Z",
    updated_at: "2026-09-21T00:00:00Z",
  };

  it("renders quote, page number, user note and tags", () => {
    render(<NoteCard note={mockNote} />);

    expect(screen.getByText(/Attention is all you need for sequence modeling/i)).toBeInTheDocument();
    expect(screen.getByText(/Trang 3/i)).toBeInTheDocument();
    expect(screen.getByText(/Nhận định quan trọng của nhóm nghiên cứu/i)).toBeInTheDocument();
    expect(screen.getByText("#core")).toBeInTheDocument();
    expect(screen.getByText("#nlp")).toBeInTheDocument();
  });

  it("triggers onJumpToPage when clicking page badge", () => {
    const onJump = vi.fn();
    render(<NoteCard note={mockNote} onJumpToPage={onJump} />);

    const pageBadge = screen.getByRole("button", { name: /xem trên trang 3/i });
    fireEvent.click(pageBadge);
    expect(onJump).toHaveBeenCalledWith(3, "note-1");
  });

  it("opens inline edit form and triggers onUpdateNote with version", async () => {
    const onUpdate = vi.fn().mockResolvedValue(undefined);
    render(<NoteCard note={mockNote} onUpdateNote={onUpdate} />);

    const editBtn = screen.getByRole("button", { name: /chỉnh sửa ghi chú/i });
    fireEvent.click(editBtn);

    const textarea = screen.getByPlaceholderText(/ghi chú phản biện/i);
    fireEvent.change(textarea, { target: { value: "Ý kiến bổ sung." } });

    const saveBtn = screen.getByRole("button", { name: /lưu/i });
    fireEvent.click(saveBtn);

    expect(onUpdate).toHaveBeenCalledWith(
      "note-1",
      "Ý kiến bổ sung.",
      ["core", "nlp"],
      1
    );
  });
});
