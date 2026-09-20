import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { HeroUploadDropzone } from "./HeroUploadDropzone";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";

describe("HeroUploadDropzone Component", () => {
  beforeEach(() => {
    useWorkspaceStore.getState().resetWorkspace();
  });

  it("renders Hero Dropzone with concise title and subtitle", () => {
    const handleIngest = vi.fn();
    render(<HeroUploadDropzone onIngest={handleIngest} />);

    expect(
      screen.getByRole("heading", { name: /Tải lên bài báo/i })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Kéo thả hoặc chọn tệp PDF/i)
    ).toBeInTheDocument();
    expect(screen.queryByText(/PDF • Tối đa 50MB/i)).not.toBeInTheDocument();

    // Sample papers are removed
    expect(screen.queryByText(/Attention Is All You Need/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Deep Residual Learning/i)).not.toBeInTheDocument();
  });

  it("displays progress bar and stages when ingestion is active", () => {
    useWorkspaceStore.getState().setStatus("parsing", 65, "Đang phân tích layout 2 cột...");
    render(<HeroUploadDropzone onIngest={vi.fn()} />);

    expect(screen.getByText(/Đang phân tích layout 2 cột/i)).toBeInTheDocument();
    expect(screen.getByText("65%")).toBeInTheDocument();
  });

  it("displays error banner when ingestion error occurs", () => {
    useWorkspaceStore
      .getState()
      .setError("Tệp tải lên không có cấu trúc bài báo nghiên cứu khoa học.");
    render(<HeroUploadDropzone onIngest={vi.fn()} />);

    expect(
      screen.getByText(/Tệp tải lên không có cấu trúc bài báo nghiên cứu khoa học/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Thử lại/i })).toBeInTheDocument();
  });

  it("triggers onIngest when a valid PDF file is selected", () => {
    const handleIngest = vi.fn();
    render(<HeroUploadDropzone onIngest={handleIngest} />);

    const input = screen.getByTestId("hero-file-input") as HTMLInputElement;
    const file = new File(["%PDF-1.5 test"], "attention.pdf", { type: "application/pdf" });

    fireEvent.change(input, { target: { files: [file] } });
    expect(handleIngest).toHaveBeenCalledWith(file);
  });
});
