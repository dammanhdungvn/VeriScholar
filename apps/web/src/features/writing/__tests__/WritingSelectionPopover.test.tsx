import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { WritingSelectionPopover } from "../components/WritingSelectionPopover";

describe("WritingSelectionPopover Component", () => {
  it("renders Add to Chat and Ask AI buttons when open with selected text", () => {
    const onAddToChat = vi.fn();
    const onAskAi = vi.fn();

    render(
      <WritingSelectionPopover
        selectedText="Theorem 1: Convergence of Self-Attention"
        position={{ top: 100, left: 200 }}
        isOpen={true}
        onAddToChat={onAddToChat}
        onAskAi={onAskAi}
      />
    );

    const addBtn = screen.getByTestId("selection-add-to-chat-btn");
    const askBtn = screen.getByTestId("selection-ask-ai-btn");

    expect(addBtn).toBeInTheDocument();
    expect(addBtn).toHaveTextContent("Add to Chat");
    expect(askBtn).toBeInTheDocument();
    expect(askBtn).toHaveTextContent("Ask AI");

    fireEvent.click(addBtn);
    expect(onAddToChat).toHaveBeenCalledWith("Theorem 1: Convergence of Self-Attention");

    fireEvent.click(askBtn);
    expect(onAskAi).toHaveBeenCalledWith("Theorem 1: Convergence of Self-Attention");
  });

  it("does not render when isOpen is false", () => {
    render(
      <WritingSelectionPopover
        selectedText="Some selected text"
        position={{ top: 100, left: 200 }}
        isOpen={false}
        onAddToChat={vi.fn()}
        onAskAi={vi.fn()}
      />
    );

    expect(screen.queryByTestId("selection-popover-container")).not.toBeInTheDocument();
  });
});
