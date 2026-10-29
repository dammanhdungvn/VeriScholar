import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DraftAssetManagementModal } from "../components/DraftAssetManagementModal";
import { draftsApi } from "../api/draftsApi";
import { useWritingStore } from "../stores/useWritingStore";

vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    listAssets: vi.fn(),
    createAsset: vi.fn(),
  },
}));

describe("DraftAssetManagementModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useWritingStore.getState().reset();
    useWritingStore.setState({ activeDraftId: "test-draft-123" });
  });

  it("renders dropzone with multiple attribute on file input and no redundant empty state box when empty", async () => {
    vi.mocked(draftsApi.listAssets).mockResolvedValue({
      draft_id: "test-draft-123",
      items: [],
      total: 0,
    });

    render(<DraftAssetManagementModal isOpen={true} onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByTestId("asset-dropzone")).toBeInTheDocument();
    });

    const fileInput = screen.getByTestId("asset-file-input") as HTMLInputElement;
    expect(fileInput).toBeInTheDocument();
    expect(fileInput.multiple).toBe(true);

    // Verify redundant bulky empty box is removed
    expect(screen.queryByText(/Chưa có asset nào trong bản thảo/i)).toBeNull();
  });

  it("supports batch uploading multiple files concurrently", async () => {
    vi.mocked(draftsApi.listAssets).mockResolvedValue({
      draft_id: "test-draft-123",
      items: [],
      total: 0,
    });

    vi.mocked(draftsApi.createAsset).mockImplementation(async (_draftId, payload) => ({
      id: `asset-${payload.filename}`,
      draft_id: "test-draft-123",
      asset_type: payload.asset_type || "image",
      filename: payload.filename,
      file_size_bytes: 512,
      storage_url: `/assets/${payload.filename}`,
      caption: payload.caption,
      latex_label: payload.latex_label,
      created_at: "2026-10-29T00:00:00Z",
    }));

    render(<DraftAssetManagementModal isOpen={true} onClose={vi.fn()} />);

    const fileInput = screen.getByTestId("asset-file-input");

    const file1 = new File(["dummy content 1"], "fig1.png", { type: "image/png" });
    const file2 = new File(["dummy content 2"], "fig2.jpg", { type: "image/jpeg" });

    fireEvent.change(fileInput, { target: { files: [file1, file2] } });

    await waitFor(() => {
      expect(draftsApi.createAsset).toHaveBeenCalledTimes(2);
    });

    expect(await screen.findByText("fig1.png")).toBeInTheDocument();
    expect(await screen.findByText("fig2.jpg")).toBeInTheDocument();
  });
});
