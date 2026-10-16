import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { DraftAssetManagementModal } from "./DraftAssetManagementModal";
import { generateLatexSnippet, formatBytes } from "../lib/assetUtils";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import type { DraftAsset } from "../types";

vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    listAssets: vi.fn(),
    createAsset: vi.fn(),
  },
}));

describe("DraftAssetManagementModal", () => {
  const mockAssets: DraftAsset[] = [
    {
      id: "asset-1",
      draft_id: "draft-100",
      asset_type: "image",
      filename: "architecture.png",
      file_size_bytes: 204800,
      storage_url: "/files/architecture.png",
      caption: "Kiến trúc mô hình Transformer",
      latex_label: "fig:transformer_arch",
      created_at: "2026-10-15T08:00:00Z",
    },
    {
      id: "asset-2",
      draft_id: "draft-100",
      asset_type: "bibtex",
      filename: "references.bib",
      file_size_bytes: 4096,
      storage_url: "/files/references.bib",
      caption: null,
      latex_label: null,
      created_at: "2026-10-15T08:05:00Z",
    },
    {
      id: "asset-3",
      draft_id: "draft-100",
      asset_type: "supplementary",
      filename: "custom_style.sty",
      file_size_bytes: 8192,
      storage_url: "/files/custom_style.sty",
      caption: null,
      latex_label: null,
      created_at: "2026-10-15T08:10:00Z",
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    useWritingStore.getState().reset();
    useWritingStore.getState().setDraft({
      id: "draft-100",
      user_id: "user-1",
      title: "Draft 100",
      content: "\\section{Intro}\nInitial content\n",
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });
    vi.mocked(draftsApi.listAssets).mockResolvedValue({
      draft_id: "draft-100",
      items: mockAssets,
      total: 3,
    });
  });

  it("formats bytes accurately", () => {
    expect(formatBytes(0)).toBe("0 B");
    expect(formatBytes(1024)).toBe("1 KB");
    expect(formatBytes(1048576)).toBe("1 MB");
  });

  it("generates correct LaTeX snippets for different asset types", () => {
    const imgSnippet = generateLatexSnippet(mockAssets[0]);
    expect(imgSnippet).toContain("\\begin{figure}");
    expect(imgSnippet).toContain("architecture.png");
    expect(imgSnippet).toContain("fig:transformer_arch");

    const bibSnippet = generateLatexSnippet(mockAssets[1]);
    expect(bibSnippet).toContain("\\bibliography{references}");

    const stySnippet = generateLatexSnippet(mockAssets[2]);
    expect(stySnippet).toContain("\\usepackage{custom_style}");
  });

  it("does not render when isOpen is false", () => {
    render(<DraftAssetManagementModal isOpen={false} />);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("renders modal and fetches asset list on open", async () => {
    render(<DraftAssetManagementModal isOpen={true} draftId="draft-100" />);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(
      screen.getByText(/Quản lý Assets Học Thuật/i)
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(draftsApi.listAssets).toHaveBeenCalledWith("draft-100");
    });

    expect(screen.getByText("architecture.png")).toBeInTheDocument();
    expect(screen.getByText("references.bib")).toBeInTheDocument();
    expect(screen.getByText("custom_style.sty")).toBeInTheDocument();
  });

  it("copies LaTeX snippet to clipboard when clicking copy button", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
      },
    });

    render(<DraftAssetManagementModal isOpen={true} draftId="draft-100" />);

    await waitFor(() => {
      expect(screen.getByText("architecture.png")).toBeInTheDocument();
    });

    const copyButtons = screen.getAllByTestId("copy-latex-btn");
    fireEvent.click(copyButtons[0]);

    expect(writeTextMock).toHaveBeenCalledTimes(1);
    expect(writeTextMock.mock.calls[0][0]).toContain("\\begin{figure}");
    expect(screen.getByText("Đã sao chép")).toBeInTheDocument();
  });

  it("inserts LaTeX snippet into editor content when clicking insert button", async () => {
    render(<DraftAssetManagementModal isOpen={true} draftId="draft-100" />);

    await waitFor(() => {
      expect(screen.getByText("architecture.png")).toBeInTheDocument();
    });

    const insertButtons = screen.getAllByTestId("insert-editor-btn");
    fireEvent.click(insertButtons[0]);

    const updatedContent = useWritingStore.getState().editorContent;
    expect(updatedContent).toContain("\\begin{figure}");
    expect(updatedContent).toContain("architecture.png");
  });

  it("filters assets by category", async () => {
    render(<DraftAssetManagementModal isOpen={true} draftId="draft-100" />);

    await waitFor(() => {
      expect(screen.getByText("architecture.png")).toBeInTheDocument();
    });

    // Filter to images
    const imgTab = screen.getByRole("button", { name: /Hình ảnh/i });
    fireEvent.click(imgTab);

    expect(screen.getByText("architecture.png")).toBeInTheDocument();
    expect(screen.queryByText("references.bib")).toBeNull();

    // Filter to bibtex
    const bibTab = screen.getByRole("button", { name: /Trích dẫn/i });
    fireEvent.click(bibTab);

    expect(screen.queryByText("architecture.png")).toBeNull();
    expect(screen.getByText("references.bib")).toBeInTheDocument();
  });

  it("handles file drop upload", async () => {
    const newAsset: DraftAsset = {
      id: "asset-new",
      draft_id: "draft-100",
      asset_type: "image",
      filename: "figure2.png",
      file_size_bytes: 10240,
      storage_url: "/files/figure2.png",
      caption: "Biểu đồ figure2.png",
      latex_label: "fig:figure2",
      created_at: "2026-10-15T09:00:00Z",
    };

    vi.mocked(draftsApi.createAsset).mockResolvedValue(newAsset);

    render(<DraftAssetManagementModal isOpen={true} draftId="draft-100" />);

    const dropzone = screen.getByTestId("asset-dropzone");
    const file = new File(["dummy png content"], "figure2.png", {
      type: "image/png",
    });

    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [file],
      },
    });

    await waitFor(() => {
      expect(draftsApi.createAsset).toHaveBeenCalledWith(
        "draft-100",
        expect.objectContaining({
          filename: "figure2.png",
          asset_type: "image",
        })
      );
    });

    expect(screen.getByText("figure2.png")).toBeInTheDocument();
  });
});
