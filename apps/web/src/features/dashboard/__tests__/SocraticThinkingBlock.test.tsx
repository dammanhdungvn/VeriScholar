import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { SocraticThinkingBlock } from "../components/SocraticThinkingBlock";
import type { ChatMessage } from "@/types/dashboard";

describe("SocraticThinkingBlock Component", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders live activity stepper during streaming (Working..., Thought for Xs >)", () => {
    const message: ChatMessage = {
      id: "asst-1",
      session_id: "s-1",
      role: "assistant",
      content: "",
      created_at: new Date(Date.now()).toISOString(),
      is_streaming: true,
      thought: "Checking hypotheses against section 3...",
      citations: [
        {
          citation_id: "c-1",
          paper_id: "p-1",
          paper_title: "Paper",
          page: 3,
          bbox: [0, 0, 1, 1, 3],
        },
      ],
    };

    render(<SocraticThinkingBlock message={message} />);

    // Live activity stepper renders during stream
    expect(screen.getByText(/Working\.\.\./i)).toBeInTheDocument();
    expect(screen.getByText(/Thought for \d+s >/i)).toBeInTheDocument();
    expect(screen.getByText(/Reading paper chunks\.\.\./i)).toBeInTheDocument();
    expect(screen.getByText(/Analyzed Bounding Box #Page 3/i)).toBeInTheDocument();

    // Timer increments live
    act(() => {
      vi.advanceTimersByTime(2000);
    });
    expect(screen.getByText(/Thought for \d+s >/i)).toBeInTheDocument();
  });

  it("automatically collapses to single header (Worked for Xs > or Thought for Xs >) when is_streaming is false", () => {
    const message: ChatMessage = {
      id: "asst-2",
      session_id: "s-1",
      role: "assistant",
      content: "Final answer",
      created_at: new Date(Date.now() - 3000).toISOString(),
      is_streaming: false,
      thought: "Detailed internal chain of thought reasoning.",
      thought_duration_seconds: 3,
      citations: [
        {
          citation_id: "c-1",
          paper_id: "p-1",
          paper_title: "Paper",
          page: 1,
          bbox: [0, 0, 1, 1, 1],
        },
      ],
    };

    render(<SocraticThinkingBlock message={message} />);

    // Header displays Thought for 3s > (or Worked for 3s >)
    const header = screen.getByRole("button", {
      name: /(Thought|Worked) for 3s >/i,
    });
    expect(header).toBeInTheDocument();

    // Detailed action history and full thought text are collapsed (hidden)
    expect(screen.queryByText(/Working\.\.\./i)).not.toBeInTheDocument();
    expect(
      screen.queryByText("Detailed internal chain of thought reasoning.")
    ).not.toBeInTheDocument();
  });

  it("expands action history and full thought text on click, and collapses on second click", () => {
    const message: ChatMessage = {
      id: "asst-3",
      session_id: "s-1",
      role: "assistant",
      content: "Complete response",
      created_at: new Date().toISOString(),
      is_streaming: false,
      thought: "Synthesizing theoretical framework from section 2.",
      thought_duration_seconds: 4,
      citations: [
        {
          citation_id: "c-2",
          paper_id: "p-2",
          paper_title: "Paper 2",
          page: 2,
          bbox: [0, 0, 1, 1, 2],
        },
      ],
    };

    render(<SocraticThinkingBlock message={message} />);

    // Header exists in collapsed state
    const header = screen.getByRole("button", {
      name: /(Thought|Worked) for 4s >/i,
    });
    expect(header).toBeInTheDocument();
    expect(
      screen.queryByText("Synthesizing theoretical framework from section 2.")
    ).not.toBeInTheDocument();

    // 1st click: expands
    fireEvent.click(header);
    expect(
      screen.getByText("Synthesizing theoretical framework from section 2.")
    ).toBeInTheDocument();
    expect(screen.getByText(/Reading paper chunks\.\.\./i)).toBeInTheDocument();
    expect(screen.getByText(/Analyzed Bounding Box #Page 2/i)).toBeInTheDocument();

    // 2nd click: collapses back
    fireEvent.click(header);
    expect(
      screen.queryByText("Synthesizing theoretical framework from section 2.")
    ).not.toBeInTheDocument();
  });

  it("returns null when message has no thought and is not streaming", () => {
    const message: ChatMessage = {
      id: "asst-4",
      session_id: "s-1",
      role: "assistant",
      content: "Hello",
      created_at: new Date().toISOString(),
      is_streaming: false,
    };

    const { container } = render(<SocraticThinkingBlock message={message} />);
    expect(container.firstChild).toBeNull();
  });
});
