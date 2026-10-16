import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, act, waitFor } from "@testing-library/react";
import { SmartReferenceDrawer } from "./SmartReferenceDrawer";
import type { ResolvedReferenceCard } from "../types/reference";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { useReaderStore } from "../stores/useReaderStore";

vi.mock("@/features/documents/api/documentsApi", () => ({
  documentsApi: {
    resolveReferences: vi.fn(),
  },
}));

vi.mock("@/features/sessions/api/sessionsApi", () => ({
  sessionsApi: {
    ingestReferences: vi.fn(),
  },
}));

describe("SmartReferenceDrawer Component", () => {
  const mockReferences: ResolvedReferenceCard[] = [
    {
      ref_index: 1,
      raw_text: "Vaswani et al. Attention Is All You Need. NeurIPS 2017.",
      title: "Attention Is All You Need",
      authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
      year: 2017,
      doi: "10.5555/3295222.3295349",
      arxiv_id: "1706.03762",
      open_access_pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
      abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
      citation_count: 120500,
      sources: ["arXiv", "Crossref", "Exa"],
      landing_url: "https://arxiv.org/abs/1706.03762",
      is_ingested: false,
    },
    {
      ref_index: 2,
      raw_text: "Devlin et al. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL 2019.",
      title: "BERT: Pre-training of Deep Bidirectional Transformers",
      authors: ["Jacob Devlin", "Ming-Wei Chang"],
      year: 2019,
      doi: "10.18653/v1/N19-1423",
      arxiv_id: "1810.04805",
      open_access_pdf_url: null, // Abstract only!
      abstract: "We introduce a new language representation model called BERT.",
      citation_count: 85000,
      sources: ["Semantic Scholar", "Crossref"],
      landing_url: "https://aclanthology.org/N19-1423/",
      is_ingested: false,
    },
    {
      ref_index: 3,
      raw_text: "Brown et al. Language Models are Few-Shot Learners. NeurIPS 2020.",
      title: "Language Models are Few-Shot Learners (GPT-3)",
      authors: ["Tom B. Brown", "Benjamin Mann"],
      year: 2020,
      arxiv_id: "2005.14165",
      open_access_pdf_url: "https://arxiv.org/pdf/2005.14165.pdf",
      sources: ["arXiv", "Exa", "PubMed"],
      citation_count: 42000,
      is_ingested: false,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    useReaderStore.setState({
      openDocumentIds: ["doc-root"],
      activeDocumentId: "doc-root",
    });
  });

  it("renders 3-column table with header, select-all checkbox, and information", () => {
    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="doc-root"
        references={mockReferences}
        currentDocCount={1}
      />
    );

    // Dialog & Header
    expect(screen.getByRole("dialog", { name: /Smart Reference Card Drawer/i })).toBeInTheDocument();
    expect(screen.getByText(/Tài liệu Tham khảo & Đọc Sâu \(PRD §3.3\)/i)).toBeInTheDocument();
    expect(screen.getByText(/3 bài/i)).toBeInTheDocument();

    // 3 Columns in Table Header
    expect(screen.getByTestId("select-all-checkbox")).toBeInTheDocument();
    expect(screen.getByText("Thông tin bài báo & Trạng thái")).toBeInTheDocument();
    expect(screen.getByText("Nguồn học thuật & Liên kết")).toBeInTheDocument();

    // Column 2 content: Titles & Authors
    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText("BERT: Pre-training of Deep Bidirectional Transformers")).toBeInTheDocument();
    expect(screen.getByText(/Ashish Vaswani, Noam Shazeer/i)).toBeInTheDocument();
    expect(screen.getByText("(2017)")).toBeInTheDocument();

    // Column 3 content: Sources
    expect(screen.getAllByText("arXiv").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Crossref").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Exa").length).toBeGreaterThanOrEqual(1);
  });

  it("renders [🟢 Đã tìm thấy PDF Open-Access] badge when open-access PDF is available, and [🟡 Chỉ có Abstract] when not", () => {
    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="doc-root"
        references={mockReferences}
        currentDocCount={1}
      />
    );

    const openAccessBadges = screen.getAllByTestId("badge-open-access");
    expect(openAccessBadges.length).toBe(2); // ref 1 and ref 3
    expect(openAccessBadges[0]).toHaveTextContent(/🟢 Đã tìm thấy PDF Open-Access/i);

    const abstractOnlyBadges = screen.getAllByTestId("badge-abstract-only");
    expect(abstractOnlyBadges.length).toBe(1); // ref 2
    expect(abstractOnlyBadges[0]).toHaveTextContent(/🟡 Chỉ có Abstract/i);
  });

  it("handles select-all and individual checkbox toggles", () => {
    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="doc-root"
        references={mockReferences}
        currentDocCount={1}
      />
    );

    const selectAll = screen.getByTestId("select-all-checkbox") as HTMLInputElement;
    const ref1Checkbox = screen.getByTestId("ref-checkbox-1") as HTMLInputElement;
    const ref2Checkbox = screen.getByTestId("ref-checkbox-2") as HTMLInputElement;

    expect(selectAll.checked).toBe(false);
    expect(ref1Checkbox.checked).toBe(false);

    // Select individual
    fireEvent.click(ref1Checkbox);
    expect(ref1Checkbox.checked).toBe(true);
    expect(screen.getByTestId("session-capacity-info")).toHaveTextContent("Đã chọn: 1");

    // Select all
    fireEvent.click(selectAll);
    expect(ref1Checkbox.checked).toBe(true);
    expect(ref2Checkbox.checked).toBe(true);
    expect(screen.getByTestId("session-capacity-info")).toHaveTextContent("Đã chọn: 3");

    // Deselect all
    fireEvent.click(selectAll);
    expect(ref1Checkbox.checked).toBe(false);
    expect(ref2Checkbox.checked).toBe(false);
  });

  it("enforces session capacity guard: disables ingest button and displays warning banner when currentDocCount + selectedCount > 5", () => {
    // Current session already has 4 documents open
    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="doc-root"
        references={mockReferences}
        currentDocCount={4}
      />
    );

    const ingestBtn = screen.getByTestId("ingest-references-btn");
    expect(ingestBtn).toBeDisabled(); // 0 selected
    expect(screen.queryByTestId("capacity-warning-banner")).toBeNull();

    // Select 1 paper (4 + 1 = 5 <= 5, exactly at capacity)
    fireEvent.click(screen.getByTestId("ref-checkbox-1"));
    expect(ingestBtn).not.toBeDisabled();
    expect(screen.queryByTestId("capacity-warning-banner")).toBeNull();

    // Select second paper (4 + 2 = 6 > 5, capacity exceeded!)
    fireEvent.click(screen.getByTestId("ref-checkbox-2"));
    expect(ingestBtn).toBeDisabled();

    // Capacity warning banner must be shown
    const warningBanner = screen.getByTestId("capacity-warning-banner");
    expect(warningBanner).toBeInTheDocument();
    expect(warningBanner).toHaveTextContent(
      "Phiên đọc sâu giới hạn tối đa 5 bài báo. Vui lòng bỏ bớt bài hoặc lưu vào Thư viện (Module 4) để quản lý kho lớn hơn"
    );
  });

  it("calls sessionsApi.ingestReferences and adds documents to reader store on successful ingestion", async () => {
    const onIngestSuccess = vi.fn();
    const mockIngestResponse = {
      session_id: "sess-abc",
      ingested_documents: [
        {
          id: "doc-vaswani",
          title: "Attention Is All You Need",
          filename: "1706.03762.pdf",
        },
      ],
      total_documents_in_session: 2,
    };

    vi.mocked(sessionsApi.ingestReferences).mockResolvedValueOnce(mockIngestResponse);

    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="doc-root"
        sessionId="sess-abc"
        references={mockReferences}
        currentDocCount={1}
        onIngestSuccess={onIngestSuccess}
      />
    );

    // Select reference 1
    fireEvent.click(screen.getByTestId("ref-checkbox-1"));

    const ingestBtn = screen.getByTestId("ingest-references-btn");
    expect(ingestBtn).not.toBeDisabled();

    await act(async () => {
      fireEvent.click(ingestBtn);
    });

    expect(sessionsApi.ingestReferences).toHaveBeenCalledWith(
      "sess-abc",
      "doc-root",
      [1]
    );

    expect(onIngestSuccess).toHaveBeenCalledWith(mockIngestResponse);

    // Verify reader store updated
    expect(useReaderStore.getState().openDocumentIds).toContain("doc-vaswani");
    expect(useReaderStore.getState().activeDocumentId).toBe("doc-vaswani");

    // Row should now display ingested badge
    expect(screen.getByText("Đã nạp vào phiên")).toBeInTheDocument();
  });

  it("handles auto-fetch when no references are provided in props", async () => {
    vi.mocked(documentsApi.resolveReferences).mockResolvedValueOnce([mockReferences[0]]);

    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="doc-auto"
        currentDocCount={1}
      />
    );

    await waitFor(() => {
      expect(documentsApi.resolveReferences).toHaveBeenCalledWith("doc-auto");
    });

    await waitFor(() => {
      expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    });
  });

  it("closes drawer when clicking cancel or close button or pressing Escape", () => {
    const onClose = vi.fn();

    const { rerender } = render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={onClose}
        documentId="doc-root"
        references={mockReferences}
      />
    );

    // Click close X
    fireEvent.click(screen.getByTestId("close-drawer-btn"));
    expect(onClose).toHaveBeenCalledTimes(1);

    // Click cancel button
    fireEvent.click(screen.getByTestId("cancel-drawer-btn"));
    expect(onClose).toHaveBeenCalledTimes(2);

    // Press Escape
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(3);

    // If isOpen is false, nothing is rendered
    rerender(
      <SmartReferenceDrawer
        isOpen={false}
        onClose={onClose}
        documentId="doc-root"
        references={mockReferences}
      />
    );
    expect(screen.queryByTestId("smart-reference-drawer")).toBeNull();
  });
});
