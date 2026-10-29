import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ScholarSelectionMenu } from "../components/ScholarSelectionMenu";

describe("ScholarSelectionMenu Clean Copy Action", () => {
  it("renders 'Sao chép' button and copies raw plain text to clipboard", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText: writeTextMock } });

    const onClearMock = vi.fn();
    render(
      <ScholarSelectionMenu
        selectedText="Attention Is All You Need"
        coord={{ x: 100, y: 100 }}
        pageNumber={1}
        documentTitle="Transformer Paper"
        onAddToNote={vi.fn()}
        onClearSelection={onClearMock}
      />
    );

    const rawCopyBtn = screen.getByTestId("selection-copy-raw-btn");
    expect(rawCopyBtn).toBeInTheDocument();
    expect(rawCopyBtn).toHaveTextContent("Sao chép");

    await act(async () => {
      fireEvent.click(rawCopyBtn);
    });

    expect(writeTextMock).toHaveBeenCalledWith("Attention Is All You Need");
    expect(rawCopyBtn).toHaveTextContent("Đã chép");
  });

  it("falls back to document.execCommand when navigator.clipboard.writeText throws", async () => {
    const writeTextMock = vi.fn().mockRejectedValue(new Error("Permission denied"));
    Object.assign(navigator, { clipboard: { writeText: writeTextMock } });
    const execCommandMock = vi.fn().mockReturnValue(true);
    document.execCommand = execCommandMock;

    const onClearMock = vi.fn();
    render(
      <ScholarSelectionMenu
        selectedText="Attention Is All You Need"
        coord={{ x: 100, y: 100 }}
        pageNumber={1}
        documentTitle="Transformer Paper"
        onAddToNote={vi.fn()}
        onClearSelection={onClearMock}
      />
    );

    const rawCopyBtn = screen.getByTestId("selection-copy-raw-btn");
    await act(async () => {
      fireEvent.click(rawCopyBtn);
    });

    expect(execCommandMock).toHaveBeenCalledWith("copy");
    expect(rawCopyBtn).toHaveTextContent("Đã chép");
  });

  it("cleans up timeout on unmount safely without firing onClearSelection", () => {
    vi.useFakeTimers();
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText: writeTextMock } });

    const onClearMock = vi.fn();
    const { unmount } = render(
      <ScholarSelectionMenu
        selectedText="Attention Is All You Need"
        coord={{ x: 100, y: 100 }}
        pageNumber={1}
        documentTitle="Transformer Paper"
        onAddToNote={vi.fn()}
        onClearSelection={onClearMock}
      />
    );

    const rawCopyBtn = screen.getByTestId("selection-copy-raw-btn");
    fireEvent.click(rawCopyBtn);

    unmount();
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(onClearMock).not.toHaveBeenCalled();
    vi.useRealTimers();
  });
});
