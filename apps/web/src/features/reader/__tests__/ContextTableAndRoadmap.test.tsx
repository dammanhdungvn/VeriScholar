import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { SmartReferenceDrawer } from "../components/SmartReferenceDrawer";
import { BridgeHintCard } from "../components/BridgeHintCard";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";

vi.mock("@/features/documents/api/documentsApi", () => ({
  documentsApi: {
    getReferences: vi.fn(),
    resolveReferences: vi.fn(),
  },
}));

vi.mock("@/features/sessions/api/sessionsApi", () => ({
  sessionsApi: {
    ingestReference: vi.fn(),
    ingestReferences: vi.fn(),
    removeDocumentFromSession: vi.fn(),
  },
}));

describe("BridgeHintCard Component", () => {
  const defaultProps = {
    refIndex: 3,
    conceptName: "Cơ chế Tự Chú Ý (Self-Attention)",
    paperTitle: "Attention Is All You Need",
    authors: "Vaswani et al.",
    year: 2017,
    reason: "Bài báo hiện tại áp dụng Transformer nhưng không giải thích chi tiết ma trận Q, K, V.",
    canIngest: true,
    onIngest: vi.fn(),
    onDismiss: vi.fn(),
    isIngesting: false,
  };

  it("renders Amber badge and displays concept, paper title, and reason", () => {
    render(<BridgeHintCard {...defaultProps} />);

    // 1. Amber badge
    expect(
      screen.getByText(/GỢI Ý LỘ TRÌNH HỌC TUẦN TỰ \(A → B → C → D\)/i)
    ).toBeInTheDocument();

    // 2. Paper title & Ref index
    expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
    expect(screen.getAllByText(/\[3\]/i).length).toBeGreaterThan(0);

    // 3. Concept name
    expect(
      screen.getByText(/Cơ chế Tự Chú Ý \(Self-Attention\)/i)
    ).toBeInTheDocument();

    // 4. Reason
    expect(
      screen.getByText(/áp dụng Transformer nhưng không giải thích chi tiết/i)
    ).toBeInTheDocument();
  });

  it("triggers onIngest when clicking [➕ Nạp bài [k] vào phiên chat này]", () => {
    const onIngest = vi.fn();
    render(<BridgeHintCard {...defaultProps} onIngest={onIngest} />);

    const ingestBtn = screen.getByRole("button", {
      name: /Nạp bài.*\[3\].*vào phiên chat/i,
    });
    fireEvent.click(ingestBtn);
    expect(onIngest).toHaveBeenCalledTimes(1);
  });

  it("triggers onDismiss when clicking [Bỏ qua]", () => {
    const onDismiss = vi.fn();
    render(<BridgeHintCard {...defaultProps} onDismiss={onDismiss} />);

    const dismissBtn = screen.getByRole("button", { name: /Bỏ qua/i });
    fireEvent.click(dismissBtn);
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("disables ingest button and shows loading state when isIngesting is true", () => {
    render(<BridgeHintCard {...defaultProps} isIngesting={true} />);

    const ingestBtn = screen.getByRole("button", {
      name: /Đang nạp|Nạp bài/i,
    });
    expect(ingestBtn).toBeDisabled();
  });

  it("disables ingest button when canIngest is false", () => {
    render(<BridgeHintCard {...defaultProps} canIngest={false} />);

    const ingestBtn = screen.getByRole("button", {
      name: /Nạp bài/i,
    });
    expect(ingestBtn).toBeDisabled();
  });
});

describe("SmartReferenceDrawer 3-Column Context Table", () => {
  const mockReferences = [
    {
      ref_index: 1,
      raw_text: "Vaswani et al. (2017). Attention is all you need.",
      parsed_title: "Attention Is All You Need",
      parsed_authors: ["Vaswani et al."],
      parsed_year: 2017,
      doi: "10.48550/arXiv.1706.03762",
      arxiv_id: "1706.03762",
      access_status: "open_access_pdf",
      pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
      landing_url: "https://arxiv.org/abs/1706.03762",
      is_in_session: false,
      resolved_document_id: null,
    },
    {
      ref_index: 2,
      raw_text: "He et al. (2016). Deep Residual Learning for Image Recognition.",
      parsed_title: "Deep Residual Learning for Image Recognition",
      parsed_authors: ["He et al."],
      parsed_year: 2016,
      doi: "10.1109/CVPR.2016.90",
      arxiv_id: "1512.03385",
      access_status: "paywalled",
      pdf_url: null,
      landing_url: "https://doi.org/10.1109/CVPR.2016.90",
      is_in_session: true,
      resolved_document_id: "doc-he-2016",
    },
    {
      ref_index: 3,
      raw_text: "Goodfellow et al. (2014). Generative Adversarial Networks.",
      parsed_title: "Generative Adversarial Nets",
      parsed_authors: ["Goodfellow et al."],
      parsed_year: 2014,
      doi: null,
      arxiv_id: "1406.2661",
      access_status: "open_access_pdf",
      pdf_url: "https://arxiv.org/pdf/1406.2661.pdf",
      landing_url: "https://arxiv.org/abs/1406.2661",
      is_in_session: false,
      resolved_document_id: null,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders 3 columns properly with paper details, open access URL, and action buttons", () => {
    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="source-doc-id"
        sessionId="active-session-id"
        references={mockReferences as any}
      />
    );

    // Verify 3 column headers exist
    expect(screen.getByRole("columnheader", { name: /Thông tin bài báo/i })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /Nguồn gốc|Liên kết/i })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /Hành động/i })).toBeInTheDocument();

    // Column 1 checks:
    // - Index, title, authors, year, DOI / arXiv
    expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
    expect(screen.getByText(/\[1\]/i)).toBeInTheDocument();
    expect(screen.getByText(/Vaswani et al\./i)).toBeInTheDocument();
    expect(screen.getByText(/arXiv: 1706\.03762/i)).toBeInTheDocument();
    // Status badges:
    // ref 1 and 3 have open access -> 🟢 Có sẵn PDF
    expect(screen.getAllByText(/🟢 Có sẵn PDF/i).length).toBeGreaterThan(0);
    // ref 2 has paywalled/abstract only -> 🔒 Abstract Only or 🟡 Chỉ có Abstract
    expect(screen.getByText(/🔒 Abstract Only|🟡 Chỉ có Abstract/i)).toBeInTheDocument();

    // Column 2 checks:
    // Link to origin URL with external link
    const links = screen.getAllByRole("link");
    const arxivLink = links.find((l) => l.getAttribute("href")?.includes("arxiv.org"));
    expect(arxivLink).toBeInTheDocument();

    // Column 3 checks:
    // ref 1 is not in session -> [➕ Thêm vào chat]
    // ref 2 is in session -> [🗑️ Xóa khỏi chat]
    const addButtons = screen.getAllByRole("button", { name: /Thêm vào chat/i });
    expect(addButtons.length).toBeGreaterThan(0);

    const removeButtons = screen.getAllByRole("button", { name: /Xóa khỏi chat|Gỡ khỏi phiên/i });
    expect(removeButtons.length).toBeGreaterThan(0);
  });

  it("filters reference list quickly via search input (title, author, DOI/arXiv)", () => {
    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="source-doc-id"
        sessionId="active-session-id"
        references={mockReferences as any}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Lọc theo tiêu đề, tác giả/i);

    // Search by title
    fireEvent.change(searchInput, { target: { value: "Residual" } });
    expect(screen.getByText(/Deep Residual Learning/i)).toBeInTheDocument();
    expect(screen.queryByText(/Attention Is All You Need/i)).not.toBeInTheDocument();

    // Search by author
    fireEvent.change(searchInput, { target: { value: "Goodfellow" } });
    expect(screen.getByText(/Generative Adversarial Nets/i)).toBeInTheDocument();
    expect(screen.queryByText(/Deep Residual Learning/i)).not.toBeInTheDocument();

    // Search by arxiv id
    fireEvent.change(searchInput, { target: { value: "1706.03762" } });
    expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
    expect(screen.queryByText(/Generative Adversarial Nets/i)).not.toBeInTheDocument();
  });

  it("calls sessionsApi.ingestReference when clicking [➕ Thêm vào chat] and transitions to [🗑️ Xóa khỏi chat]", async () => {
    vi.mocked(sessionsApi.ingestReference).mockResolvedValueOnce({
      session_id: "active-session-id",
      document_id: "doc-new-ingested",
      title: "Attention Is All You Need",
      status: "parsing",
      access_status: "open_access_pdf",
      ref_index: 1,
      total_documents_in_session: 2,
      ingested_documents: [
        { id: "doc-new-ingested", title: "Attention Is All You Need", filename: "reference_1.pdf" },
      ],
    } as any);

    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="source-doc-id"
        sessionId="active-session-id"
        currentDocCount={1}
        references={mockReferences as any}
      />
    );

    // Find row 1's add button
    const row1 = screen.getByTestId("ref-row-1");
    const addBtn = row1.querySelector("button[data-action='ingest']");
    expect(addBtn).toBeInTheDocument();
    fireEvent.click(addBtn!);

    await waitFor(() => {
      expect(sessionsApi.ingestReference).toHaveBeenCalledWith(
        "active-session-id",
        "source-doc-id",
        1
      );
    });

    // After successful ingest, row 1 now shows remove action [🗑️ Xóa khỏi chat]
    await waitFor(() => {
      const removeBtn = row1.querySelector("button[data-action='remove']");
      expect(removeBtn).toBeInTheDocument();
    });
  });

  it("calls sessionsApi.removeDocumentFromSession when clicking [🗑️ Xóa khỏi chat]", async () => {
    vi.mocked(sessionsApi.removeDocumentFromSession).mockResolvedValueOnce(undefined);

    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="source-doc-id"
        sessionId="active-session-id"
        currentDocCount={2}
        references={mockReferences as any}
      />
    );

    const row2 = screen.getByTestId("ref-row-2");
    const removeBtn = row2.querySelector("button[data-action='remove']");
    expect(removeBtn).toBeInTheDocument();
    fireEvent.click(removeBtn!);

    await waitFor(() => {
      expect(sessionsApi.removeDocumentFromSession).toHaveBeenCalledWith(
        "active-session-id",
        "doc-he-2016"
      );
    });
  });

  it("disables [➕ Thêm vào chat] button when session reaches 5 documents limit", () => {
    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="source-doc-id"
        sessionId="active-session-id"
        currentDocCount={5}
        references={mockReferences as any}
      />
    );

    const row1 = screen.getByTestId("ref-row-1");
    const addBtn = row1.querySelector("button[data-action='ingest']") as HTMLButtonElement;
    expect(addBtn).toBeDisabled();
    expect(screen.getByTestId("capacity-warning-banner")).toBeInTheDocument();
  });

  it("fetches references via documentsApi.getReferences when opened without prop references", async () => {
    vi.mocked(documentsApi.getReferences).mockResolvedValueOnce({
      document_id: "source-doc-id",
      total_references: 1,
      references: [mockReferences[0] as any],
    });

    render(
      <SmartReferenceDrawer
        isOpen={true}
        onClose={vi.fn()}
        documentId="source-doc-id"
        sessionId="active-session-id"
      />
    );

    await waitFor(() => {
      expect(documentsApi.getReferences).toHaveBeenCalledWith(
        "source-doc-id",
        "active-session-id"
      );
    });

    await waitFor(() => {
      expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
    });
  });
});
