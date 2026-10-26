import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { HeroUploadDropzone } from "../components/HeroUploadDropzone";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";

describe("HeroUploadDropzone Component", () => {
  beforeEach(() => {
    useWorkspaceStore.getState().resetWorkspace();
  });

  it("does not render cancel button when status is idle", () => {
    useWorkspaceStore.setState({ documentStatus: "idle" });
    render(<HeroUploadDropzone onIngest={vi.fn()} />);

    expect(screen.queryByText(/Hủy bỏ/i)).not.toBeInTheDocument();
  });

  it("renders cancel button 'Hủy bỏ' when processing and clicking it resets workspace", () => {
    useWorkspaceStore.setState({
      documentStatus: "parsing",
      uploadProgress: 94,
      statusStage: "Đang xử lý nội dung tài liệu...",
    });

    render(<HeroUploadDropzone onIngest={vi.fn()} />);

    const cancelButton = screen.getByRole("button", { name: /Hủy bỏ/i });
    expect(cancelButton).toBeInTheDocument();

    fireEvent.click(cancelButton);

    const state = useWorkspaceStore.getState();
    expect(state.documentStatus).toBe("idle");
    expect(state.uploadProgress).toBe(0);
    expect(state.statusStage).toBeNull();
  });
});
