import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardChatInputBox } from "../components/DashboardChatInputBox";
import { useDashboardStore } from "../stores/useDashboardStore";

describe("DashboardChatInputBox Component", () => {
  beforeEach(() => {
    useDashboardStore.setState({
      reasoningEffort: "light",
      isReasoningEnabled: false,
      selectedModel: "5.6 Luna",
    });
  });

  it("renders pill input without hand icon, opens Reasoning Popover, and defaults to Light", () => {
    const handleSend = vi.fn();
    const handleChangeText = vi.fn();

    render(
      <DashboardChatInputBox
        inputText="Explain attention mechanism"
        onChangeText={handleChangeText}
        onSend={handleSend}
      />
    );

    // Verify hand icon does NOT exist
    expect(screen.queryByTitle(/bàn tay/i)).not.toBeInTheDocument();
    expect(screen.queryByTestId("hand-tool-btn")).not.toBeInTheDocument();

    // Verify Brain toggle exists
    const brainBtn = screen.getByTestId("toggle-reasoning-btn");
    expect(brainBtn).toBeInTheDocument();

    // Click brain button to open Popover
    fireEvent.click(brainBtn);

    // Popover elements: Default is Light (Rule Item 7)
    expect(screen.getByText(/5.6 Luna/i)).toBeInTheDocument();
    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("Light");
    expect(screen.getByTestId("reasoning-slider")).toBeInTheDocument();

    // Select Medium effort
    const mediumStep = screen.getByTestId("reasoning-step-medium");
    fireEvent.click(mediumStep);
    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("Medium");

    // Click Reset button to return to Light
    const resetBtn = screen.getByTestId("reasoning-reset-btn");
    fireEvent.click(resetBtn);
    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("Light");
  });

  it("omits + attachment and Mic buttons when mode='search'", () => {
    render(
      <DashboardChatInputBox
        mode="search"
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
      />
    );

    expect(screen.queryByTitle(/Đính kèm bài báo PDF/i)).not.toBeInTheDocument();
    expect(screen.queryByTitle(/Nhập bằng giọng nói/i)).not.toBeInTheDocument();
  });

  it("stages dropped PDF files, displays dismissible chips, and submits files with prompt", () => {
    const handleSend = vi.fn();
    const handleSendWithFiles = vi.fn();

    render(
      <DashboardChatInputBox
        mode="chat"
        inputText="Tóm tắt paper này"
        onChangeText={vi.fn()}
        onSend={handleSend}
        onSendWithFiles={handleSendWithFiles}
      />
    );

    const dropTarget = screen.getByTestId("chat-input-pill-container");
    const testFile = new File(["dummy pdf content"], "transformer.pdf", {
      type: "application/pdf",
    });

    // Drag over & drop
    fireEvent.dragOver(dropTarget);
    fireEvent.drop(dropTarget, {
      dataTransfer: {
        files: [testFile],
      },
    });

    // Chip should be displayed
    const stagedChip = screen.getByTestId("staged-file-chip");
    expect(stagedChip).toBeInTheDocument();
    expect(stagedChip).toHaveTextContent("transformer.pdf");

    // Submit by clicking send button
    const sendBtn = screen.getByRole("button", { name: /Gửi câu hỏi/i });
    fireEvent.click(sendBtn);

    expect(handleSendWithFiles).toHaveBeenCalledWith(
      "Tóm tắt paper này",
      expect.arrayContaining([testFile])
    );
  });

  it("displays spinning loader when isGenerating is true", () => {
    render(
      <DashboardChatInputBox
        inputText="Explain attention mechanism"
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        isGenerating={true}
      />
    );

    const spinner = screen.getByTestId("send-spinner");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("animate-spin");
  });
});
