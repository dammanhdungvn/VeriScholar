import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { WritingHeaderBar } from "./WritingHeaderBar";
import { useWritingStore } from "../stores/useWritingStore";
import type { Draft } from "../types";

describe("WritingHeaderBar", () => {
  const mockDraft: Draft = {
    id: "draft-xyz",
    user_id: "user-1",
    title: "Quantum Transformer Paper",
    content: "Content",
    format: "latex",
    version: 4,
    created_at: "2026-10-15T00:00:00Z",
    updated_at: "2026-10-15T00:00:00Z",
  };

  beforeEach(() => {
    useWritingStore.getState().reset();
    useWritingStore.getState().setDraft(mockDraft);
  });

  it("renders draft title, version tag, and saved status", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    expect(screen.getByText("Quantum Transformer Paper")).toBeInTheDocument();
    expect(screen.getByText("v4")).toBeInTheDocument();
    expect(screen.getByText("Đã lưu")).toBeInTheDocument();
  });

  it("opens layout pocket popover and switches mode on option click", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    // Click layout dropdown trigger
    const layoutTrigger = screen.getByTestId("header-layout-dropdown");
    fireEvent.click(layoutTrigger);

    // Popover content should be open
    expect(screen.getByTestId("layout-popover-content")).toBeInTheDocument();

    const dualCodeBtn = screen.getByTestId("mode-dual-code");
    fireEvent.click(dualCodeBtn);

    expect(useWritingStore.getState().workspaceMode).toBe("dual-code");
  });

  it("calls onSave and onCompile directly from prominent buttons, and onExportBundle from tools popover", () => {
    const onSave = vi.fn();
    const onCompile = vi.fn();
    const onExportBundle = vi.fn();

    // Mark dirty so save button is enabled
    useWritingStore.getState().setEditorContent("Modified");

    render(
      <BrowserRouter>
        <WritingHeaderBar
          onSave={onSave}
          onCompile={onCompile}
          onExportBundle={onExportBundle}
        />
      </BrowserRouter>
    );

    // 1. Save button is prominent
    const saveBtn = screen.getByText("Lưu");
    fireEvent.click(saveBtn);
    expect(onSave).toHaveBeenCalledTimes(1);

    // 2. Compile button is prominent
    const compileBtn = screen.getByText("Biên dịch");
    fireEvent.click(compileBtn);
    expect(onCompile).toHaveBeenCalledTimes(1);

    // 3. Export bundle is inside tools popover
    const toolsTrigger = screen.getByTestId("header-tools-dropdown");
    fireEvent.click(toolsTrigger);

    const exportBtn = screen.getByTestId("header-export-bundle-btn");
    fireEvent.click(exportBtn);
    expect(onExportBundle).toHaveBeenCalledTimes(1);
  });

  it("opens Asset modal from tools pocket dropdown and does not render Share, Comments, or Overleaf buttons", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);

    // Open tools dropdown
    fireEvent.click(screen.getByTestId("header-tools-dropdown"));
    const assetsBtn = screen.getByTestId("header-assets-btn");
    expect(assetsBtn).toBeInTheDocument();
    expect(screen.queryByTestId("header-share-btn")).not.toBeInTheDocument();
    expect(screen.queryByTestId("header-comments-btn")).not.toBeInTheDocument();
    expect(screen.queryByTestId("header-overleaf-btn")).not.toBeInTheDocument();

    fireEvent.click(assetsBtn);

    expect(useWritingStore.getState().isAssetModalOpen).toBe(true);
  });
});
