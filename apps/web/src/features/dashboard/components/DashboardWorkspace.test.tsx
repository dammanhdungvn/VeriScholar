import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardWorkspace } from "./DashboardWorkspace";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import type { ChatMessage } from "@/types/dashboard";

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  );
}

describe("DashboardWorkspace Split-Pane Component", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
    useWorkspaceStore.getState().resetWorkspace();
    useReaderStore.getState().resetReader();
  });

  const mockMessages: ChatMessage[] = [
    {
      id: "msg-1",
      session_id: "ses-1",
      role: "user",
      content: "Giải thích cơ chế Positional Encoding trong bài báo này?",
      created_at: new Date().toISOString(),
    },
    {
      id: "msg-2",
      session_id: "ses-1",
      role: "assistant",
      content: "Positional Encoding sử dụng các hàm lượng giác sin và cos để mã hóa vị trí.",
      created_at: new Date().toISOString(),
    },
  ];

  it("renders Split-Pane layout with Left PDF Canvas and Right Socratic Copilot Chat", () => {
    useWorkspaceStore.getState().setDocument("doc-1", "Attention Is All You Need");

    renderWithClient(
      <DashboardWorkspace
        messages={mockMessages}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    // Left Pane Document Header & Canvas
    expect(screen.getAllByText(/Attention Is All You Need/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Trang 1/i).length).toBeGreaterThan(0);

    // Right Pane Socratic Copilot
    expect(screen.getByText(/Socratic Copilot/i)).toBeInTheDocument();

    // Messages displayed
    expect(
      screen.getByText(/Giải thích cơ chế Positional Encoding trong bài báo này/i)
    ).toBeInTheDocument();

    // Bottom-docked Chat Input Box is present
    expect(
      screen.getByPlaceholderText(/Tôi có thể giúp gì/i)
    ).toBeInTheDocument();
  });

  it("renders short prompt suggestions when chat is empty and triggers onSend on click", () => {
    const handleSend = vi.fn();

    renderWithClient(
      <DashboardWorkspace
        messages={[]}
        inputText=""
        onChangeText={vi.fn()}
        onSend={handleSend}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    // Gợi ý prompt ngắn
    const summaryChips = screen.getAllByText("Tóm tắt paper");
    expect(summaryChips.length).toBeGreaterThanOrEqual(1);
    const summaryChip = summaryChips[0];
    expect(summaryChip).toBeInTheDocument();
    expect(screen.getAllByText("Đóng góp chính")[0]).toBeInTheDocument();
    expect(screen.getAllByText("Phương pháp & Kiến trúc")[0]).toBeInTheDocument();
    expect(screen.getAllByText("Hạn chế & Thách thức")[0]).toBeInTheDocument();

    // Không tự động render card 3 luận điểm cốt lõi trong tab chat
    expect(screen.queryByText(/3 Luận Điểm Cốt Lõi/i)).not.toBeInTheDocument();

    // Click gửi prompt cho AI
    fireEvent.click(summaryChip);
    expect(handleSend).toHaveBeenCalledWith(
      expect.stringContaining("tóm tắt ngắn gọn và toàn diện")
    );
  });

  it("renders dynamic Grounded Bounding Box highlight overlay when activeBbox is set", () => {
    useDashboardStore.getState().setActiveBbox([0.15, 0.62, 0.85, 0.88, 6]);

    renderWithClient(
      <DashboardWorkspace
        messages={[]}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    const overlay = screen.getByTestId("grounded-bbox-overlay");
    expect(overlay).toBeInTheDocument();
    expect(overlay.textContent).toBe("");
  });

  it("calls onSend when user types and submits in the bottom-docked chat input", () => {
    const handleSend = vi.fn();
    const handleChangeText = vi.fn();

    renderWithClient(
      <DashboardWorkspace
        messages={mockMessages}
        inputText="Câu hỏi kiểm thử"
        onChangeText={handleChangeText}
        onSend={handleSend}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    const sendBtn = screen.getByLabelText("Gửi câu hỏi");
    fireEvent.click(sendBtn);

    expect(handleSend).toHaveBeenCalled();
  });

  it("allows switching tabs between Chat, Notes, Summary, Structure, and References", () => {
    renderWithClient(
      <DashboardWorkspace
        messages={mockMessages}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    // Switch to Notes tab
    const notesTabBtn = screen.getByRole("tab", { name: /Sổ tay/i });
    fireEvent.click(notesTabBtn);
    expect(useWorkspaceStore.getState().activeRightTab).toBe("notes");

    // Switch to Summary tab
    const summaryTabBtn = screen.getByRole("tab", { name: /Tóm tắt/i });
    fireEvent.click(summaryTabBtn);
    expect(useWorkspaceStore.getState().activeRightTab).toBe("summary");

    // Switch to Structure tab
    const structureTabBtn = screen.getByRole("tab", { name: /Mục lục/i });
    fireEvent.click(structureTabBtn);
    expect(useWorkspaceStore.getState().activeRightTab).toBe("structure");

    // Switch to References tab
    const refsTabBtn = screen.getByRole("tab", { name: /Tham khảo/i });
    fireEvent.click(refsTabBtn);
    expect(useWorkspaceStore.getState().activeRightTab).toBe("references");
  });

  it("opens academic context menu on right click and intercepts default event", () => {
    const handleResetChat = vi.fn();
    renderWithClient(
      <DashboardWorkspace
        messages={mockMessages}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={handleResetChat}
      />
    );

    // Initial state: context menu is not visible
    expect(screen.queryByTestId("academic-context-menu")).not.toBeInTheDocument();

    // Trigger right click (contextmenu) on the right pane
    const rightPane = screen.getByRole("tablist", { name: /Các khung tính năng học thuật/i }).closest("section");
    expect(rightPane).toBeInTheDocument();

    fireEvent.contextMenu(rightPane!, { clientX: 400, clientY: 300 });

    // Academic context menu should now be visible with safe options
    const contextMenu = screen.getByTestId("academic-context-menu");
    expect(contextMenu).toBeInTheDocument();
    expect(screen.getByText("Làm mới hội thoại")).toBeInTheDocument();
    expect(screen.queryByText(/Xuất gói nghiên cứu/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Cài đặt phiên nghiên cứu/i)).toBeInTheDocument();

    // Clicking "Làm mới hội thoại" triggers onResetChat and closes menu
    fireEvent.click(screen.getByText("Làm mới hội thoại"));
    expect(handleResetChat).toHaveBeenCalled();
    expect(screen.queryByTestId("academic-context-menu")).not.toBeInTheDocument();
  });

  it("renders Resizable Split-Pane draggable divider and allows keyboard/double-click resizing", () => {
    useWorkspaceStore.getState().setSplitRatio(60);

    renderWithClient(
      <DashboardWorkspace
        messages={mockMessages}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    const divider = screen.getByTestId("split-pane-divider");
    expect(divider).toBeInTheDocument();
    expect(divider).toHaveAttribute("role", "separator");
    expect(divider).toHaveAttribute("aria-valuenow", "60");

    // Double-click resets to 50%
    fireEvent.doubleClick(divider);
    expect(useWorkspaceStore.getState().splitRatio).toBe(50);

    // Arrow keys adjust ratio
    fireEvent.keyDown(divider, { key: "ArrowLeft" });
    expect(useWorkspaceStore.getState().splitRatio).toBe(48);

    fireEvent.keyDown(divider, { key: "ArrowRight" });
    expect(useWorkspaceStore.getState().splitRatio).toBe(50);
  });

  it("handles Zen reading modes (Hide Chatbot / Hide PDF) and restores with Escape or exit pill", () => {
    renderWithClient(
      <DashboardWorkspace
        messages={mockMessages}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    // Initial state: Zen mode none, divider visible
    expect(useWorkspaceStore.getState().zenMode).toBe("none");
    expect(screen.getByTestId("split-pane-divider")).toBeInTheDocument();
    expect(screen.queryByTestId("zen-exit-pill")).not.toBeInTheDocument();

    // 1. Toggle Zen PDF mode (Hide Chatbot)
    const zenPdfBtn = screen.getByTestId("zen-pdf-btn");
    fireEvent.click(zenPdfBtn);
    expect(useWorkspaceStore.getState().zenMode).toBe("pdf");
    expect(screen.queryByTestId("split-pane-divider")).not.toBeInTheDocument();

    // Floating exit pill is visible
    const exitPill = screen.getByTestId("zen-exit-pill");
    expect(exitPill).toBeInTheDocument();
    expect(exitPill).toHaveTextContent(/Khôi phục chia đôi/i);

    // Click exit pill restores split-pane
    fireEvent.click(exitPill);
    expect(useWorkspaceStore.getState().zenMode).toBe("none");

    // 2. Toggle Zen Chat mode (Hide PDF)
    const zenChatBtn = screen.getByTestId("zen-chat-btn");
    fireEvent.click(zenChatBtn);
    expect(useWorkspaceStore.getState().zenMode).toBe("workspace");

    // Pressing Escape restores split-pane
    fireEvent.keyDown(window, { key: "Escape" });
    expect(useWorkspaceStore.getState().zenMode).toBe("none");
  });

  it("displays Context Chip above chat input and formats prompt on send", () => {
    const handleSend = vi.fn();
    const handleChangeText = vi.fn();

    useWorkspaceStore.getState().setActiveContextChip({
      text: "The Transformer is the first transduction model relying entirely on self-attention",
      pageNumber: 1,
      documentTitle: "Attention Is All You Need",
    });

    renderWithClient(
      <DashboardWorkspace
        messages={mockMessages}
        inputText="Giải thích ý chính"
        onChangeText={handleChangeText}
        onSend={handleSend}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    // Context Chip is rendered
    const chip = screen.getByTestId("context-chip");
    expect(chip).toBeInTheDocument();
    expect(screen.getByText(/Attention Is All You Need • Tr\. 1/i)).toBeInTheDocument();
    expect(screen.getByText(/The Transformer is the first transduction model/i)).toBeInTheDocument();

    // Submit sends formatted quote
    const sendBtn = screen.getByLabelText("Gửi câu hỏi");
    fireEvent.click(sendBtn);

    expect(handleSend).toHaveBeenCalledWith(
      expect.stringContaining('📎 [Attention Is All You Need - Trang 1]: "The Transformer is the first transduction model relying entirely on self-attention"')
    );
    expect(handleSend).toHaveBeenCalledWith(
      expect.stringContaining("Giải thích ý chính")
    );

    // Chip is cleared
    expect(useWorkspaceStore.getState().activeContextChip).toBeNull();
  });

  it("renders reasoning accordion with BrainCircuit and citation badges in chat stream", () => {
    const messageWithThoughtAndCitation: ChatMessage = {
      id: "msg-thought-cite",
      session_id: "ses-1",
      role: "assistant",
      content: "Đoạn trích dẫn này nằm tại trang 5.",
      thought: "Suy luận logic và tham chiếu tọa độ văn bản...",
      is_streaming: false,
      created_at: new Date().toISOString(),
      citations: [
        {
          paper_id: "doc-1",
          paper_title: "Attention Is All You Need",
          page: 5,
          bbox: [0.2, 0.3, 0.8, 0.7, 5],
        },
      ],
    };

    renderWithClient(
      <DashboardWorkspace
        messages={[messageWithThoughtAndCitation]}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    // Reasoning accordion is present
    expect(screen.getByTestId("reasoning-accordion")).toBeInTheDocument();
    expect(screen.getByText("Suy luận học thuật")).toBeInTheDocument();
    expect(
      screen.getByText("Suy luận logic và tham chiếu tọa độ văn bản...")
    ).toBeInTheDocument();

    // Citation badge is present
    const citationBtn = screen.getByTestId("citation-badge");
    expect(citationBtn).toBeInTheDocument();
    expect(screen.getByText("Tr.5")).toBeInTheDocument();

    // Click citation badge: focuses on bounding box without popping up reference drawer
    fireEvent.click(citationBtn);
    expect(useDashboardStore.getState().activeBbox).toEqual([0.2, 0.3, 0.8, 0.7, 5]);
    expect(screen.queryByTestId("smart-reference-drawer")).not.toBeInTheDocument();
  });

  it("renders smooth empty state for Paper Viewer and Chat AI when no document is loaded", () => {
    renderWithClient(
      <DashboardWorkspace
        messages={[]}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
        onResetChat={vi.fn()}
      />
    );

    // Left Pane Paper Viewer: shows graceful empty state rather than infinite loading skeleton
    expect(screen.getByText("Chưa có tài liệu nghiên cứu nào")).toBeInTheDocument();
    expect(screen.getByText(/Tải lên tệp PDF bài báo khoa học/i)).toBeInTheDocument();

    // Right Pane Chat AI: shows smooth Socratic onboarding empty state
    expect(screen.getByTestId("chat-empty-state")).toBeInTheDocument();
    expect(screen.getByText("Socratic Copilot sẵn sàng đối thoại")).toBeInTheDocument();
    expect(screen.getByText(/Chưa có tài liệu nghiên cứu nào được nạp/i)).toBeInTheDocument();
  });
});
