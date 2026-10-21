import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { WritingEditorPane } from "./WritingEditorPane";
import { buildSelectionContextBuffer } from "../lib/contextBuffer";
import { useWritingStore } from "../stores/useWritingStore";

describe("buildSelectionContextBuffer", () => {
  it("formats surrounding context window correctly with XML tags", () => {
    const fullText = "Introduction paragraph before.\nThis is the targeted sentence to rewrite.\nConclusion paragraph following.";
    const target = "This is the targeted sentence to rewrite.";
    const start = fullText.indexOf(target);
    const end = start + target.length;

    const buffer = buildSelectionContextBuffer(fullText, start, end, 100);

    expect(buffer).toContain("<pre_context>");
    expect(buffer).toContain("Introduction paragraph before.");
    expect(buffer).toContain("</pre_context>");

    expect(buffer).toContain("<target_selection>");
    expect(buffer).toContain(target);
    expect(buffer).toContain("</target_selection>");

    expect(buffer).toContain("<post_context>");
    expect(buffer).toContain("Conclusion paragraph following.");
    expect(buffer).toContain("</post_context>");
  });
});

describe("WritingEditorPane", () => {
  beforeEach(() => {
    useWritingStore.getState().reset();
  });

  it("renders editor toolbar, line count, and textarea, and updates line count upon typing", () => {
    useWritingStore.getState().setEditorContent("\\section{Intro}\nHello world\nTesting 123");
    render(<WritingEditorPane />);

    expect(screen.getByText("main.tex")).toBeInTheDocument();
    expect(screen.getByText("(3 dòng)")).toBeInTheDocument();
    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement;
    expect(textarea).toBeInTheDocument();

    // Type new content with 5 lines
    fireEvent.change(textarea, {
      target: { value: "Line 1\nLine 2\nLine 3\nLine 4\nLine 5" },
    });

    expect(screen.getByText("(5 dòng)")).toBeInTheDocument();
    expect(useWritingStore.getState().editorContent).toBe("Line 1\nLine 2\nLine 3\nLine 4\nLine 5");
    expect(useWritingStore.getState().isDirty).toBe(true);
  });

  it("triggers onSelectionAddToChat with formatted context buffer when clicking [Thêm vào Chat]", () => {
    const onSelectionAddToChat = vi.fn();
    const content = "Prior literature established baseline.\nTransformer models scale better with compute.\nFuture work will explore sparsity.";
    useWritingStore.getState().setEditorContent(content);

    render(
      <WritingEditorPane onSelectionAddToChat={onSelectionAddToChat} />
    );

    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement;
    const target = "Transformer models scale better with compute.";
    const start = content.indexOf(target);
    const end = start + target.length;

    // Simulate user selecting text
    textarea.selectionStart = start;
    textarea.selectionEnd = end;
    fireEvent.select(textarea);

    // Expect selection indicator and button
    expect(screen.getByText(`Đã chọn ${target.length} ký tự`)).toBeInTheDocument();
    const addToChatBtn = screen.getByRole("button", { name: /Thêm vào Chat/i });
    expect(addToChatBtn).toBeInTheDocument();

    // Click [Thêm vào Chat]
    fireEvent.click(addToChatBtn);

    expect(onSelectionAddToChat).toHaveBeenCalledTimes(1);
    const passedBuffer = onSelectionAddToChat.mock.calls[0][0];
    expect(passedBuffer).toContain("<pre_context>");
    expect(passedBuffer).toContain("Prior literature established baseline.");
    expect(passedBuffer).toContain("<target_selection>");
    expect(passedBuffer).toContain("Transformer models scale better with compute.");
    expect(passedBuffer).toContain("<post_context>");
    expect(passedBuffer).toContain("Future work will explore sparsity.");
  });

  it("triggers onSelectionVerify when clicking [Kiểm chứng]", () => {
    const onSelectionVerify = vi.fn();
    const content = "Attention is all you need for sequence translation.";
    useWritingStore.getState().setEditorContent(content);

    render(
      <WritingEditorPane onSelectionVerify={onSelectionVerify} />
    );

    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement;
    textarea.selectionStart = 0;
    textarea.selectionEnd = 9; // "Attention"
    fireEvent.select(textarea);

    const verifyBtn = screen.getByRole("button", { name: /Kiểm chứng/i });
    fireEvent.click(verifyBtn);

    expect(onSelectionVerify).toHaveBeenCalledWith("Attention");
  });

  it("renders Overleaf file tabs, [Code | Visual] toggle, and rich formatting toolbar buttons", () => {
    useWritingStore.getState().setEditorContent("\\section{Intro}\nHello world");

    render(<WritingEditorPane />);

    // File tabs
    expect(screen.getByTestId("editor-tab-main")).toBeInTheDocument();
    expect(screen.getByTestId("editor-tab-bib")).toBeInTheDocument();

    // View mode switch
    expect(screen.getByTestId("editor-view-code")).toBeInTheDocument();
    const visualBtn = screen.getByTestId("editor-view-visual");
    expect(visualBtn).toBeInTheDocument();

    // Toggle to visual view
    fireEvent.click(visualBtn);
    expect(screen.getByText("Chế độ Visual Preview")).toBeInTheDocument();

    // Toggle back to code view
    fireEvent.click(screen.getByTestId("editor-view-code"));

    // Formatting buttons
    const boldBtn = screen.getByTestId("format-bold-btn");
    const italicBtn = screen.getByTestId("format-italic-btn");
    const mathBtn = screen.getByTestId("format-math-btn");
    const tableBtn = screen.getByTestId("format-table-btn");
    const listBtn = screen.getByTestId("format-list-btn");
    const orderedBtn = screen.getByTestId("format-ordered-btn");
    const sectionBtn = screen.getByTestId("format-section-btn");

    expect(boldBtn).toBeInTheDocument();
    expect(italicBtn).toBeInTheDocument();
    expect(mathBtn).toBeInTheDocument();
    expect(tableBtn).toBeInTheDocument();
    expect(listBtn).toBeInTheDocument();
    expect(orderedBtn).toBeInTheDocument();
    expect(sectionBtn).toBeInTheDocument();

    // Click bold button
    fireEvent.click(boldBtn);
    expect(useWritingStore.getState().editorContent).toContain("\\textbf{");
  });
});
