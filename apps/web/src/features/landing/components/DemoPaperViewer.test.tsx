import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { DemoPaperViewer } from "./DemoPaperViewer";
import { useLandingStore } from "../stores/useLandingStore";

// Mock MathRenderer to render plain text or formula
vi.mock("@/components/shared/MathRenderer", () => ({
  MathRenderer: ({ math }: { math: string }) => <span data-testid="math-renderer">{math}</span>,
}));

describe("DemoPaperViewer Component", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    useLandingStore.setState({
      activePaperId: "demo-paper-attention",
      activeCitationId: "cite-pos-enc",
      citationFocusTick: 0,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders paper title, canonical authors, and abstract", () => {
    render(<DemoPaperViewer />);

    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText("Ashish Vaswani*")).toBeInTheDocument();
    expect(screen.getByText("Noam Shazeer*")).toBeInTheDocument();
    expect(screen.getByText(/Google Brain • Google Research/i)).toBeInTheDocument();
    expect(screen.getByText(/The dominant sequence transduction models/i)).toBeInTheDocument();
  });

  it("renders Positional Encoding bounding box with active styling and optical crosshairs", () => {
    render(<DemoPaperViewer />);

    const bboxes = screen.getAllByTestId("demo-bbox-highlight");
    const posEncBox = bboxes[0];

    expect(posEncBox).toHaveAttribute("data-active", "true");
    expect(screen.getByText("Mục 3.5 • Tr. 6")).toBeInTheDocument();
    expect(screen.getByText("3.5 Positional Encoding")).toBeInTheDocument();
  });

  it("renders both sine and cosine KaTeX math formulas inside Positional Encoding block", () => {
    render(<DemoPaperViewer />);

    const mathElements = screen.getAllByTestId("math-renderer");
    const formulas = mathElements.map((el) => el.textContent);

    expect(formulas.some((f) => f?.includes("\\sin"))).toBe(true);
    expect(formulas.some((f) => f?.includes("\\cos"))).toBe(true);
  });

  it("switches citation when clicking on the bounding box", () => {
    render(<DemoPaperViewer />);

    const bboxes = screen.getAllByTestId("demo-bbox-highlight");
    const attentionBox = bboxes[1];

    fireEvent.click(attentionBox);

    expect(useLandingStore.getState().activeCitationId).toBe("cite-attention-formula");
  });

  it("triggers smooth auto-scroll to the active citation on mount and updates", () => {
    const scrollToMock = vi.fn();
    // Mock Element.prototype.scrollTo
    HTMLElement.prototype.scrollTo = scrollToMock;

    render(<DemoPaperViewer />);

    act(() => {
      vi.advanceTimersByTime(150);
    });

    expect(scrollToMock).toHaveBeenCalled();
    const callArgs = scrollToMock.mock.calls[0][0];
    expect(callArgs).toHaveProperty("top");
    expect(callArgs).toHaveProperty("behavior", "smooth");
  });
});
