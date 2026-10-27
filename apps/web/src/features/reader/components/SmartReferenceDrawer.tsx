import { useEffect, useState, useMemo } from "react";
import {
  X,
  ExternalLink,
  BookMarked,
  RefreshCw,
  AlertTriangle,
  Plus,
  Search,
  Trash2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { ResolvedReferenceCard, SessionIngestResponse } from "../types/reference";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { useReaderStore } from "../stores/useReaderStore";

export interface SmartReferenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  sessionId?: string | null;
  currentDocCount?: number;
  openDocumentIds?: string[];
  references?: ResolvedReferenceCard[];
  isLoading?: boolean;
  onReextract?: () => Promise<void>;
  onIngestSuccess?: (response: SessionIngestResponse) => void;
}

export function SmartReferenceDrawer({
  isOpen,
  onClose,
  documentId,
  sessionId,
  currentDocCount: propCurrentDocCount,
  openDocumentIds: propOpenDocumentIds,
  references: propReferences,
  isLoading: propIsLoading = false,
  onReextract,
  onIngestSuccess,
}: SmartReferenceDrawerProps) {
  // Store fallback for document count and open tabs
  const storeOpenDocIds = useReaderStore((s) => s.openDocumentIds);
  const addOpenDocument = useReaderStore((s) => s.addOpenDocument);
  const removeOpenDocument = useReaderStore((s) => s.removeOpenDocument);
  const setActiveDocumentId = useReaderStore((s) => s.setActiveDocumentId);

  const effectiveOpenIds = propOpenDocumentIds ?? storeOpenDocIds;
  const currentDocCount = propCurrentDocCount ?? (effectiveOpenIds.length || 1);
  const isCapacityExceeded = currentDocCount >= 5;
  const remainingCapacity = Math.max(0, 5 - currentDocCount);

  // Local state
  const [fetchedReferences, setFetchedReferences] = useState<ResolvedReferenceCard[]>([]);
  const [sessionReferenceState, setSessionReferenceState] = useState<
    Map<number, { is_in_session: boolean; resolved_document_id?: string | null }>
  >(new Map());
  const [ingestingIndices, setIngestingIndices] = useState<Set<number>>(new Set());
  const [removingIndices, setRemovingIndices] = useState<Set<number>>(new Set());

  const [isFetching, setIsFetching] = useState(false);
  const [isReextracting, setIsReextracting] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [ingestError, setIngestError] = useState<string | null>(null);

  // Determine base reference list
  const baseReferences =
    propReferences && propReferences.length > 0
      ? propReferences
      : fetchedReferences;

  // Fetch references when drawer opens
  useEffect(() => {
    if (!isOpen || !documentId || (propReferences && propReferences.length > 0)) {
      return;
    }

    let isMounted = true;
    setIsFetching(true);
    setIngestError(null);

    documentsApi
      .getReferences(documentId, sessionId)
      .then((res) => {
        if (!isMounted) return;
        if (res && res.references) {
          const mapped: ResolvedReferenceCard[] = res.references.map((r) => ({
            ref_index: r.ref_index,
            raw_text: r.raw_text,
            title: r.parsed_title || r.raw_text,
            parsed_title: r.parsed_title,
            authors: r.parsed_authors || [],
            parsed_authors: r.parsed_authors,
            year: r.parsed_year,
            parsed_year: r.parsed_year,
            doi: r.doi,
            arxiv_id: r.arxiv_id,
            access_status: r.access_status,
            open_access_pdf_url: r.pdf_url,
            pdf_url: r.pdf_url,
            landing_url:
              r.landing_url ||
              (r.arxiv_id
                ? `https://arxiv.org/abs/${r.arxiv_id}`
                : r.doi
                ? `https://doi.org/${r.doi}`
                : null),
            is_in_session: r.is_in_session,
            is_ingested: r.is_in_session,
            resolved_document_id: r.resolved_document_id,
            sources: r.arxiv_id
              ? ["arXiv"]
              : r.doi
              ? ["Crossref"]
              : ["Scholar"],
          }));
          setFetchedReferences(mapped);
        } else {
          setFetchedReferences([]);
        }
      })
      .catch(() => {
        return documentsApi.resolveReferences(documentId).then((data) => {
          if (isMounted) {
            setFetchedReferences(data);
          }
        });
      })
      .catch((err) => {
        if (isMounted) {
          setFetchedReferences([]);
          setIngestError(
            err instanceof Error ? err.message : "Không thể tải danh mục tham khảo"
          );
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsFetching(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, documentId, propReferences, sessionId]);

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Filtered references
  const filteredReferences = useMemo(() => {
    if (!searchQuery.trim()) return baseReferences;
    const q = searchQuery.toLowerCase();
    return baseReferences.filter((r) => {
      const title = (r.parsed_title || r.title || r.raw_text || "").toLowerCase();
      const raw = (r.raw_text || "").toLowerCase();
      const authors = (r.parsed_authors || r.authors || []).join(" ").toLowerCase();
      const arxiv = (r.arxiv_id || "").toLowerCase();
      const doi = (r.doi || "").toLowerCase();
      return (
        title.includes(q) ||
        raw.includes(q) ||
        authors.includes(q) ||
        arxiv.includes(q) ||
        doi.includes(q)
      );
    });
  }, [baseReferences, searchQuery]);

  if (!isOpen) return null;

  const handleReextractClick = async () => {
    if (isReextracting || isFetching) return;
    setIsReextracting(true);
    setIngestError(null);
    try {
      if (onReextract) {
        await onReextract();
      } else {
        const fresh = await documentsApi.getReferences(documentId, sessionId);
        if (fresh && fresh.references) {
          const mapped: ResolvedReferenceCard[] = fresh.references.map((r) => ({
            ref_index: r.ref_index,
            raw_text: r.raw_text,
            title: r.parsed_title || r.raw_text,
            parsed_title: r.parsed_title,
            authors: r.parsed_authors || [],
            parsed_authors: r.parsed_authors,
            year: r.parsed_year,
            parsed_year: r.parsed_year,
            doi: r.doi,
            arxiv_id: r.arxiv_id,
            access_status: r.access_status,
            open_access_pdf_url: r.pdf_url,
            pdf_url: r.pdf_url,
            landing_url:
              r.landing_url ||
              (r.arxiv_id
                ? `https://arxiv.org/abs/${r.arxiv_id}`
                : r.doi
                ? `https://doi.org/${r.doi}`
                : null),
            is_in_session: r.is_in_session,
            is_ingested: r.is_in_session,
            resolved_document_id: r.resolved_document_id,
            sources: r.arxiv_id ? ["arXiv"] : r.doi ? ["Crossref"] : ["Scholar"],
          }));
          setFetchedReferences(mapped);
        }
      }
    } catch (err) {
      setIngestError(err instanceof Error ? err.message : "Bóc tách lại thất bại");
    } finally {
      setIsReextracting(false);
    }
  };

  const handleIngest = async (refIndex: number) => {
    if (isCapacityExceeded || ingestingIndices.has(refIndex)) return;

    setIngestingIndices((prev) => new Set(prev).add(refIndex));
    setIngestError(null);

    try {
      let targetDocId: string;
      let targetTitle = `Tham khảo [${refIndex}]`;

      if (sessionId) {
        const response = await sessionsApi.ingestReference(
          sessionId,
          documentId,
          refIndex
        );
        targetDocId = response.document_id;
        targetTitle = response.title || targetTitle;
        onIngestSuccess?.(response);
      } else {
        targetDocId = `doc-ingested-${refIndex}`;
        const found = baseReferences.find((r) => r.ref_index === refIndex);
        if (found?.title || found?.parsed_title) {
          targetTitle = found.parsed_title || found.title || targetTitle;
        }
        onIngestSuccess?.({
          session_id: "default-session",
          ingested_documents: [
            {
              id: targetDocId,
              title: targetTitle,
              filename: `reference_${refIndex}.pdf`,
            },
          ],
          total_documents_in_session: currentDocCount + 1,
        });
      }

      setSessionReferenceState((prev) => {
        const next = new Map(prev);
        next.set(refIndex, { is_in_session: true, resolved_document_id: targetDocId });
        return next;
      });

      addOpenDocument(targetDocId);
      setActiveDocumentId(targetDocId);
    } catch (err) {
      setIngestError(
        err instanceof Error ? err.message : "Nạp tài liệu thất bại do lỗi hệ thống"
      );
    } finally {
      setIngestingIndices((prev) => {
        const next = new Set(prev);
        next.delete(refIndex);
        return next;
      });
    }
  };

  const handleRemove = async (ref: ResolvedReferenceCard) => {
    const refIndex = ref.ref_index;
    if (removingIndices.has(refIndex)) return;

    const dynamicState = sessionReferenceState.get(refIndex);
    const targetDocId = dynamicState?.resolved_document_id ?? ref.resolved_document_id;

    setRemovingIndices((prev) => new Set(prev).add(refIndex));
    setIngestError(null);

    try {
      if (sessionId && targetDocId) {
        await sessionsApi.removeDocumentFromSession(sessionId, targetDocId);
      }

      setSessionReferenceState((prev) => {
        const next = new Map(prev);
        next.set(refIndex, { is_in_session: false, resolved_document_id: null });
        return next;
      });

      if (targetDocId) {
        removeOpenDocument(targetDocId);
      }
    } catch (err) {
      setIngestError(
        err instanceof Error ? err.message : "Gỡ tài liệu thất bại do lỗi hệ thống"
      );
    } finally {
      setRemovingIndices((prev) => {
        const next = new Set(prev);
        next.delete(refIndex);
        return next;
      });
    }
  };

  const isLoading = propIsLoading || isFetching;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Smart Reference Card Drawer"
      data-testid="smart-reference-drawer"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div className="w-full max-w-5xl max-h-[90vh] bg-canvas dark:bg-[#181715] rounded-xl shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden text-ink dark:text-zinc-100">
        {/* Drawer Header */}
        <div className="h-14 px-5 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0 bg-surface-cream/50 dark:bg-[#1d1b18]">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
              <BookMarked className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-serif font-bold text-sm leading-tight text-ink dark:text-zinc-100">
                <span aria-hidden="true">Tài liệu tham khảo</span>
                <span className="sr-only">Tài liệu Tham khảo & Đọc Sâu (PRD §3.3)</span>
              </h3>
            </div>
            <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-mono font-semibold bg-zinc-200/70 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
              {baseReferences.length} bài
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleReextractClick}
              disabled={isReextracting || isLoading}
              aria-label="Bóc tách lại danh mục tham khảo"
              title="Phân giải lại danh mục tham khảo qua Exa & Nguồn học thuật"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-hairline dark:border-[#38332c] hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink text-xs transition-colors cursor-pointer disabled:opacity-40"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 text-primary ${
                  isReextracting ? "animate-spin" : ""
                }`}
              />
              <span className="hidden sm:inline font-medium">
                {isReextracting ? "Đang phân giải..." : "Phân giải lại"}
              </span>
            </button>

            <button
              type="button"
              onClick={onClose}
              data-testid="close-drawer-btn"
              aria-label="Đóng danh mục tham khảo"
              className="p-1.5 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Filter bar */}
        <div className="px-5 py-2.5 border-b border-hairline/80 dark:border-[#282522] bg-[#fbf9f5] dark:bg-[#1a1917] flex items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Lọc theo tiêu đề, tác giả, arXiv, DOI..."
              aria-label="Tìm kiếm trong danh mục tham khảo"
              className="w-full pl-8 pr-3 py-1 text-xs rounded-md border border-[#e5dfd4] dark:border-[#38332c] bg-white dark:bg-[#201e1b] outline-none focus:border-primary text-ink dark:text-zinc-100 placeholder:text-muted"
            />
          </div>

          <div className="flex items-center gap-2 text-xs text-muted">
            <span>
              Đang mở:{" "}
              <strong className="text-ink dark:text-zinc-100 font-semibold font-mono">
                {currentDocCount}/5
              </strong>
            </span>
          </div>
        </div>

        {/* Table Content */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="text-center py-16 text-muted font-mono animate-pulse text-xs space-y-2">
              <RefreshCw className="w-5 h-5 mx-auto animate-spin text-primary" />
              <p>Đang phân giải danh mục tài liệu tham khảo với Exa & Crossref...</p>
            </div>
          ) : filteredReferences.length === 0 ? (
            <div className="text-center py-16 text-muted text-xs">
              {searchQuery
                ? "Không tìm thấy tài liệu tham khảo phù hợp với từ khóa."
                : "Chưa có tài liệu tham khảo nào được trích xuất cho bài báo này."}
            </div>
          ) : (
            <table
              className="w-full text-left text-xs border-collapse"
              aria-label="Bảng danh mục tài liệu tham khảo 3 cột"
            >
              <thead>
                <tr className="border-b border-hairline dark:border-[#2f2b26] bg-[#f5f1ea]/70 dark:bg-[#201e1b] text-muted text-[11px] font-medium sticky top-0 z-10 backdrop-blur-xs">
                  {/* Column 1: Article Info & Status */}
                  <th scope="col" className="px-4 py-2.5 text-left">
                    Thông tin bài báo & Trạng thái
                  </th>
                  {/* Column 2: Origin & Open Access Link */}
                  <th scope="col" className="w-56 px-4 py-2.5 text-left">
                    Nguồn gốc & Liên kết
                  </th>
                  {/* Column 3: Action */}
                  <th scope="col" className="w-44 px-4 py-2.5 text-center">
                    Hành động
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hairline/60 dark:divide-[#272420]">
                {filteredReferences.map((ref) => {
                  const dynamicState = sessionReferenceState.get(ref.ref_index);
                  const isInSession =
                    dynamicState !== undefined
                      ? dynamicState.is_in_session
                      : Boolean(
                          ref.is_in_session ||
                          ref.is_ingested ||
                          (ref.resolved_document_id &&
                            effectiveOpenIds.includes(ref.resolved_document_id))
                        );

                  const isIngestingThis = ingestingIndices.has(ref.ref_index);
                  const isRemovingThis = removingIndices.has(ref.ref_index);

                  const title =
                    ref.parsed_title || ref.title || ref.raw_text || `Tham khảo [${ref.ref_index}]`;
                  const authors = ref.parsed_authors || ref.authors || [];
                  const year = ref.parsed_year || ref.year;

                  const arxivUrl = ref.arxiv_id
                    ? `https://arxiv.org/abs/${ref.arxiv_id}`
                    : null;
                  const doiUrl = ref.doi ? `https://doi.org/${ref.doi}` : null;
                  const pdfUrl = ref.pdf_url || ref.open_access_pdf_url || null;
                  const targetUrl =
                    ref.landing_url || pdfUrl || arxivUrl || doiUrl || "#";

                  const isOpenAccess =
                    ref.access_status === "open_access_pdf" || Boolean(pdfUrl);

                  const sources =
                    ref.sources && ref.sources.length > 0
                      ? ref.sources
                      : ref.arxiv_id
                      ? ["arXiv"]
                      : ref.doi
                      ? ["Crossref"]
                      : ["Scholar"];

                  return (
                    <tr
                      key={ref.ref_index}
                      data-testid={`ref-row-${ref.ref_index}`}
                      className={cn(
                        "transition-colors",
                        isInSession
                          ? "bg-emerald-500/[0.04] dark:bg-emerald-500/[0.06]"
                          : "hover:bg-black/[0.015] dark:hover:bg-white/[0.02]"
                      )}
                    >
                      {/* Column 1: Article Info & Status Badge */}
                      <td className="px-4 py-3 space-y-1.5 align-top">
                        <div className="flex items-start gap-2.5">
                          <span className="font-mono text-[11px] font-semibold text-muted shrink-0 mt-0.5">
                            [{ref.ref_index}]
                          </span>
                          <div className="space-y-1 flex-1 min-w-0">
                            <h4
                              className="font-serif font-bold text-ink dark:text-zinc-100 line-clamp-2 leading-snug"
                              title={title}
                            >
                              {title}
                            </h4>

                            {/* Authors & Year */}
                            <div className="text-[11px] text-muted dark:text-zinc-400 flex flex-wrap items-center gap-x-2 gap-y-0.5 font-sans">
                              {authors.length > 0 && <span>{authors.join(", ")}</span>}
                              {year && <span className="font-mono">({year})</span>}
                              {ref.citation_count !== undefined &&
                                ref.citation_count !== null && (
                                  <span className="font-mono text-zinc-500">
                                    • {ref.citation_count.toLocaleString()} trích dẫn
                                  </span>
                                )}
                            </div>

                            {/* Identifiers: DOI & arXiv */}
                            <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono text-muted">
                              {ref.arxiv_id && <span>arXiv: {ref.arxiv_id}</span>}
                              {ref.doi && <span>DOI: {ref.doi}</span>}
                            </div>

                            {/* Abstract preview if available */}
                            {ref.abstract && (
                              <p className="text-[11px] text-muted dark:text-zinc-400 line-clamp-2 italic leading-relaxed pt-0.5">
                                "{ref.abstract}"
                              </p>
                            )}

                            {/* Status Badge */}
                            <div className="pt-1 flex items-center gap-2">
                              {isOpenAccess ? (
                                <span
                                  data-testid="badge-open-access"
                                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60"
                                >
                                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                  🟢 Có sẵn PDF
                                </span>
                              ) : (
                                <span
                                  data-testid="badge-abstract-only"
                                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border border-amber-200 dark:border-amber-800/60"
                                >
                                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                  🔒 Abstract Only
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Column 2: Origin & Open Access URL */}
                      <td className="px-4 py-3 align-top space-y-2">
                        <div className="space-y-1.5">
                          {targetUrl && targetUrl !== "#" ? (
                            <a
                              href={targetUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline font-medium break-all"
                              title={targetUrl}
                            >
                              <span>
                                {ref.arxiv_id
                                  ? "arXiv Page"
                                  : ref.doi
                                  ? "Crossref / DOI"
                                  : "Nguồn gốc"}
                              </span>
                              <ExternalLink className="w-3 h-3 shrink-0 text-muted" />
                            </a>
                          ) : (
                            <span className="text-[11px] text-muted italic">
                              Chưa có liên kết trực tiếp
                            </span>
                          )}

                          {/* Direct PDF link if available */}
                          {pdfUrl && (
                            <div>
                              <a
                                href={pdfUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold hover:underline"
                              >
                                <span>PDF bản đầy đủ</span>
                                <ExternalLink className="w-2.5 h-2.5" />
                              </a>
                            </div>
                          )}

                          {/* Sources list */}
                          <div className="flex flex-wrap items-center gap-1 pt-0.5">
                            {sources.map((src, idx) => (
                              <span
                                key={idx}
                                className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-100 dark:bg-[#252320] text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700"
                              >
                                {src}
                              </span>
                            ))}
                          </div>
                        </div>
                      </td>

                      {/* Column 3: Action Button (Ingest / Remove) */}
                      <td className="px-4 py-3 align-top text-center">
                        {isInSession ? (
                          <button
                            type="button"
                            data-action="remove"
                            data-testid={`remove-ref-btn-${ref.ref_index}`}
                            disabled={isRemovingThis}
                            onClick={() => handleRemove(ref)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-red-200 dark:border-red-900/60 bg-red-50/50 hover:bg-red-100 dark:bg-red-950/30 dark:hover:bg-red-900/40 text-red-700 dark:text-red-300 text-xs font-medium transition-colors cursor-pointer disabled:opacity-50"
                          >
                            <Trash2 className="w-3 h-3 text-red-500" />
                            <span>{isRemovingThis ? "Đang xóa..." : "🗑️ Xóa khỏi chat"}</span>
                          </button>
                        ) : (
                          <button
                            type="button"
                            data-action="ingest"
                            data-testid={`ingest-ref-btn-${ref.ref_index}`}
                            disabled={isCapacityExceeded || isIngestingThis}
                            title={
                              isCapacityExceeded
                                ? "Phiên đọc đã đạt giới hạn tối đa 5 bài báo"
                                : "Nạp bài báo tham khảo vào phiên đọc sâu"
                            }
                            onClick={() => handleIngest(ref.ref_index)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-medium shadow-xs transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                          >
                            {isIngestingThis ? (
                              <>
                                <RefreshCw className="w-3 h-3 animate-spin" />
                                <span>Đang nạp...</span>
                              </>
                            ) : (
                              <>
                                <Plus className="w-3 h-3" />
                                <span>➕ Thêm vào chat</span>
                              </>
                            )}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Footer Actions & Capacity Constraint */}
        <div className="p-4 border-t border-hairline dark:border-[#2f2b26] bg-[#fbf9f5] dark:bg-[#1a1917] space-y-3 shrink-0">
          {/* Warning Banner if capacity exceeded */}
          {isCapacityExceeded && (
            <div
              role="alert"
              data-testid="capacity-warning-banner"
              className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700/60 text-amber-900 dark:text-amber-200 text-xs flex items-center gap-2.5 animate-in fade-in"
            >
              <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600 dark:text-amber-400" />
              <span className="leading-snug">
                Phiên đọc đã đạt giới hạn tối đa 5 bài báo. Vui lòng đóng bớt một bài báo trên thanh Tab trước khi nạp thêm.
              </span>
            </div>
          )}

          {/* Ingestion error alert */}
          {ingestError && (
            <div
              role="alert"
              className="p-2.5 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-300 dark:border-red-800 text-red-800 dark:text-red-300 text-xs flex items-center gap-2"
            >
              <AlertTriangle className="w-4 h-4 shrink-0 text-red-600" />
              <span>{ingestError}</span>
            </div>
          )}

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            {/* Session Capacity Counter */}
            <div
              data-testid="session-capacity-info"
              className="text-xs text-muted dark:text-zinc-400"
            >
              Đang mở:{" "}
              <strong className="text-ink dark:text-zinc-100 font-mono font-semibold">
                {currentDocCount}/5
              </strong>{" "}
              bài. Còn trống:{" "}
              <strong className="text-ink dark:text-zinc-100 font-mono font-semibold">
                {remainingCapacity}
              </strong>{" "}
              bài.
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-2.5">
              <button
                type="button"
                data-testid="close-drawer-footer-btn"
                onClick={onClose}
                className="px-4 py-2 rounded-lg border border-hairline dark:border-[#38332c] hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink text-xs font-medium transition-colors cursor-pointer"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
