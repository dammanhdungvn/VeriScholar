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

  it("renders Grounded 3-Point Summary Card when summary data is available", () => {
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

    // 3 Luận điểm cốt lõi
    expect(screen.getByText(/3 Luận Điểm Cốt Lõi/i)).toBeInTheDocument();
    expect(screen.getByText(/Vấn đề nghiên cứu/i)).toBeInTheDocument();
    expect(screen.getByText(/Đóng góp chính/i)).toBeInTheDocument();
    expect(screen.getByText(/Hạn chế & Hướng phát triển/i)).toBeInTheDocument();
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
    expect(overlay).toHaveTextContent(/Tr. 6/i);
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
    expect(screen.getByText(/Xuất gói nghiên cứu/i)).toBeInTheDocument();
    expect(screen.getByText(/Cài đặt phiên nghiên cứu/i)).toBeInTheDocument();

    // Clicking "Làm mới hội thoại" triggers onResetChat and closes menu
    fireEvent.click(screen.getByText("Làm mới hội thoại"));
    expect(handleResetChat).toHaveBeenCalled();
    expect(screen.queryByTestId("academic-context-menu")).not.toBeInTheDocument();
  });
});
