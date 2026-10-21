import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DashboardChatInputBox } from "./DashboardChatInputBox";
import { useDashboardStore } from "../stores/useDashboardStore";

describe("DashboardChatInputBox component", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
  });

  it("updates text and submits with Enter", () => {
    const handleChange = vi.fn();
    const handleSend = vi.fn();

    render(
      <DashboardChatInputBox
        inputText="Giải thích cơ chế Attention"
        onChangeText={handleChange}
        onSend={handleSend}
      />
    );

    const textarea = screen.getByPlaceholderText(/Tôi có thể giúp gì/i);
    expect(textarea).toHaveValue("Giải thích cơ chế Attention");

    // Enter without Shift submits
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });
    expect(handleSend).toHaveBeenCalledTimes(1);
  });

  it("does not submit with Enter if Shift key is held", () => {
    const handleSend = vi.fn();

    render(
      <DashboardChatInputBox
        inputText="Dòng 1"
        onChangeText={vi.fn()}
        onSend={handleSend}
      />
    );

    const textarea = screen.getByPlaceholderText(/Tôi có thể giúp gì/i);
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: true });
    expect(handleSend).not.toHaveBeenCalled();
  });

  it("triggers file upload directly without opening modal when clicking attachment button", () => {
    const handleUploadFile = vi.fn();
    render(
      <DashboardChatInputBox
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        onUploadFile={handleUploadFile}
      />
    );

    const fileInput = screen.getByLabelText(/Đính kèm bài báo PDF/i) as HTMLInputElement;
    expect(fileInput).toBeInTheDocument();
    expect(fileInput.type).toBe("file");

    const testFile = new File(["pdf content"], "research_paper.pdf", { type: "application/pdf" });
    fireEvent.change(fileInput, { target: { files: [testFile] } });

    expect(handleUploadFile).toHaveBeenCalledWith(testFile);
    // Modal is NEVER opened
    expect(useDashboardStore.getState().isUploadModalOpen).toBe(false);
  });

  it("opens voice modal when clicking mic button", () => {
    render(
      <DashboardChatInputBox
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
      />
    );

    const micBtn = screen.getByTitle(/Nhập bằng giọng nói/i);
    fireEvent.click(micBtn);
    expect(useDashboardStore.getState().isVoiceModalOpen).toBe(true);
  });

  it("renders Context Chip above chat input and auto-focuses textarea (Zero-Click Focus)", () => {
    const handleRemoveChip = vi.fn();
    const handleChipClick = vi.fn();

    const mockChip = {
      text: "Multi-head attention allows the model to jointly attend to information...",
      pageNumber: 3,
      bbox: [0.1, 0.2, 0.8, 0.4, 3] as [number, number, number, number, number],
      documentTitle: "Attention Is All You Need",
    };

    render(
      <DashboardChatInputBox
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
        contextChip={mockChip}
        onRemoveContextChip={handleRemoveChip}
        onContextChipClick={handleChipClick}
      />
    );

    // Context chip is displayed with title, page and text
    const chip = screen.getByTestId("context-chip");
    expect(chip).toBeInTheDocument();
    expect(screen.getByText(/Attention Is All You Need • Tr\. 3/i)).toBeInTheDocument();
    expect(screen.getByText(/Multi-head attention/i)).toBeInTheDocument();

    // Auto-focus check
    const textarea = screen.getByRole("textbox");
    expect(document.activeElement).toBe(textarea);

    // Click chip
    fireEvent.click(screen.getByText(/Attention Is All You Need • Tr\. 3/i));
    expect(handleChipClick).toHaveBeenCalledWith(mockChip);

    // Click remove chip
    const removeBtn = screen.getByLabelText(/Xóa đoạn trích ngữ cảnh/i);
    fireEvent.click(removeBtn);
    expect(handleRemoveChip).toHaveBeenCalledTimes(1);
  });

  it("submits message formatted with Context Chip and clears chip upon sending", () => {
    const handleSend = vi.fn();
    const handleChangeText = vi.fn();
    const handleRemoveChip = vi.fn();

    const mockChip = {
      text: "x = a + b",
      pageNumber: 2,
      documentTitle: "Paper Alpha",
    };

    render(
      <DashboardChatInputBox
        inputText="Ý nghĩa của công thức này là gì?"
        onChangeText={handleChangeText}
        onSend={handleSend}
        contextChip={mockChip}
        onRemoveContextChip={handleRemoveChip}
      />
    );

    const sendBtn = screen.getByLabelText("Gửi câu hỏi");
    expect(sendBtn).not.toBeDisabled();

    fireEvent.click(sendBtn);

    expect(handleSend).toHaveBeenCalledWith(
      expect.stringContaining('📎 [Paper Alpha - Trang 2]: "x = a + b"')
    );
    expect(handleSend).toHaveBeenCalledWith(
      expect.stringContaining("Ý nghĩa của công thức này là gì?")
    );
    expect(handleRemoveChip).toHaveBeenCalledTimes(1);
    expect(handleChangeText).toHaveBeenCalledWith("");
  });

  it("renders Socratic Deep Reasoning mode toggle and toggles store state", () => {
    render(
      <DashboardChatInputBox
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
      />
    );

    const toggleBtn = screen.getByTestId("toggle-reasoning-btn");
    expect(toggleBtn).toBeInTheDocument();
    expect(screen.getByText("Suy luận Socratic")).toBeInTheDocument();
    expect(useDashboardStore.getState().isReasoningEnabled).toBe(true);

    // Click to toggle off
    fireEvent.click(toggleBtn);
    expect(useDashboardStore.getState().isReasoningEnabled).toBe(false);

    // Click to toggle on
    fireEvent.click(toggleBtn);
    expect(useDashboardStore.getState().isReasoningEnabled).toBe(true);
  });

  it("opens reasoning popover and allows selecting different reasoning levels via 4-step slider", () => {
    render(
      <DashboardChatInputBox
        inputText=""
        onChangeText={vi.fn()}
        onSend={vi.fn()}
      />
    );

    const toggleBtn = screen.getByTestId("toggle-reasoning-btn");

    // Open popover by clicking toggle button
    fireEvent.click(toggleBtn);

    // Verify popover appears
    const popover = screen.getByTestId("reasoning-popover");
    expect(popover).toBeInTheDocument();

    // Select Step 1: Light
    const step1Btn = screen.getByTestId("reasoning-step-btn-1");
    fireEvent.click(step1Btn);
    expect(useDashboardStore.getState().effortLevel).toBe("Thấp");
    expect(useDashboardStore.getState().isReasoningEnabled).toBe(true);
    expect(screen.getAllByText("Light").length).toBeGreaterThan(0);

    // Select Step 3: Deep
    const step3Btn = screen.getByTestId("reasoning-step-btn-3");
    fireEvent.click(step3Btn);
    expect(useDashboardStore.getState().effortLevel).toBe("Cao");
    expect(screen.getAllByText("Deep").length).toBeGreaterThan(0);

    // Select Step 0: Off
    const step0Btn = screen.getByTestId("reasoning-step-btn-0");
    fireEvent.click(step0Btn);
    expect(useDashboardStore.getState().isReasoningEnabled).toBe(false);
    expect(screen.getAllByText("Tắt").length).toBeGreaterThan(0);
  });
});
