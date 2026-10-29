import { describe, it, expect } from "vitest";
import { normalizeCitation } from "../hooks/useStreamingChat";

describe("normalizeCitation", () => {
  it("preserves full bounding_boxes array and assigns primary bbox", () => {
    const raw = {
      citation_id: "cit_1",
      paper_id: "doc-123",
      page_number: 1,
      bounding_boxes: [
        [0.1, 0.2, 0.4, 0.3, 1],
        [0.1, 0.35, 0.4, 0.45, 1],
      ],
      document_title: "Test Paper",
    };

    const normalized = normalizeCitation(raw);
    expect(normalized.citation_id).toBe("cit_1");
    expect(normalized.paper_id).toBe("doc-123");
    expect(normalized.page).toBe(1);
    expect(normalized.bbox).toEqual([0.1, 0.2, 0.4, 0.3, 1]);
    expect(normalized.bounding_boxes).toEqual([
      [0.1, 0.2, 0.4, 0.3, 1],
      [0.1, 0.35, 0.4, 0.45, 1],
    ]);
  });

  it("falls back to wrapping single bbox in bounding_boxes when bounding_boxes is missing", () => {
    const raw = {
      citation_id: "cit_2",
      document_id: "doc-456",
      page: 2,
      bbox: [0.05, 0.1, 0.5, 0.2, 2],
      paper_title: "Single Bbox Paper",
    };

    const normalized = normalizeCitation(raw);
    expect(normalized.citation_id).toBe("cit_2");
    expect(normalized.paper_id).toBe("doc-456");
    expect(normalized.page).toBe(2);
    expect(normalized.bbox).toEqual([0.05, 0.1, 0.5, 0.2, 2]);
    expect(normalized.bounding_boxes).toEqual([[0.05, 0.1, 0.5, 0.2, 2]]);
  });
});
