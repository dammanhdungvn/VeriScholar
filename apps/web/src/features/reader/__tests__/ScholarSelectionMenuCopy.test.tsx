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
});
