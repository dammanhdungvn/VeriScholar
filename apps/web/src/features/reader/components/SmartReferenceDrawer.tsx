import { useEffect, useState, useMemo } from "react";
import {
  X,
  ExternalLink,
  BookMarked,
  RefreshCw,
  AlertTriangle,
  Plus,
  Search,
  CheckCircle2,
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
  // Store fallback for document count
  const storeOpenDocIds = useReaderStore((s) => s.openDocumentIds);
  const addOpenDocument = useReaderStore((s) => s.addOpenDocument);
  const setActiveDocumentId = useReaderStore((s) => s.setActiveDocumentId);

  const effectiveOpenIds = propOpenDocumentIds ?? storeOpenDocIds;
  const currentDocCount = propCurrentDocCount ?? (effectiveOpenIds.length || 1);
  const remainingCapacity = Math.max(0, 5 - currentDocCount);

  // Local state
  const [fetchedReferences, setFetchedReferences] = useState<ResolvedReferenceCard[]>([]);
  const [ingestedIndices, setIngestedIndices] = useState<Set<number>>(new Set());
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [isFetching, setIsFetching] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isReextracting, setIsReextracting] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [ingestError, setIngestError] = useState<string | null>(null);

  // Derive active reference list without cascading effect
  const baseReferences =
    propReferences && propReferences.length > 0
      ? propReferences
      : fetchedReferences;

  const internalReferences = useMemo(() => {
    return baseReferences.map((r) =>
      ingestedIndices.has(r.ref_index) ? { ...r, is_ingested: true } : r
    );
  }, [baseReferences, ingestedIndices]);

  // Auto-resolve when drawer is opened and no references provided
  useEffect(() => {
    if (!isOpen || !documentId || (propReferences && propReferences.length > 0)) {
      return;
    }

    let isMounted = true;
    setIsFetching(true);
    setIngestError(null);
    documentsApi
      .resolveReferences(documentId)
      .then((data) => {
        if (isMounted) {
          setFetchedReferences(data);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setFetchedReferences([]);
          setIngestError(err instanceof Error ? err.message : "Không thể tải danh mục tham khảo");
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
  }, [isOpen, documentId, propReferences]);

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
    if (!searchQuery.trim()) return internalReferences;
    const q = searchQuery.toLowerCase();
    return internalReferences.filter(
      (r) =>
        r.title?.toLowerCase().includes(q) ||
        r.raw_text?.toLowerCase().includes(q) ||
        r.authors?.some((a) => a.toLowerCase().includes(q)) ||
        r.arxiv_id?.toLowerCase().includes(q) ||
        r.doi?.toLowerCase().includes(q)
    );
  }, [internalReferences, searchQuery]);

  if (!isOpen) return null;

  const selectedCount = selectedIndices.size;
  const isCapacityExceeded = currentDocCount + selectedCount > 5;
  const isAllSelected =
    filteredReferences.length > 0 &&
    filteredReferences.every(
      (r) => r.is_ingested || selectedIndices.has(r.ref_index)
    );

  const handleToggleSelectAll = () => {
    if (isAllSelected) {
      setSelectedIndices(new Set());
    } else {
      const next = new Set<number>();
      for (const r of filteredReferences) {
        if (!r.is_ingested) {
          next.add(r.ref_index);
        }
      }
      setSelectedIndices(next);
    }
  };

  const handleToggleSelect = (refIndex: number) => {
    setSelectedIndices((prev) => {
      const next = new Set(prev);
      if (next.has(refIndex)) {
        next.delete(refIndex);
      } else {
        next.add(refIndex);
      }
      return next;
    });
  };

  const handleReextractClick = async () => {
    if (isReextracting || isFetching) return;
    setIsReextracting(true);
    setIngestError(null);
    try {
      if (onReextract) {
        await onReextract();
      } else {
        const fresh = await documentsApi.resolveReferences(documentId);
        setFetchedReferences(fresh);
      }
    } catch (err) {
      setIngestError(err instanceof Error ? err.message : "Bóc tách lại thất bại");
    } finally {
      setIsReextracting(false);
    }
  };

  const handleIngest = async () => {
    if (selectedCount === 0 || isCapacityExceeded || isIngesting) return;

    const indicesToIngest = Array.from(selectedIndices);
    setIsIngesting(true);
    setIngestError(null);

    try {
      let response: SessionIngestResponse;
      if (sessionId) {
        response = await sessionsApi.ingestReferences(
          sessionId,
          documentId,
          indicesToIngest
        );
      } else {
        // Fallback response when session id is not present
        response = {
          session_id: "default-session",
          ingested_documents: indicesToIngest.map((idx) => {
            const found = internalReferences.find((r) => r.ref_index === idx);
            return {
              id: `doc-ingested-${idx}`,
              title: found?.title || `Tham khảo [${idx}]`,
              filename: `reference_${idx}.pdf`,
            };
          }),
          total_documents_in_session: currentDocCount + indicesToIngest.length,
        };
      }

      // Update local ingested status
      setIngestedIndices((prev) => {
        const next = new Set(prev);
        for (const idx of indicesToIngest) {
          next.add(idx);
        }
        return next;
      });

      // Add to Reader store
      for (const doc of response.ingested_documents) {
        addOpenDocument(doc.id);
      }
      if (response.ingested_documents[0]) {
        setActiveDocumentId(response.ingested_documents[0].id);
      }

      // Clear selection
      setSelectedIndices(new Set());

      // Callback
      onIngestSuccess?.(response);
    } catch (err) {
      setIngestError(
        err instanceof Error
          ? err.message
          : "Nạp tài liệu thất bại do lỗi hệ thống"
      );
    } finally {
      setIsIngesting(false);
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
      <div className="w-full max-w-4xl max-h-[90vh] bg-canvas dark:bg-[#181715] rounded-xl shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden text-ink dark:text-zinc-100">
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
              {internalReferences.length} bài
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
          <div className="relative flex-1 max-w-sm">
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
              Đã chọn:{" "}
              <strong className="text-primary font-semibold font-mono">
                {selectedCount}
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
                  {/* Column 1: Checkbox */}
                  <th scope="col" className="w-12 px-4 py-2.5 text-center">
                    <input
                      type="checkbox"
                      data-testid="select-all-checkbox"
                      checked={isAllSelected}
                      onChange={handleToggleSelectAll}
                      aria-label="Chọn tất cả / Bỏ chọn"
                      className="rounded border-zinc-300 dark:border-zinc-700 text-primary cursor-pointer focus:ring-0"
                    />
                  </th>
                  {/* Column 2: Information & Status Badge */}
                  <th scope="col" className="px-4 py-2.5">
                    Thông tin bài báo & Trạng thái
                  </th>
                  {/* Column 3: Academic Sources & External Link */}
                  <th scope="col" className="w-56 px-4 py-2.5 text-right">
                    Nguồn học thuật & Liên kết
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hairline/60 dark:divide-[#272420]">
                {filteredReferences.map((ref) => {
                  const isSelected = selectedIndices.has(ref.ref_index);
                  const isIngested = ref.is_ingested;
                  const arxivUrl = ref.arxiv_id
                    ? `https://arxiv.org/abs/${ref.arxiv_id}`
                    : null;
                  const doiUrl = ref.doi ? `https://doi.org/${ref.doi}` : null;
                  const targetUrl =
                    ref.landing_url || ref.open_access_pdf_url || arxivUrl || doiUrl || "#";
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
                        isIngested
                          ? "bg-black/[0.02] dark:bg-white/[0.02] opacity-75"
                          : isSelected
                          ? "bg-primary/[0.04] dark:bg-primary/[0.08]"
                          : "hover:bg-black/[0.015] dark:hover:bg-white/[0.02]"
                      )}
                    >
                      {/* Column 1: Checkbox */}
                      <td className="px-4 py-3 text-center align-top">
                        <input
                          type="checkbox"
                          data-testid={`ref-checkbox-${ref.ref_index}`}
                          checked={isSelected}
                          disabled={isIngested}
                          onChange={() => handleToggleSelect(ref.ref_index)}
                          aria-label={`Chọn bài ${ref.title || ref.raw_text}`}
                          className="mt-0.5 rounded border-zinc-300 dark:border-zinc-700 text-primary cursor-pointer focus:ring-0 disabled:opacity-40"
                        />
                      </td>

                      {/* Column 2: Information & Status Badge */}
                      <td className="px-4 py-3 space-y-1.5 align-top">
                        <div className="flex items-start gap-2">
                          <span className="font-mono text-[11px] font-semibold text-muted shrink-0 mt-0.5">
                            [{ref.ref_index}]
                          </span>
                          <div className="space-y-1 flex-1 min-w-0">
                            <a
                              href={targetUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="font-bold text-ink dark:text-zinc-100 hover:text-primary hover:underline line-clamp-2 leading-snug cursor-pointer inline-flex items-center gap-1"
                              title={ref.title || ref.raw_text}
                            >
                              <span>{ref.title || ref.raw_text}</span>
                              <ExternalLink className="w-3 h-3 text-muted shrink-0" />
                            </a>

                            {/* Authors & Year & Citation count */}
                            <div className="text-[11px] text-muted dark:text-zinc-400 flex flex-wrap items-center gap-x-2 gap-y-0.5 font-sans">
                              {ref.authors && ref.authors.length > 0 && (
                                <span>{ref.authors.join(", ")}</span>
                              )}
                              {ref.year && (
                                <span className="font-mono">({ref.year})</span>
                              )}
                              {ref.citation_count !== undefined &&
                                ref.citation_count !== null && (
                                  <span className="font-mono text-zinc-500">
                                    • {ref.citation_count.toLocaleString()} trích dẫn
                                  </span>
                                )}
                            </div>

                            {/* Abstract preview if available */}
                            {ref.abstract && (
                              <p className="text-[11px] text-muted dark:text-zinc-400 line-clamp-2 italic leading-relaxed pt-0.5">
                                "{ref.abstract}"
                              </p>
                            )}

                            {/* Status Badge */}
                            <div className="pt-1 flex items-center gap-2">
                              {ref.open_access_pdf_url ? (
                                <span
                                  data-testid="badge-open-access"
                                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60"
                                >
                                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                  🟢 Đã tìm thấy PDF Open-Access
                                </span>
                              ) : (
                                <span
                                  data-testid="badge-abstract-only"
                                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border border-amber-200 dark:border-amber-800/60"
                                >
                                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                  🟡 Chỉ có Abstract
                                </span>
                              )}

                              {isIngested && (
                                <span className="inline-flex items-center gap-1 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                                  <CheckCircle2 className="w-3 h-3" />
                                  Đã nạp vào phiên
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Column 3: Academic Sources & External Link */}
                      <td className="px-4 py-3 text-right align-top space-y-2">
                        {/* Source badges */}
                        <div className="flex flex-wrap items-center justify-end gap-1">
                          {sources.map((src, idx) => (
                            <span
                              key={idx}
                              className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-100 dark:bg-[#252320] text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700"
                            >
                              {src}
                            </span>
                          ))}
                        </div>

                        {/* Direct links */}
                        <div className="flex items-center justify-end gap-2 text-[11px] pt-1">
                          {ref.open_access_pdf_url && (
                            <a
                              href={ref.open_access_pdf_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 hover:underline font-semibold"
                            >
                              <span>PDF</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          )}
                          {arxivUrl && (
                            <a
                              href={arxivUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-primary hover:underline font-mono"
                            >
                              <span>arXiv</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          )}
                          {doiUrl && (
                            <a
                              href={doiUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-teal-600 dark:text-teal-400 hover:underline font-mono"
                            >
                              <span>DOI</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          )}
                        </div>
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
                Phiên đọc sâu giới hạn tối đa 5 bài báo. Vui lòng bỏ bớt bài hoặc lưu vào Thư viện (Module 4) để quản lý kho lớn hơn
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
              {selectedCount > 0 && (
                <span className="ml-1">
                  (Đã chọn:{" "}
                  <strong className="text-primary font-mono font-semibold">
                    {selectedCount}
                  </strong>
                  )
                </span>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-2.5">
              <button
                type="button"
                data-testid="cancel-drawer-btn"
                onClick={onClose}
                className="px-4 py-2 rounded-lg border border-hairline dark:border-[#38332c] hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink text-xs font-medium transition-colors cursor-pointer"
              >
                Hủy
              </button>

              <button
                type="button"
                data-testid="ingest-references-btn"
                disabled={selectedCount === 0 || isCapacityExceeded || isIngesting}
                onClick={handleIngest}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-primary hover:bg-primary-hover text-white shadow-xs transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>
                  {isIngesting
                    ? "Đang nạp bài báo..."
                    : `➕ Thêm vào Nghiên cứu (${selectedCount})`}
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
