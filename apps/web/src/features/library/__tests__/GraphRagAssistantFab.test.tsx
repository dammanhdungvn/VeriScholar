import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { GraphRagAssistantFab } from "../components/GraphRagAssistantFab";
import { libraryApi } from "../api/libraryApi";

vi.mock("../api/libraryApi", () => ({
  libraryApi: {
    queryGraph: vi.fn(),
  },
}));

describe("GraphRagAssistantFab", () => {
  it("opens assistant drawer when clicking the floating bubble", () => {
    render(<GraphRagAssistantFab folderId={null} />);

    // FAB button
    const fabButton = screen.getByRole("button", { name: /Trợ lý GraphRAG/i });
    expect(fabButton).toBeInTheDocument();

    // Drawer should initially not be open
    expect(screen.queryByText(/Hỏi đáp Đồ thị Tri thức GraphRAG/i)).toBeNull();

    // Click FAB
    fireEvent.click(fabButton);

    // Drawer should open
    expect(screen.getByText(/Hỏi đáp Đồ thị Tri thức GraphRAG/i)).toBeInTheDocument();
  });

  it("submits synthesis query and displays answer", async () => {
    vi.mocked(libraryApi.queryGraph).mockResolvedValueOnce({
      mode_used: "hybrid",
      answer: "Transformer vượt trội hơn RNN nhờ cơ chế Self-Attention đa đầu.",
      subgraph: { nodes: [], edges: [] },
      evidence_chunks: [],
    });

    render(<GraphRagAssistantFab folderId={null} />);

    // Open drawer
    fireEvent.click(screen.getByRole("button", { name: /Trợ lý GraphRAG/i }));

    const queryInput = screen.getByPlaceholderText(/Đặt câu hỏi đối chiếu, tổng hợp tri thức/i);
    fireEvent.change(queryInput, { target: { value: "So sánh Transformer và RNN" } });

    const sendBtn = screen.getByTestId("graphrag-submit-btn");
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(screen.getByText(/Transformer vượt trội hơn RNN nhờ cơ chế Self-Attention/i)).toBeInTheDocument();
    });
  });
});
