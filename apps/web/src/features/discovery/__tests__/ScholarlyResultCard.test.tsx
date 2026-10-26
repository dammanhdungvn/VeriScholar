import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import {
  ScholarlyResultCard,
  formatScholarlyAuthors,
  sanitizeAcademicTitle,
} from "../components/ScholarlyResultCard";
import type { ScholarlyPaper } from "../api/discoveryApi";

describe("ScholarlyResultCard Utilities", () => {
  describe("formatScholarlyAuthors", () => {
    it("returns 'Chưa rõ tác giả' when author list is empty", () => {
      expect(formatScholarlyAuthors([])).toBe("Chưa rõ tác giả");
    });

    it("joins up to 2 authors directly with comma", () => {
      expect(formatScholarlyAuthors(["Alice"])).toBe("Alice");
      expect(formatScholarlyAuthors(["Alice", "Bob"])).toBe("Alice, Bob");
    });

    it("truncates 3 or more authors to first two followed by 'và cộng sự'", () => {
      expect(formatScholarlyAuthors(["Alice", "Bob", "Charlie"])).toBe(
        "Alice, Bob và cộng sự"
      );
      const fiftyAuthors = Array.from({ length: 50 }, (_, i) => `Researcher ${i + 1}`);
      expect(formatScholarlyAuthors(fiftyAuthors)).toBe(
        "Researcher 1, Researcher 2 và cộng sự"
      );
    });
  });

  describe("sanitizeAcademicTitle", () => {
    it("preserves clean academic titles without LaTeX", () => {
      const title = "Retrieval-Augmented Generation for Large Language Models: A Survey";
      expect(sanitizeAcademicTitle(title)).toBe(title);
    });

    it("cleans raw LaTeX math expressions and symbols", () => {
      const rawTitle = "$B^0_s\\to\\mu^+\\mu^-$ branching fraction measurement";
      const cleaned = sanitizeAcademicTitle(rawTitle);
      expect(cleaned).not.toContain("$");
      expect(cleaned).not.toContain("\\to");
      expect(cleaned).not.toContain("\\mu");
      expect(cleaned).toContain("->");
      expect(cleaned).toContain("mu");
    });
  });
});

describe("ScholarlyResultCard Component", () => {
  const basePaper: ScholarlyPaper = {
    title: "$B^0_s\\to\\mu^+\\mu^-$ Differential Branching Ratio",
    authors: [
      "CMS Collaboration",
      "LHCb Collaboration",
      "ATLAS Collaboration",
      "Alice Cooper",
    ],
    publication_year: 2024,
    venue: "Nature Physics",
    doi: "10.1038/s41567-024-001",
    arxiv_id: "2401.00001",
    abstract:
      "This is a long academic abstract detailing quantum decay rates and empirical measurements observed in particle collisions.",
    access_status: "open_access_pdf",
    is_peer_reviewed: true,
  };

  it("renders truncated authors, sanitized title, and peer-reviewed badge", () => {
    render(<ScholarlyResultCard paper={basePaper} onOpenReading={vi.fn()} />);

    // Truncated authors
    expect(
      screen.getByText("CMS Collaboration, LHCb Collaboration và cộng sự")
    ).toBeInTheDocument();

    // Sanitized title
    expect(
      screen.getByText("B^0_s -> mu^+mu^- Differential Branching Ratio")
    ).toBeInTheDocument();
    expect(screen.queryByText(/\$B\^0_s/)).not.toBeInTheDocument();

    // Badges
    expect(screen.getByText("Open Access PDF")).toBeInTheDocument();
    expect(screen.getByText("Đã bình duyệt")).toBeInTheDocument();

    // Year and venue
    expect(screen.getByText("2024")).toBeInTheDocument();
    expect(screen.getByText("Nature Physics")).toBeInTheDocument();
  });

  it("limits abstract to line-clamp-2 and supports expansion", () => {
    render(<ScholarlyResultCard paper={basePaper} onOpenReading={vi.fn()} />);

    const abstractElem = screen.getByText(basePaper.abstract!);
    expect(abstractElem).toHaveClass("line-clamp-2");

    const expandBtn = screen.getByText("Xem thêm tóm tắt");
    fireEvent.click(expandBtn);

    expect(abstractElem).not.toHaveClass("line-clamp-2");
    expect(screen.getByText("Thu gọn")).toBeInTheDocument();
  });

  it("renders external DOI and arXiv links with target='_blank' and rel='noreferrer'", () => {
    render(<ScholarlyResultCard paper={basePaper} onOpenReading={vi.fn()} />);

    const doiLink = screen.getByRole("link", { name: /DOI:/i });
    expect(doiLink).toHaveAttribute("target", "_blank");
    expect(doiLink).toHaveAttribute("rel", "noreferrer");
    expect(doiLink).toHaveAttribute("href", `https://doi.org/${basePaper.doi}`);

    const arxivLink = screen.getByRole("link", { name: /arXiv:/i });
    expect(arxivLink).toHaveAttribute("target", "_blank");
    expect(arxivLink).toHaveAttribute("rel", "noreferrer");
    expect(arxivLink).toHaveAttribute("href", `https://arxiv.org/abs/${basePaper.arxiv_id}`);
  });

  it("renders 'Tóm tắt' badge for abstract_only paper without peer-reviewed tag when false", () => {
    const paywalledPaper: ScholarlyPaper = {
      ...basePaper,
      access_status: "abstract_only",
      is_peer_reviewed: false,
    };

    render(<ScholarlyResultCard paper={paywalledPaper} onOpenReading={vi.fn()} />);

    expect(screen.getByText("Tóm tắt")).toBeInTheDocument();
    expect(screen.queryByText("Đã bình duyệt")).not.toBeInTheDocument();
  });
});
