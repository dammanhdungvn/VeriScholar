import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ReasoningThinkingAccordion } from "../components/ReasoningThinkingAccordion";

describe("ReasoningThinkingAccordion Component", () => {
  it("renders thinking loading state when isStreaming is true", () => {
    render(<ReasoningThinkingAccordion thoughtContent="Đang phân tích..." isStreaming={true} />);
    expect(screen.getByText(/Thinking/i)).toBeInTheDocument();
  });

  it("renders collapsible finished state and expands on click", () => {
    render(<ReasoningThinkingAccordion thoughtContent="Bắt đầu suy luận công thức..." isStreaming={false} />);
    const trigger = screen.getByText(/Thinking Finished/i);
    expect(trigger).toBeInTheDocument();
    fireEvent.click(trigger);
    expect(screen.getByText(/Bắt đầu suy luận công thức.../i)).toBeVisible();
  });

  it("returns null when no thought content and not streaming", () => {
    const { container } = render(<ReasoningThinkingAccordion thoughtContent="" isStreaming={false} />);
    expect(container.firstChild).toBeNull();
  });

  it("supports defaultExpanded and allows collapsing back", () => {
    render(
      <ReasoningThinkingAccordion
        thoughtContent="Phân tích định lý..."
        isStreaming={false}
        defaultExpanded={true}
      />
    );
    expect(screen.getByText(/Phân tích định lý.../i)).toBeVisible();
    const trigger = screen.getByText(/Thinking Finished/i);
    fireEvent.click(trigger);
    expect(screen.queryByText(/Phân tích định lý.../i)).not.toBeInTheDocument();
  });
});
