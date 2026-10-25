import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { WritingAssistantPane } from "./WritingAssistantPane";
import { useWritingStore } from "../stores/useWritingStore";

describe("WritingAssistantPane", () => {
  beforeEach(() => {
    useWritingStore.getState().reset();
  });

  it("renders AI Writing Assistant header and preset chips", () => {
    render(<WritingAssistantPane />);

    expect(screen.getByText("AI Writing Assistant")).toBeInTheDocument();
    expect(screen.getByText("Hỗ trợ soạn thảo LaTeX học thuật")).toBeInTheDocument();
    expect(screen.getByText("Chuẩn hóa văn phong học thuật")).toBeInTheDocument();
  });

  it("synchronizes assistantPrompt from store into prompt input with Zero-Click Focus", async () => {
    render(<WritingAssistantPane />);

    const input = screen.getByPlaceholderText(/Yêu cầu AI viết tiếp hoặc sửa văn phong/i) as HTMLInputElement;
    expect(input.value).toBe("");

    const buffer = "<pre_context>Pre</pre_context><target_selection>Target</target_selection><post_context>Post</post_context>";
    act(() => {
      useWritingStore.getState().setAssistantPrompt(buffer);
    });

    await vi.waitFor(() => {
      expect(input.value).toBe(buffer);
    });
  });

  it("sends assistant prompt and clears input and store", async () => {
    const onSendAssistantPrompt = vi.fn();
    render(<WritingAssistantPane onSendAssistantPrompt={onSendAssistantPrompt} />);

    const input = screen.getByPlaceholderText(/Yêu cầu AI viết tiếp hoặc sửa văn phong/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "Viết tiếp phần mở đầu" } });

    const sendBtn = screen.getByTitle("Gửi prompt");
    await act(async () => {
      fireEvent.click(sendBtn);
    });

    expect(onSendAssistantPrompt).toHaveBeenCalledWith("Viết tiếp phần mở đầu");
    expect(input.value).toBe("");
    expect(useWritingStore.getState().assistantPrompt).toBe("");
  });

  it("calls onClose when close button is clicked", () => {
    const onClose = vi.fn();
    render(<WritingAssistantPane onClose={onClose} />);

    const closeBtn = screen.getByTestId("close-assistant-pane-btn");
    expect(closeBtn).toBeInTheDocument();
    fireEvent.click(closeBtn);
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
