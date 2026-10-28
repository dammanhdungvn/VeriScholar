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

    expect(screen.getByRole("heading", { name: "Workspace" })).toBeInTheDocument();
    expect(screen.getByText(/Tìm bài báo/i)).toBeInTheDocument();
    expect(screen.getByText(/Nghiên cứu/i)).toBeInTheDocument();
    expect(screen.getByText(/Attention Mechanism/i)).toBeInTheDocument();
    // Standalone dropzone is removed (Rule Item 9)
    expect(screen.queryByText(/Kéo thả tệp PDF bài báo vào đây/i)).not.toBeInTheDocument();
    expect(screen.queryByTestId("toggle-reasoning-btn")).not.toBeInTheDocument();
  });

  it("renders workspace logo horizontally aligned with the Workspace title", () => {
    const { container } = render(
      <UnifiedHeroWorkspace
        inputText=""
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={vi.fn()}
      />
    );
    const titleContainer = container.querySelector(".workspace-header-title");
    expect(titleContainer).not.toBeNull();
    expect(titleContainer).toHaveClass("flex-row");
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

    const chatModeBtn = screen.getByText(/Nghiên cứu/i);
    fireEvent.click(chatModeBtn);

    expect(
      screen.getByPlaceholderText(/Đặt câu hỏi nghiên cứu, kéo thả PDF hoặc yêu cầu tóm tắt/i)
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

  it("renders search results inside horizontal snap carousel track with scrollbar-none and card dimensions", async () => {
    vi.spyOn(discoveryApi, "search").mockResolvedValue([
      {
        title: "Paper 1",
        authors: ["Author 1"],
        publication_year: 2024,
        access_status: "open_access_pdf",
      },
      {
        title: "Paper 2",
        authors: ["Author 2"],
        publication_year: 2024,
        access_status: "open_access_pdf",
      },
    ]);

    render(
      <UnifiedHeroWorkspace
        inputText="Transformer"
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={vi.fn()}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Tìm kiếm bài báo khoa học/i);
    fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

    await waitFor(() => {
      expect(screen.getByTestId("scholarly-carousel-track")).toBeInTheDocument();
    });

    const carouselTrack = screen.getByTestId("scholarly-carousel-track");
    expect(carouselTrack).toHaveClass("overflow-x-auto", "scrollbar-none", "snap-x", "snap-mandatory");

    // Check that cards are wrapped in snap-start items
    const cardItems = screen.getAllByTestId("scholarly-carousel-item");
    expect(cardItems).toHaveLength(2);
    expect(cardItems[0]).toHaveClass("shrink-0", "snap-start");
  });

  it("renders carousel navigation chevrons and triggers smooth scrolling", async () => {
    vi.spyOn(discoveryApi, "search").mockResolvedValue([
      {
        title: "Paper 1",
        authors: ["Author 1"],
        publication_year: 2024,
        access_status: "open_access_pdf",
      },
      {
        title: "Paper 2",
        authors: ["Author 2"],
        publication_year: 2024,
        access_status: "open_access_pdf",
      },
    ]);

    render(
      <UnifiedHeroWorkspace
        inputText="Transformer"
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={vi.fn()}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Tìm kiếm bài báo khoa học/i);
    fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

    await waitFor(() => {
      expect(screen.getByTestId("scholarly-carousel-track")).toBeInTheDocument();
    });

    const carouselTrack = screen.getByTestId("scholarly-carousel-track");
    const scrollByMock = vi.fn();
    carouselTrack.scrollBy = scrollByMock;

    // Simulate track overflow where scrolling right is available
    Object.defineProperty(carouselTrack, "scrollLeft", { configurable: true, value: 0 });
    Object.defineProperty(carouselTrack, "clientWidth", { configurable: true, value: 400 });
    Object.defineProperty(carouselTrack, "scrollWidth", { configurable: true, value: 1200 });

    fireEvent.scroll(carouselTrack);

    await waitFor(() => {
      expect(screen.getByTestId("carousel-next-btn")).toBeInTheDocument();
    });
    expect(screen.queryByTestId("carousel-prev-btn")).not.toBeInTheDocument();

    // Click next button
    fireEvent.click(screen.getByTestId("carousel-next-btn"));
    expect(scrollByMock).toHaveBeenCalledWith({ left: 380, behavior: "smooth" });

    // Now simulate being scrolled to middle where both left and right are available
    Object.defineProperty(carouselTrack, "scrollLeft", { configurable: true, value: 380 });
    fireEvent.scroll(carouselTrack);

    await waitFor(() => {
      expect(screen.getByTestId("carousel-prev-btn")).toBeInTheDocument();
      expect(screen.getByTestId("carousel-next-btn")).toBeInTheDocument();
    });

    // Click prev button
    fireEvent.click(screen.getByTestId("carousel-prev-btn"));
    expect(scrollByMock).toHaveBeenCalledWith({ left: -380, behavior: "smooth" });
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

    const searchInput = screen.getByPlaceholderText(/Tìm kiếm bài báo khoa học/i);
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

    const searchInput = screen.getByPlaceholderText(/Tìm kiếm bài báo khoa học/i);
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

  describe("URL Guardrail & Empty State Handling", () => {
    it("blocks untrusted URL without calling search API and displays polite notice", async () => {
      const searchSpy = vi.spyOn(discoveryApi, "search");

      render(
        <UnifiedHeroWorkspace
          inputText="https://pornhub.com/video"
          onChangeText={vi.fn()}
          onSendChat={vi.fn()}
          onIngestFile={vi.fn()}
          onOpenPaper={vi.fn()}
        />
      );

      const searchInput = screen.getByPlaceholderText(/Tìm kiếm bài báo khoa học/i);
      fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

      expect(searchSpy).not.toHaveBeenCalled();
      expect(
        screen.getByText(
          /Hệ thống chỉ hỗ trợ liên kết từ các cổng học thuật uy tín/i
        )
      ).toBeInTheDocument();
    });

    it("extracts identifier from arXiv URL and passes ID to search API", async () => {
      const searchSpy = vi
        .spyOn(discoveryApi, "search")
        .mockResolvedValue([]);

      render(
        <UnifiedHeroWorkspace
          inputText="https://arxiv.org/abs/2305.18290"
          onChangeText={vi.fn()}
          onSendChat={vi.fn()}
          onIngestFile={vi.fn()}
          onOpenPaper={vi.fn()}
        />
      );

      const searchInput = screen.getByPlaceholderText(/Tìm kiếm bài báo khoa học/i);
      fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

      expect(searchSpy).toHaveBeenCalledWith("2305.18290", 8);
    });

    it("extracts identifier from DOI URL and passes DOI to search API", async () => {
      const searchSpy = vi
        .spyOn(discoveryApi, "search")
        .mockResolvedValue([]);

      render(
        <UnifiedHeroWorkspace
          inputText="https://doi.org/10.1145/3805774"
          onChangeText={vi.fn()}
          onSendChat={vi.fn()}
          onIngestFile={vi.fn()}
          onOpenPaper={vi.fn()}
        />
      );

      const searchInput = screen.getByPlaceholderText(/Tìm kiếm bài báo khoa học/i);
      fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

      expect(searchSpy).toHaveBeenCalledWith("10.1145/3805774", 8);
    });

    it("displays empty state with reset button when search returns 0 results and resets on click", async () => {
      vi.spyOn(discoveryApi, "search").mockResolvedValue([]);
      const onChangeText = vi.fn();

      render(
        <UnifiedHeroWorkspace
          inputText="Unknown Query 12345"
          onChangeText={onChangeText}
          onSendChat={vi.fn()}
          onIngestFile={vi.fn()}
          onOpenPaper={vi.fn()}
        />
      );

      const searchInput = screen.getByPlaceholderText(/Tìm kiếm bài báo khoa học/i);
      fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

      await waitFor(() => {
        expect(
          screen.getByText("Không tìm thấy bài báo phù hợp với yêu cầu này.")
        ).toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Làm mới" })).toBeInTheDocument();
      });

      // Click "Làm mới"
      const resetBtn = screen.getByRole("button", { name: "Làm mới" });
      fireEvent.click(resetBtn);

      await waitFor(() => {
        expect(
          screen.queryByText("Không tìm thấy bài báo phù hợp với yêu cầu này.")
        ).not.toBeInTheDocument();
        expect(screen.getByText(/Attention Mechanism/i)).toBeInTheDocument();
      });
      expect(onChangeText).toHaveBeenCalledWith("");
    });
  });
});
