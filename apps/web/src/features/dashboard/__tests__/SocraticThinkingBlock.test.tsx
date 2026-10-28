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

  it("renders live thinking status during streaming (Thought for Xs >)", () => {
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

    // Live thinking indicator renders during stream
    expect(screen.getByTestId("socratic-working-status")).toBeInTheDocument();
    expect(screen.getByText(/Thought for \d+s >/i)).toBeInTheDocument();
    // Does NOT render robotic debug bounding box lines
    expect(screen.queryByText(/Analyzed Bounding Box/i)).toBeNull();

    // Timer increments live
    act(() => {
      vi.advanceTimersByTime(2000);
    });
    expect(screen.getByText(/Thought for \d+s >/i)).toBeInTheDocument();
  });

  it("automatically collapses to single header (Thought for Xs >) when is_streaming is false", () => {
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

    // Header displays Thought for 3s >
    const header = screen.getByRole("button", {
      name: /Thought for 3s >/i,
    });
    expect(header).toBeInTheDocument();

    // Detailed full thought text is collapsed (hidden)
    expect(
      screen.queryByText("Detailed internal chain of thought reasoning.")
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/Analyzed Bounding Box/i)).toBeNull();
  });

  it("expands thought monologue on click, and collapses on second click", () => {
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
      name: /Thought for 4s >/i,
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
    // Must NOT render robotic bounding box lines
    expect(screen.queryByText(/Analyzed Bounding Box/i)).toBeNull();

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
