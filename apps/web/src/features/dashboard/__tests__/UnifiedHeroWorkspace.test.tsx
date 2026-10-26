import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { UnifiedHeroWorkspace } from "../components/UnifiedHeroWorkspace";
import { discoveryApi } from "@/features/discovery/api/discoveryApi";

describe("UnifiedHeroWorkspace Component", () => {
  it("renders centered heading, mode switchers, topic chips, and upload trigger", () => {
    render(
      <UnifiedHeroWorkspace
        inputText=""
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={vi.fn()}
      />
    );

    expect(screen.getByText(/Không gian nghiên cứu/i)).toBeInTheDocument();
    expect(screen.getByText(/Tìm bài báo/i)).toBeInTheDocument();
    expect(screen.getByText(/Đối thoại AI/i)).toBeInTheDocument();
    expect(screen.getByText(/Attention Mechanism/i)).toBeInTheDocument();
    expect(screen.getByText(/Kéo thả tệp PDF/i)).toBeInTheDocument();
    expect(screen.queryByTestId("toggle-reasoning-btn")).not.toBeInTheDocument();
  });

  it("switches to chat mode and renders reasoning control button", () => {
    render(
      <UnifiedHeroWorkspace
        inputText=""
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={vi.fn()}
      />
    );

    const chatModeBtn = screen.getByText(/Đối thoại AI/i);
    fireEvent.click(chatModeBtn);

    expect(
      screen.getByPlaceholderText(/Đặt câu hỏi hoặc yêu cầu phân tích học thuật/i)
    ).toBeInTheDocument();
    expect(screen.getByTestId("toggle-reasoning-btn")).toBeInTheDocument();
  });

  it("executes search when topic chip is clicked and displays result cards", async () => {
    vi.spyOn(discoveryApi, "search").mockResolvedValue([
      {
        title: "Attention Is All You Need",
        authors: ["Vaswani et al."],
        publication_year: 2017,
        venue: "NeurIPS",
        access_status: "open_access_pdf",
        pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
      },
    ]);

    const onOpenPaper = vi.fn();
    render(
      <UnifiedHeroWorkspace
        inputText=""
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={onOpenPaper}
      />
    );

    const chip = screen.getByText(/Attention Mechanism/i);
    fireEvent.click(chip);

    await waitFor(() => {
      expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
      expect(screen.getByText(/Open Access PDF/i)).toBeInTheDocument();
    });

    const openReadingBtn = screen.getByText(/Mở Đọc Sâu/i);
    fireEvent.click(openReadingBtn);

    expect(onOpenPaper).toHaveBeenCalledWith(
      expect.objectContaining({ title: "Attention Is All You Need" })
    );
  });

  it("renders scholarly skeleton list while search is pending and hides dropzone", async () => {
    let resolveSearch: (val: any) => void;
    const searchPromise = new Promise((resolve) => {
      resolveSearch = resolve;
    });
    vi.spyOn(discoveryApi, "search").mockReturnValue(searchPromise as any);

    render(
      <UnifiedHeroWorkspace
        inputText="Attention"
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={vi.fn()}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Nhập tên bài báo/i);
    fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

    // Skeleton list is rendered with data-testid="scholarly-skeleton-list"
    expect(screen.getByTestId("scholarly-skeleton-list")).toBeInTheDocument();
    // Dropzone is hidden while searching
    expect(screen.queryByText(/Kéo thả tệp PDF/i)).not.toBeInTheDocument();

    // Resolve search
    resolveSearch!([
      {
        title: "Attention Is All You Need",
        authors: ["Ashish Vaswani"],
        publication_year: 2017,
        access_status: "open_access_pdf",
      },
    ]);

    await waitFor(() => {
      expect(screen.queryByTestId("scholarly-skeleton-list")).not.toBeInTheDocument();
      expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
    });
  });

  it("toggles between all papers and peer-reviewed papers using the pill filter", async () => {
    vi.spyOn(discoveryApi, "search").mockResolvedValue([
      {
        title: "Paper One (Peer Reviewed)",
        authors: ["Author A"],
        publication_year: 2023,
        access_status: "open_access_pdf",
        is_peer_reviewed: true,
      },
      {
        title: "Paper Two (Preprint)",
        authors: ["Author B"],
        publication_year: 2024,
        access_status: "open_access_pdf",
        is_peer_reviewed: false,
      },
    ]);

    render(
      <UnifiedHeroWorkspace
        inputText="Transformers"
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={vi.fn()}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Nhập tên bài báo/i);
    fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

    await waitFor(() => {
      expect(screen.getByText("Paper One (Peer Reviewed)")).toBeInTheDocument();
      expect(screen.getByText("Paper Two (Preprint)")).toBeInTheDocument();
    });

    // Pill filter buttons
    const peerReviewedBtn = screen.getByTestId("filter-peer-reviewed-btn");
    expect(peerReviewedBtn).toHaveTextContent("Đã bình duyệt (1)");
    const allBtn = screen.getByTestId("filter-all-btn");
    expect(allBtn).toHaveTextContent("Tất cả (2)");

    // Switch to peer-reviewed
    fireEvent.click(peerReviewedBtn);

    expect(screen.getByText("Paper One (Peer Reviewed)")).toBeInTheDocument();
    expect(screen.queryByText("Paper Two (Preprint)")).not.toBeInTheDocument();

    // Switch back to all
    fireEvent.click(allBtn);

    expect(screen.getByText("Paper One (Peer Reviewed)")).toBeInTheDocument();
    expect(screen.getByText("Paper Two (Preprint)")).toBeInTheDocument();
  });
});
