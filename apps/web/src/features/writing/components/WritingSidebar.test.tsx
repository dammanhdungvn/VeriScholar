import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { WritingSidebar } from "./WritingSidebar";
import { useWritingStore } from "../stores/useWritingStore";

describe("WritingSidebar", () => {
  beforeEach(() => {
    useWritingStore.getState().reset();
  });

  it("renders file tree tab with main.tex, collapse button, and action buttons", () => {
    const handleUpload = vi.fn();
    render(<WritingSidebar onUploadAsset={handleUpload} />);

    // File tree tab is active by default
    expect(screen.getByTestId("sidebar-tab-files")).toBeInTheDocument();
    expect(screen.getByTestId("file-main-tex")).toBeInTheDocument();
    const collapseBtn = screen.getByTestId("sidebar-collapse-btn");
    expect(collapseBtn).toBeInTheDocument();

    // Clicking collapse button toggles file tree
    fireEvent.click(collapseBtn);
    expect(useWritingStore.getState().isFileTreeOpen).toBe(false);

    // Toolbar buttons
    expect(screen.getByTestId("sidebar-new-file-btn")).toBeInTheDocument();
    expect(screen.queryByTestId("sidebar-new-folder-btn")).not.toBeInTheDocument();
    const uploadBtn = screen.getByTestId("sidebar-upload-btn");
    expect(uploadBtn).toBeInTheDocument();

    fireEvent.click(uploadBtn);
    expect(handleUpload).toHaveBeenCalledTimes(1);
  });

  it("switches to outline tab and extracts sections from editorContent, triggering onSelectOutlineItem on click", () => {
    const handleSelectOutline = vi.fn();
    useWritingStore
      .getState()
      .setEditorContent(
        "\\section{Giới thiệu}\nNội dung giới thiệu.\n\\subsection{Bối cảnh nghiên cứu}\nChi tiết.\n\\section{Phương pháp}\nMô tả."
      );

    render(<WritingSidebar onSelectOutlineItem={handleSelectOutline} />);

    // Switch to Outline tab
    const outlineTabBtn = screen.getByTestId("sidebar-tab-outline");
    fireEvent.click(outlineTabBtn);

    // Verify parsed sections
    expect(screen.getByText("Giới thiệu")).toBeInTheDocument();
    expect(screen.getByText("Bối cảnh nghiên cứu")).toBeInTheDocument();
    expect(screen.getByText("Phương pháp")).toBeInTheDocument();

    // Click outline item
    const introItem = screen.getByTestId("outline-item-1");
    fireEvent.click(introItem);

    expect(handleSelectOutline).toHaveBeenCalledWith(1, "Giới thiệu");
  });

  it("supports adding a new file via prompt", () => {
    vi.spyOn(window, "prompt").mockReturnValue("appendix.tex");

    render(<WritingSidebar />);

    const newFileBtn = screen.getByTestId("sidebar-new-file-btn");
    fireEvent.click(newFileBtn);

    expect(screen.getByTestId("file-appendix.tex")).toBeInTheDocument();
  });
});
