import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import * as React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardWorkspace } from "./DashboardWorkspace";
import { DashboardChatStreamView } from "./DashboardChatStreamView";
import { DashboardErrorBoundary } from "@/components/ui/DashboardErrorBoundary";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { ApiError } from "@/lib/api-client";
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

describe("E2E User Flow & Edge Cases Verification", () => {
  const originalConsoleError = console.error;

  beforeEach(() => {
    console.error = vi.fn();
    useDashboardStore.getState().reset();
    useWorkspaceStore.getState().resetWorkspace();
    useReaderStore.getState().resetReader();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  /* ========================================================================= */
  /* LUỒNG 1: Tương tác chat streaming & Accordion Suy luận (BrainCircuit)      */
  /* ========================================================================= */
  describe("Luồng 1: Socratic Chat Streaming & Collapsible Reasoning Tokens", () => {
    it("displays pulsing 'Đang tư duy...', BrainCircuit emblem, and auto-expands reasoning accordion during streaming", () => {
      const streamingMessage: ChatMessage = {
        id: "msg-stream-reasoning",
        session_id: "s1",
        role: "assistant",
        content: "",
        thought: "Đang phân tích cấu trúc Attention nhiều đầu và đối chiếu công thức ma trận Q, K, V...",
        is_streaming: true,
        created_at: new Date().toISOString(),
      };

      renderWithClient(
        <DashboardWorkspace
          messages={[streamingMessage]}
          inputText=""
          onChangeText={vi.fn()}
          onSend={vi.fn()}
          isGenerating={true}
          onStopGeneration={vi.fn()}
          onResetChat={vi.fn()}
        />
      );

      // Verify Socratic streaming indicator
      expect(screen.getByText("Đang suy luận...")).toBeInTheDocument();

      // Verify Thought Accordion elements
      const accordion = screen.getByTestId("reasoning-accordion") as HTMLDetailsElement;
      expect(accordion).toBeInTheDocument();
      // Auto-expanded because message is streaming and has no content yet
      expect(accordion.open).toBe(true);

      // Verify BrainCircuit label and pulsing status
      expect(screen.getByText("Suy luận học thuật")).toBeInTheDocument();
      const thinkingIndicator = screen.getByText("Đang tư duy...");
      expect(thinkingIndicator).toBeInTheDocument();
      expect(thinkingIndicator.className).toContain("animate-pulse");

      // Verify thinking tokens content
      expect(
        screen.getByText(
          "Đang phân tích cấu trúc Attention nhiều đầu và đối chiếu công thức ma trận Q, K, V..."
        )
      ).toBeInTheDocument();
    });

    it("transitions gracefully when streaming completes with answer content", () => {
      const completedMessage: ChatMessage = {
        id: "msg-completed-reasoning",
        session_id: "s1",
        role: "assistant",
        content: "Cơ chế Self-Attention cho phép mô hình tính toán trọng số quan hệ trực tiếp.",
        thought: "Hoàn tất đối chiếu trích dẫn trang 4.",
        is_streaming: false,
        created_at: new Date().toISOString(),
      };

      renderWithClient(
        <DashboardWorkspace
          messages={[completedMessage]}
          inputText=""
          onChangeText={vi.fn()}
          onSend={vi.fn()}
          isGenerating={false}
          onStopGeneration={vi.fn()}
          onResetChat={vi.fn()}
        />
      );

      // Pulsing indicator is gone
      expect(screen.queryByText("Đang tư duy...")).not.toBeInTheDocument();
      expect(screen.queryByText("Đang suy luận...")).not.toBeInTheDocument();

      // Accordion is closed by default once content is present
      const accordion = screen.getByTestId("reasoning-accordion") as HTMLDetailsElement;
      expect(accordion.open).toBe(false);

      // Content is rendered
      expect(
        screen.getByText("Cơ chế Self-Attention cho phép mô hình tính toán trọng số quan hệ trực tiếp.")
      ).toBeInTheDocument();
    });
  });

  /* ========================================================================= */
  /* LUỒNG 2: SmartReferenceDrawer & Bounding Box Canvas Activation             */
  /* ========================================================================= */
  describe("Luồng 2: Smart Reference Drawer & Grounded Bounding Box", () => {
    it("opens SmartReferenceDrawer and projects Bounding Box on canvas when citation is clicked", () => {
      const messageWithCitation: ChatMessage = {
        id: "msg-cite-1",
        session_id: "s1",
        role: "assistant",
        content: "Mô hình Transformer được giới thiệu năm 2017.",
        created_at: new Date().toISOString(),
        citations: [
          {
            paper_id: "doc-vaswani-2017",
            paper_title: "Attention Is All You Need",
            page: 4,
            bbox: [0.15, 0.25, 0.75, 0.65, 4],
          },
        ],
      };

      renderWithClient(
        <DashboardWorkspace
          messages={[messageWithCitation]}
          inputText=""
          onChangeText={vi.fn()}
          onSend={vi.fn()}
          isGenerating={false}
          onStopGeneration={vi.fn()}
          onResetChat={vi.fn()}
        />
      );

      // 1. Initial State: activeBbox is null, drawer not open
      expect(useDashboardStore.getState().activeBbox).toBeNull();
      expect(screen.queryByTestId("grounded-bbox-overlay")).not.toBeInTheDocument();
      expect(screen.queryByTestId("smart-reference-drawer")).not.toBeInTheDocument();

      // 2. Click Citation Badge
      const citationBadge = screen.getByTestId("citation-badge");
      expect(citationBadge).toBeInTheDocument();
      expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
      expect(screen.getByText("Tr.4")).toBeInTheDocument();

      fireEvent.click(citationBadge);

      // 3. Verify Active Bounding Box in store & projected on canvas
      expect(useDashboardStore.getState().activeBbox).toEqual([0.15, 0.25, 0.75, 0.65, 4]);

      const bboxOverlay = screen.getByTestId("grounded-bbox-overlay");
      expect(bboxOverlay).toBeInTheDocument();
      expect(screen.getByText("Dẫn chứng • Tr. 4")).toBeInTheDocument();

      // 4. Verify SmartReferenceDrawer is opened
      const drawer = screen.getByTestId("smart-reference-drawer");
      expect(drawer).toBeInTheDocument();
      expect(screen.getByText(/Tài liệu Tham khảo & Đọc Sâu \(PRD §3\.3\)/i)).toBeInTheDocument();

      // 5. Close drawer via close button
      const closeBtn = screen.getByTestId("close-drawer-btn");
      fireEvent.click(closeBtn);
      expect(screen.queryByTestId("smart-reference-drawer")).not.toBeInTheDocument();
    });

    it("allows DashboardChatStreamView to trigger onOpenReferences when citation is clicked", () => {
      const handleOpenReferences = vi.fn();
      const messageWithCitation: ChatMessage = {
        id: "msg-stream-cite",
        session_id: "s1",
        role: "assistant",
        content: "Tham khảo cơ chế Attention.",
        created_at: new Date().toISOString(),
        citations: [
          {
            paper_id: "p1",
            paper_title: "Attention Is All You Need",
            page: 2,
            bbox: [0.1, 0.1, 0.8, 0.8, 2],
          },
        ],
      };

      render(
        <DashboardChatStreamView
          messages={[messageWithCitation]}
          inputText=""
          onChangeText={vi.fn()}
          onSend={vi.fn()}
          isGenerating={false}
          onStopGeneration={vi.fn()}
          onOpenReferences={handleOpenReferences}
        />
      );

      const citationBadge = screen.getByTestId("citation-badge");
      fireEvent.click(citationBadge);

      expect(useDashboardStore.getState().activeBbox).toEqual([0.1, 0.1, 0.8, 0.8, 2]);
      expect(handleOpenReferences).toHaveBeenCalledTimes(1);
    });
  });

  /* ========================================================================= */
  /* LUỒNG 3: Giả lập lỗi mạng/500 & DashboardErrorBoundary                    */
  /* ========================================================================= */
  describe("Luồng 3: Error Boundary & Error Code Copying (REQ-XXXX-YYYY)", () => {
    it("catches simulated 500 error, displays formatted REQ-XXXX-YYYY code, and copies to clipboard", () => {
      const writeTextMock = vi.fn().mockResolvedValue(undefined);
      Object.assign(navigator, {
        clipboard: {
          writeText: writeTextMock,
        },
      });

      function FailingWorkspace(): React.ReactNode {
        throw new ApiError(
          "Máy chủ gặp sự cố nội bộ khi khởi tạo phiên làm việc",
          "INTERNAL_SERVER_ERROR",
          null,
          null,
          500,
          "REQ-7A9B-4C2D"
        );
      }

      render(
        <DashboardErrorBoundary>
          <FailingWorkspace />
        </DashboardErrorBoundary>
      );

      // Verify Error Boundary renders alert UI
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText("Đã xảy ra lỗi không gian làm việc")).toBeInTheDocument();
      expect(
        screen.getByText("Máy chủ gặp sự cố nội bộ khi khởi tạo phiên làm việc")
      ).toBeInTheDocument();

      // Verify formatted error lookup code REQ-XXXX-YYYY
      expect(screen.getByText(/Mã tra cứu:/i)).toBeInTheDocument();
      expect(screen.getByText("REQ-7A9B-4C2D")).toBeInTheDocument();

      // Copy error code button
      const copyBtn = screen.getByTitle(/Sao chép mã lỗi để gửi kỹ thuật viên/i);
      expect(copyBtn).toBeInTheDocument();

      fireEvent.click(copyBtn);

      // Verify clipboard call
      expect(writeTextMock).toHaveBeenCalledWith("REQ-7A9B-4C2D");

      // Verify user feedback "Đã chép!"
      expect(screen.getByText("Đã chép!")).toBeInTheDocument();
    });

    it("recovers gracefully when user clicks 'Thử tải lại không gian'", () => {
      let failCount = 1;
      function TransientFailure(): React.ReactNode {
        if (failCount > 0) {
          throw new ApiError(
            "Lỗi kết nối tạm thời",
            "NETWORK_TIMEOUT",
            null,
            null,
            504,
            "REQ-TIMEOUT-99"
          );
        }
        return <div data-testid="recovered-ui">Không gian làm việc đã phục hồi</div>;
      }

      function Harness() {
        return (
          <DashboardErrorBoundary onReset={() => { failCount = 0; }}>
            <TransientFailure />
          </DashboardErrorBoundary>
        );
      }

      render(<Harness />);

      expect(screen.getByRole("alert")).toBeInTheDocument();

      const retryBtn = screen.getByRole("button", { name: /thử lại/i });
      fireEvent.click(retryBtn);

      // Normal UI is restored
      expect(screen.getByTestId("recovered-ui")).toBeInTheDocument();
      expect(screen.getByText("Không gian làm việc đã phục hồi")).toBeInTheDocument();
    });
  });
});
