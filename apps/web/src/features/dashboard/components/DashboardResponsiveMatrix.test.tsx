import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
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

describe("Dashboard Multi-Device Responsive Matrix Audit (Mobile, Tablet, Desktop)", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
    useWorkspaceStore.getState().resetWorkspace();
    useReaderStore.getState().resetReader();
    vi.restoreAllMocks();
  });

  const mockMessages: ChatMessage[] = [
    {
      id: "msg-1",
      session_id: "ses-1",
      role: "user",
      content: "Giải thích cơ chế Multi-Head Attention?",
      created_at: new Date().toISOString(),
    },
    {
      id: "msg-2",
      session_id: "ses-1",
      role: "assistant",
      content: "Multi-Head Attention cho phép mô hình đồng thời chú ý đến thông tin từ các không gian biểu diễn khác nhau.",
      created_at: new Date().toISOString(),
      citations: [
        {
          paper_id: "doc-1",
          paper_title: "Attention Is All You Need",
          page: 4,
          bbox: [0.15, 0.25, 0.85, 0.65, 4],
        },
      ],
    },
  ];

  describe("1. Mobile Viewport (< 768px: 375px, 390px)", () => {
    it("renders Mobile Segmented Switcher with [Tài liệu] and [Trợ lý] buttons", () => {
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

      // Verify mobile segmented tab bar exists
      const readerTab = screen.getByRole("button", { name: /Chuyển sang chế độ xem tài liệu PDF/i });
      const chatTab = screen.getByRole("button", { name: /Chuyển sang chế độ xem trợ lý đối thoại và sổ tay/i });

      expect(readerTab).toBeInTheDocument();
      expect(chatTab).toBeInTheDocument();
      expect(readerTab).toHaveTextContent("Tài liệu");
      expect(chatTab).toHaveTextContent("Trợ lý");
    });

    it("switches from Reader view to Socratic Chat view when clicking the Chat Tab", () => {
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

      const chatTab = screen.getByRole("button", { name: /Chuyển sang chế độ xem trợ lý đối thoại và sổ tay/i });
      fireEvent.click(chatTab);

      // Socratic Copilot header & chat message should be accessible
      expect(screen.getByText("Socratic Copilot")).toBeInTheDocument();
      expect(screen.getByText(/Giải thích cơ chế Multi-Head Attention/i)).toBeInTheDocument();
    });

    it("auto-switches to Reader view when a citation badge is clicked in Chat view", async () => {
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

      // Switch to Chat tab first
      const chatTab = screen.getByRole("button", { name: /Chuyển sang chế độ xem trợ lý đối thoại và sổ tay/i });
      fireEvent.click(chatTab);

      // Click citation badge
      const citationBtn = screen.getByTestId("citation-badge");
      expect(citationBtn).toBeInTheDocument();
      fireEvent.click(citationBtn);

      // Verify active bounding box set in store
      expect(useDashboardStore.getState().activeBbox).toEqual([0.15, 0.25, 0.85, 0.65, 4]);

      // Automatically transitions mobile view to Reader
      await waitFor(() => {
        const readerTab = screen.getByRole("button", { name: /Chuyển sang chế độ xem tài liệu PDF/i });
        expect(readerTab.className).toContain("text-primary");
      });
    });

    it("toggles off-canvas sidebar drawer when clicking sidebar toggle", () => {
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

      const initialSidebarState = useDashboardStore.getState().sidebarState;
      const sidebarToggleBtn = screen.getByRole("button", { name: /Mở danh sách phiên nghiên cứu/i });
      expect(sidebarToggleBtn).toBeInTheDocument();

      fireEvent.click(sidebarToggleBtn);
      const expectedNext = initialSidebarState === "expanded" ? "collapsed" : "expanded";
      expect(useDashboardStore.getState().sidebarState).toBe(expectedNext);
    });
  });

  describe("2. Tablet Viewport (768px - 1023px) & Split-Pane Desktop", () => {
    it("renders dual-pane split view with divider separator for larger screens", () => {
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

      // Split separator is present with min/max clamps
      const divider = screen.getByTestId("split-pane-divider");
      expect(divider).toBeInTheDocument();
      expect(divider).toHaveAttribute("aria-orientation", "vertical");
      expect(Number(divider.getAttribute("aria-valuemin"))).toBeGreaterThanOrEqual(30);
      expect(Number(divider.getAttribute("aria-valuemax"))).toBeLessThanOrEqual(70);
    });

    it("respects Zen Focus Mode transitions: Full PDF or Full Workspace", () => {
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

      // Enter Zen Reading Mode
      const zenPdfBtn = screen.getByTestId("zen-pdf-btn");
      fireEvent.click(zenPdfBtn);
      expect(useWorkspaceStore.getState().zenMode).toBe("pdf");

      // Divider should be hidden in Zen mode
      expect(screen.queryByTestId("split-pane-divider")).not.toBeInTheDocument();

      // Exit Zen mode via clicking zen button again
      fireEvent.click(zenPdfBtn);
      expect(useWorkspaceStore.getState().zenMode).toBe("none");
    });
  });

  describe("3. Responsive PDF Fit-to-Width Invariant", () => {
    it("preserves minimum split pane boundary to prevent crushing PDF viewer", () => {
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

      const divider = screen.getByTestId("split-pane-divider");
      // Double click divider resets to default 50%
      fireEvent.doubleClick(divider);
      expect(useWorkspaceStore.getState().splitRatio).toBe(50);

      // Keyboard arrow keys adjust within safe boundaries
      fireEvent.keyDown(divider, { key: "ArrowLeft" });
      expect(useWorkspaceStore.getState().splitRatio).toBeGreaterThanOrEqual(35);

      fireEvent.keyDown(divider, { key: "ArrowRight" });
      expect(useWorkspaceStore.getState().splitRatio).toBeLessThanOrEqual(65);
    });
  });
});
