import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { WritingAssistantPane } from "./WritingAssistantPane";
import { useWritingStore } from "../stores/useWritingStore";
import type { AtomicClaim, VerifyFactsResponse } from "../types";

describe("WritingAssistantPane", () => {
  const mockClaim: AtomicClaim = {
    id: "claim-test-1",
    claim_text: "Attention is sufficient without recurrence.",
    normalized_entities: ["attention"],
    status: "supported",
    confidence_score: 0.94,
    evidence_text: "Our model achieves state of the art results.",
    evidence_document_id: "doc-1",
    evidence_page: 3,
    evidence_bounding_boxes: [[0.1, 0.2, 0.8, 0.4, 3]],
  };

  const mockVerifyResult: VerifyFactsResponse = {
    draft_id: "draft-1",
    verified_text: "Sample text",
    claims: [mockClaim],
    total_claims: 1,
    supported_claims: 1,
    contradicted_claims: 0,
    unverified_claims: 0,
    supported_ratio: 1.0,
    latency_ms: 120,
    verified_at: "2026-10-15T00:00:00Z",
  };

  beforeEach(() => {
    useWritingStore.getState().reset();
    useWritingStore.getState().setVerifyResult(mockVerifyResult);
  });

  it("renders verification results and claim cards", () => {
    render(<WritingAssistantPane />);

    expect(screen.getByText("SAFE Fact-Checking")).toBeInTheDocument();
    expect(screen.getByText("100%")).toBeInTheDocument();
    expect(screen.getByText(new RegExp(mockClaim.claim_text, "i"))).toBeInTheDocument();
    expect(screen.getByText("Trang 3")).toBeInTheDocument();
    expect(screen.getByText(/Xem Bounding Box ↗/i)).toBeInTheDocument();
  });

  it("triggers openEvidenceModal when clicking claim card or [Xem Bounding Box ↗]", () => {
    const onOpenEvidence = vi.fn();
    render(<WritingAssistantPane onOpenEvidence={onOpenEvidence} />);

    const bboxBtn = screen.getByRole("button", { name: /Xem Bounding Box ↗/i });
    fireEvent.click(bboxBtn);

    expect(onOpenEvidence).toHaveBeenCalledWith(mockClaim);
  });

  it("synchronizes assistantPrompt from store into prompt input with Zero-Click Focus", async () => {
    render(<WritingAssistantPane />);

    const input = screen.getByPlaceholderText(/Yêu cầu AI viết tiếp hoặc sửa văn phong/i) as HTMLInputElement;
    expect(input.value).toBe("");

    const buffer = "<pre_context>Pre</pre_context><target_selection>Target</target_selection><post_context>Post</post_context>";
    act(() => {
      useWritingStore.getState().setAssistantPrompt(buffer);
    });

    // Wait for timer to set promptInput
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
});
