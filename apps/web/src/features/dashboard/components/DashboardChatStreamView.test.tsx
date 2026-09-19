import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DashboardChatStreamView } from "./DashboardChatStreamView";
import { useDashboardStore } from "../stores/useDashboardStore";
import type { ChatMessage } from "@/types/dashboard";

describe("DashboardChatStreamView component", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
  });

  const sampleMessages: ChatMessage[] = [
    {
      id: "msg-user-1",
      session_id: "s1",
      role: "user",
      content: "Giải thích Attention?",
      created_at: "2026-09-19T10:00:00Z"
    },
    {
      id: "msg-asst-1",
      session_id: "s1",
      role: "assistant",
      content: "Cơ chế Attention tính toán ma trận Q, K, V.",
      created_at: "2026-09-19T10:00:05Z",
      citations: [
        {
          paper_id: "p1",
          paper_title: "Attention Is All You Need",
          page: 4,
          bbox: [0.1, 0.2, 0.5, 0.6, 4]
        }
      ],
      presupposition_alert: {
        flawed_premise: "Có mạng RNN",
        correction: "Transformer không dùng RNN",
        grounded_bbox: [0.2, 0.3, 0.7, 0.8, 6],
        page: 6
      }
    }
  ];

  it("renders user and assistant messages with citations and presupposition alerts", () => {
    render(
      <DashboardChatStreamView
        messages={sampleMessages}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
      />
    );

    expect(screen.getByText("Giải thích Attention?")).toBeInTheDocument();
    expect(screen.getByText(/Cơ chế Attention tính toán ma trận Q, K, V/i)).toBeInTheDocument();

    // Citation badge exists
    expect(screen.getByText("Tr.4")).toBeInTheDocument();

    // Presupposition alert exists
    expect(screen.getByText(/Thẩm Định Tiền Đề Socratic/i)).toBeInTheDocument();
    expect(screen.getByText("Transformer không dùng RNN")).toBeInTheDocument();
  });

  it("clicking citation badge activates bounding box in store", () => {
    render(
      <DashboardChatStreamView
        messages={sampleMessages}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={false}
        onStopGeneration={vi.fn()}
      />
    );

    const citeBtn = screen.getByTitle(/Xem đoạn bằng chứng tại trang 4/i);
    fireEvent.click(citeBtn);

    expect(useDashboardStore.getState().activeBbox).toEqual([0.1, 0.2, 0.5, 0.6, 4]);
  });

  it("shows stop generation button when isGenerating is true", () => {
    const handleStop = vi.fn();
    render(
      <DashboardChatStreamView
        messages={sampleMessages}
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={true}
        onStopGeneration={handleStop}
      />
    );

    const stopBtn = screen.getByRole("button", { name: /dừng suy luận/i });
    expect(stopBtn).toBeInTheDocument();
    fireEvent.click(stopBtn);
    expect(handleStop).toHaveBeenCalledTimes(1);
  });
});
