import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AcademicMarkdownRenderer } from "../AcademicMarkdownRenderer";
import { TypingWaveIndicator } from "../TypingWaveIndicator";

describe("TypingWaveIndicator", () => {
  it("renders 3 bouncing dots with staggered animation", () => {
    render(<TypingWaveIndicator />);
    const indicator = screen.getByTestId("typing-wave-indicator");
    expect(indicator).toBeInTheDocument();
    expect(indicator.children).toHaveLength(3);
  });
});

describe("AcademicMarkdownRenderer isStreaming caret", () => {
  it("renders typing caret when isStreaming is true", () => {
    render(<AcademicMarkdownRenderer content="AI is drafting this response..." isStreaming={true} />);
    const caret = screen.getByTestId("typing-caret");
    expect(caret).toBeInTheDocument();
  });

  it("does not render typing caret when isStreaming is false", () => {
    render(<AcademicMarkdownRenderer content="AI finished drafting." isStreaming={false} />);
    expect(screen.queryByTestId("typing-caret")).toBeNull();
  });
});
