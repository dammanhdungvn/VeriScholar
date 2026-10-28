import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { SocraticThinkingBlock } from "../SocraticThinkingBlock";
import { AcademicMarkdownRenderer, formatConceptTitle } from "@/components/shared/AcademicMarkdownRenderer";
import type { ChatMessage, CitationBadgeData } from "@/types/dashboard";

describe("Socratic Thinking Block and Citation Formatting", () => {
  describe("formatConceptTitle helper", () => {
    it("splits PascalCase and camelCase strings into human readable words with spaces", () => {
      expect(formatConceptTitle("SelectiveAttention")).toBe("Selective Attention");
      expect(formatConceptTitle("ContextNoise")).toBe("Context Noise");
      expect(formatConceptTitle("PerformanceGain")).toBe("Performance Gain");
      expect(formatConceptTitle("InferenceEfficiency")).toBe("Inference Efficiency");
      expect(formatConceptTitle("MultiHeadAttention")).toBe("Multi Head Attention");
    });

    it("handles underscores and preserves strings that already have spaces", () => {
      expect(formatConceptTitle("Selective_Attention")).toBe("Selective Attention");
      expect(formatConceptTitle("Selective Attention")).toBe("Selective Attention");
      expect(formatConceptTitle("Transformer")).toBe("Transformer");
    });
  });

  describe("SocraticThinkingBlock cleanup (User Req 10)", () => {
    it("does not render robotic 'Analyzed Bounding Box' lines in thinking block when expanded", () => {
      const message: ChatMessage = {
        id: "m-1",
        session_id: "s-1",
        role: "assistant",
        content: "Here is the explanation.",
        thought: "Phân tích cú pháp và trích xuất ngữ cảnh liên quan cho câu hỏi.",
        thought_duration_seconds: 7,
        is_streaming: false,
        citations: [
          {
            citation_id: "cit_1",
            page: 9,
            paper_id: "p1",
            paper_title: "Paper 1",
            bbox: [0.1, 0.1, 0.8, 0.2, 9],
          },
          {
            citation_id: "cit_2",
            page: 6,
            paper_id: "p1",
            paper_title: "Paper 1",
            bbox: [0.1, 0.3, 0.8, 0.4, 6],
          },
        ],
      };

      render(<SocraticThinkingBlock message={message} />);

      // Initially collapsed: shows Thought for 7s >
      const header = screen.getByTestId("socratic-thinking-header");
      expect(header).toBeInTheDocument();
      expect(header.textContent).toContain("Thought for 7s");

      // Expand thought
      fireEvent.click(header);

      // Should display natural thought monologue
      expect(
        screen.getByText("Phân tích cú pháp và trích xuất ngữ cảnh liên quan cho câu hỏi.")
      ).toBeInTheDocument();

      // Must NOT render robotic debug bounding box lines
      expect(screen.queryByText(/Analyzed Bounding Box/i)).toBeNull();
      expect(screen.queryByText(/#Page 9/i)).toBeNull();
      expect(screen.queryByText(/#Page 6/i)).toBeNull();
    });

    it("does not render robotic 'Analyzed Bounding Box' lines during streaming", () => {
      const message: ChatMessage = {
        id: "m-stream",
        session_id: "s-1",
        role: "assistant",
        content: "",
        thought: "Thinking through the attention weights...",
        is_streaming: true,
        citations: [
          {
            citation_id: "cit_1",
            page: 9,
            paper_id: "p1",
            paper_title: "Paper 1",
            bbox: [0.1, 0.1, 0.8, 0.2, 9],
          },
        ],
      };

      render(<SocraticThinkingBlock message={message} />);

      // Shows thinking indicator
      expect(screen.getByTestId("socratic-thinking-block")).toBeInTheDocument();
      // Must NOT render robotic debug lines
      expect(screen.queryByText(/Analyzed Bounding Box/i)).toBeNull();
    });
  });

  describe("AcademicMarkdownRenderer concept citation formatting & accurate navigation (User Req 11)", () => {
    const mockCitations: CitationBadgeData[] = [
      {
        citation_id: "cit_1",
        paper_id: "doc-1",
        page: 2,
        concept_name: "Selective Attention",
        snippet: "We propose Selective Attention to filter out noise.",
        bbox: [0.1, 0.2, 0.8, 0.3, 2],
      },
      {
        citation_id: "cit_2",
        paper_id: "doc-1",
        page: 5,
        concept_name: "Context Noise",
        snippet: "Context noise significantly degrades transformer reasoning.",
        bbox: [0.15, 0.25, 0.75, 0.35, 5],
      },
      {
        citation_id: "cit_3",
        paper_id: "doc-1",
        page: 8,
        concept_name: "Performance Gain",
        snippet: "Consistent performance gain across model scales.",
        bbox: [0.2, 0.4, 0.85, 0.5, 8],
      },
    ];

    it("formats PascalCase concept tags with spaces in concept pills", () => {
      const content =
        "Cơ chế Selective Attention [cite:SelectiveAttention] giúp giảm [cite:ContextNoise] và mang lại [cite:PerformanceGain].";

      render(
        <AcademicMarkdownRenderer
          content={content}
          citations={mockCitations}
        />
      );

      // Verify pills render formatted names with spaces
      expect(screen.getByText("Selective Attention")).toBeInTheDocument();
      expect(screen.getByText("Context Noise")).toBeInTheDocument();
      expect(screen.getByText("Performance Gain")).toBeInTheDocument();

      // Raw unspaced tags should not be shown
      expect(screen.queryByText("SelectiveAttention")).toBeNull();
      expect(screen.queryByText("ContextNoise")).toBeNull();
    });

    it("clicks on specific concept pill and returns the ACCURATELY matched citation data (not always citations[0])", () => {
      const onCitationClick = vi.fn();
      const content =
        "Cơ chế Selective Attention [cite:SelectiveAttention] giúp giảm [cite:ContextNoise].";

      render(
        <AcademicMarkdownRenderer
          content={content}
          citations={mockCitations}
          onCitationClick={onCitationClick}
        />
      );

      // Click on Context Noise pill
      const contextNoisePill = screen.getByRole("button", { name: /Context Noise/i });
      fireEvent.click(contextNoisePill);

      expect(onCitationClick).toHaveBeenCalledTimes(1);
      // It must pass cit_2 (Page 5), NOT cit_1 (Page 2)
      expect(onCitationClick).toHaveBeenCalledWith(
        expect.objectContaining({
          citation_id: "cit_2",
          page: 5,
          concept_name: "Context Noise",
        }),
        "cit_2"
      );
    });

    it("parses literal [ ↪ ConceptName ] format gracefully and formats title", () => {
      const content = "Đặc tính quan trọng [ ↪ PerformanceGain ].";

      render(
        <AcademicMarkdownRenderer
          content={content}
          citations={mockCitations}
        />
      );

      expect(screen.getByText("Performance Gain")).toBeInTheDocument();
    });
  });
});
