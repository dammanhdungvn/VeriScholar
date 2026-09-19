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
});
