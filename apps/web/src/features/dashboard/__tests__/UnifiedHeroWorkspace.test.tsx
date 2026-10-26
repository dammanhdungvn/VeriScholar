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
      expect(screen.getByText(/Có sẵn PDF Open Access/i)).toBeInTheDocument();
    });

    const openReadingBtn = screen.getByText(/Mở Đọc Sâu/i);
    fireEvent.click(openReadingBtn);

    expect(onOpenPaper).toHaveBeenCalledWith(
      expect.objectContaining({ title: "Attention Is All You Need" })
    );
  });
});
