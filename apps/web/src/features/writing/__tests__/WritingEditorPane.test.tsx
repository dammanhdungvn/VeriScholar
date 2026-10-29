import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { WritingEditorPane } from "../components/WritingEditorPane";
import { useWritingStore } from "../stores/useWritingStore";

describe("WritingEditorPane", () => {
  beforeEach(() => {
    useWritingStore.setState({
      activeDraftId: "test-draft-123",
      editorContent: "\\documentclass{article}\n\\begin{document}\n\\invalidcmd\n\\end{document}",
      editorBibContent: "",
      activeFile: "main.tex",
      lastCompileResult: {
        success: false,
        diagnostics: [],
        errors: [
          {
            line: 3,
            column: 1,
            rule: "SYNTAX_ERROR",
            message: "Undefined control sequence \\invalidcmd",
            suggested_fix: "Define the macro or fix typo",
          },
        ],
        logs: "Error on line 3",
        duration_seconds: 0.5,
      },
    });
  });

  it("renders line numbers and marks line 3 with gutter error indicator", () => {
    render(<WritingEditorPane />);

    const gutterError = screen.getByTestId("gutter-error-line-3");
    expect(gutterError).toBeInTheDocument();
    expect(gutterError).toHaveTextContent("3");
    expect(gutterError.className).toContain("text-rose-500");
  });

  it("renders diagnostics error card with exact line number and message", () => {
    render(<WritingEditorPane />);

    expect(screen.getByText(/Phát hiện 1 cảnh báo cú pháp \/ lỗi biên dịch:/)).toBeInTheDocument();
    expect(screen.getByText(/Dòng 3, Cột 1 \[SYNTAX_ERROR\]/)).toBeInTheDocument();
    expect(screen.getByText(/Undefined control sequence \\invalidcmd/)).toBeInTheDocument();
  });

  it("scrolls and focuses line when clicking error card or gutter", () => {
    render(<WritingEditorPane />);

    const errorItem = screen.getByTestId("error-item-3");
    const textarea = screen.getByTestId("writing-editor-textarea") as HTMLTextAreaElement;

    // Spy on setSelectionRange
    const spySelect = vi.spyOn(textarea, "setSelectionRange");

    fireEvent.click(errorItem);

    expect(spySelect).toHaveBeenCalled();
  });
});
