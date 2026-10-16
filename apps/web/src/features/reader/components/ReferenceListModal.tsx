import type { ReferenceItemResponse } from "@/types/document";
import { SmartReferenceDrawer } from "./SmartReferenceDrawer";
import type { ResolvedReferenceCard } from "../types/reference";

export interface ReferenceListModalProps {
  isOpen: boolean;
  onClose: () => void;
  references: ReferenceItemResponse[];
  isLoading?: boolean;
  onReextract?: () => Promise<void>;
  documentId?: string;
  sessionId?: string | null;
}

/**
 * Upgraded ReferenceListModal conforming to PRD §3.3 specifications
 * by leveraging the SmartReferenceDrawer component.
 */
export function ReferenceListModal({
  isOpen,
  onClose,
  references,
  isLoading = false,
  onReextract,
  documentId = "",
  sessionId,
}: ReferenceListModalProps) {
  const mappedReferences: ResolvedReferenceCard[] = references.map((r) => ({
    ref_index: r.ref_index,
    raw_text: r.raw_text,
    title: r.parsed.title || r.raw_text,
    authors: r.parsed.authors || [],
    year: r.parsed.year,
    arxiv_id: r.parsed.arxiv_id,
    doi: r.parsed.doi,
    open_access_pdf_url: r.parsed.arxiv_id
      ? `https://arxiv.org/pdf/${r.parsed.arxiv_id}.pdf`
      : null,
    sources: r.parsed.arxiv_id
      ? ["arXiv"]
      : r.parsed.doi
      ? ["Crossref"]
      : ["Scholar"],
  }));

  return (
    <SmartReferenceDrawer
      isOpen={isOpen}
      onClose={onClose}
      documentId={documentId}
      sessionId={sessionId}
      references={mappedReferences}
      isLoading={isLoading}
      onReextract={onReextract}
    />
  );
}
