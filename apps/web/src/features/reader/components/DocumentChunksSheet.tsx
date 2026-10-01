import { useState } from "react";
import {
  X,
  Layers,
  ChevronLeft,
  ChevronRight,
  FileText,
  Search,
  Maximize2,
  Cpu,
  ArrowUpRight,
  Database,
} from "lucide-react";
import {
  useDocumentChunks,
  useChunkDetail,
} from "@/features/documents/hooks/useDocumentQueries";
import type { BoundingBox } from "@/types/dashboard";
import { cn } from "@/lib/utils";

interface DocumentChunksSheetProps {
  documentId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onNavigatePage: (page: number) => void;
  onHighlightBbox?: (bbox: BoundingBox) => void;
}

export function DocumentChunksSheet({
  documentId,
  isOpen,
  onClose,
  onNavigatePage,
  onHighlightBbox,
}: DocumentChunksSheetProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [filterPdfPage, setFilterPdfPage] = useState<string>("");
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null);

  const pageNumFilter = filterPdfPage.trim() ? Number(filterPdfPage) : undefined;

  const { data: chunksResponse, isLoading: isChunksLoading } = useDocumentChunks(
    documentId,
    {
      page: currentPage,
      per_page: 8,
      page_number: Number.isFinite(pageNumFilter) ? pageNumFilter : undefined,
      include_content: true,
    }
  );

  const { data: chunkDetail, isLoading: isDetailLoading } = useChunkDetail(
    documentId,
    selectedChunkId
  );

  if (!isOpen) return null;

  const chunks = chunksResponse?.data || [];
  const meta = chunksResponse?.meta;
  const totalChunks = meta?.total ?? chunks.length;
  const totalChunkPages = meta?.total_pages ?? Math.max(1, Math.ceil(totalChunks / 8));

  const handleSelectChunk = (chunkId: string, bboxes?: BoundingBox[], page?: number) => {
    setSelectedChunkId(chunkId);
    if (page && page > 0) {
      onNavigatePage(page);
    }
    if (bboxes && bboxes.length > 0 && onHighlightBbox) {
      onHighlightBbox(bboxes[0]);
    }
  };

  return (
    <div
      role="dialog"
      aria-label="Danh sách phân đoạn bằng chứng (Chunks)"
      className="absolute inset-y-0 right-0 w-96 max-w-full bg-surface-card dark:bg-[#1e1d1a] border-l border-hairline dark:border-[#2f2b26] shadow-xl z-20 flex flex-col animate-in slide-in-from-right duration-200"
    >
      {/* Header */}
      <div className="h-11 px-4 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2 text-xs font-serif font-semibold text-ink dark:text-zinc-100">
          <Layers className="w-4 h-4 text-primary" />
          <span>Phân đoạn bằng chứng (Chunks)</span>
          {totalChunks > 0 && (
            <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-primary/10 text-primary">
              {totalChunks}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Đóng danh sách Chunks"
          className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="p-3 border-b border-hairline dark:border-[#2f2b26] flex items-center gap-2 bg-surface-soft/40 dark:bg-[#181715]/40 shrink-0">
        <div className="relative flex-1">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted" />
          <input
            type="number"
            min={1}
            value={filterPdfPage}
            onChange={(e) => {
              setFilterPdfPage(e.target.value);
              setCurrentPage(1);
            }}
            placeholder="Lọc theo trang PDF..."
            className="w-full pl-8 pr-2.5 py-1 text-xs rounded-md bg-canvas dark:bg-[#252320] border border-hairline dark:border-[#38332c] text-ink dark:text-zinc-200 placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        {filterPdfPage && (
          <button
            type="button"
            onClick={() => setFilterPdfPage("")}
            className="text-[11px] text-muted hover:text-ink px-1.5 py-1"
          >
            Xóa lọc
          </button>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5 text-xs">
        {selectedChunkId && (
          /* Selected Chunk Detail View */
          <div className="mb-3 p-3 rounded-lg bg-surface-cream-strong dark:bg-[#252320] border border-primary/30 shadow-xs space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 font-mono text-[11px] font-semibold text-primary">
                <Database className="w-3.5 h-3.5" />
                <span>Chi tiết Chunk {chunkDetail ? `#${chunkDetail.chunk_index}` : ""}</span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedChunkId(null)}
                className="text-[10px] text-muted hover:text-ink cursor-pointer"
              >
                Đóng chi tiết
              </button>
            </div>

            {isDetailLoading ? (
              <p className="text-muted text-center py-3">Đang nạp chi tiết vector...</p>
            ) : chunkDetail ? (
              <div className="space-y-2 font-mono text-[11px]">
                <div className="flex flex-wrap items-center gap-2 text-muted text-[10px]">
                  <span>Trang PDF: <strong className="text-ink dark:text-zinc-200">{chunkDetail.page_number}</strong></span>
                  <span>•</span>
                  <span>Tokens: <strong className="text-ink dark:text-zinc-200">{chunkDetail.token_count}</strong></span>
                  {chunkDetail.embedding_dimension && (
                    <>
                      <span>•</span>
                      <span>Dim: <strong className="text-ink dark:text-zinc-200">{chunkDetail.embedding_dimension}D</strong></span>
                    </>
                  )}
                </div>

                <div className="p-2.5 rounded bg-canvas dark:bg-[#1a1917] border border-hairline dark:border-[#332f29] font-serif text-[11.5px] leading-relaxed text-ink dark:text-zinc-200 whitespace-pre-wrap max-h-48 overflow-y-auto">
                  {chunkDetail.content}
                </div>

                {chunkDetail.bounding_boxes && chunkDetail.bounding_boxes.length > 0 && (
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-sans text-muted">Vùng toạ độ (Bounding Boxes):</span>
                    <div className="flex flex-wrap gap-1">
                      {chunkDetail.bounding_boxes.map((bbox, bIdx) => (
                        <button
                          key={bIdx}
                          type="button"
                          onClick={() => {
                            onNavigatePage(bbox[4]);
                            onHighlightBbox?.(bbox);
                          }}
                          className="px-2 py-0.5 rounded text-[10px] bg-primary/10 text-primary border border-primary/20 hover:bg-primary hover:text-white transition-colors flex items-center gap-1 cursor-pointer"
                        >
                          <Maximize2 className="w-2.5 h-2.5" />
                          <span>Tr.{bbox[4]} [{bbox.slice(0, 4).map((n) => n.toFixed(2)).join(", ")}]</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        )}

        {isChunksLoading ? (
          <div className="text-center py-8 text-muted space-y-2">
            <Cpu className="w-6 h-6 mx-auto animate-spin text-primary" />
            <p>Đang tải danh sách chunks...</p>
          </div>
        ) : chunks.length === 0 ? (
          <div className="text-center py-8 text-muted space-y-1">
            <Layers className="w-6 h-6 mx-auto opacity-40 mb-2" />
            <p className="font-medium text-ink dark:text-zinc-300">Không tìm thấy chunk nào</p>
            <p className="text-[11px]">
              {pageNumFilter ? `Không có đoạn trích trên trang ${pageNumFilter}` : "Tài liệu chưa hoàn tất bóc tách layout chunking"}
            </p>
          </div>
        ) : (
          chunks.map((chunk) => {
            const isSelected = selectedChunkId === chunk.id;
            return (
              <div
                key={chunk.id}
                onClick={() => handleSelectChunk(chunk.id, chunk.bounding_boxes, chunk.page_number)}
                className={cn(
                  "p-2.5 rounded-lg border transition-all cursor-pointer group text-left",
                  isSelected
                    ? "bg-primary/5 border-primary ring-1 ring-primary/20"
                    : "bg-surface-soft/60 dark:bg-[#252320] border-hairline dark:border-[#332f29] hover:border-primary/40 hover:bg-surface-cream-strong/50"
                )}
              >
                <div className="flex items-center justify-between gap-1 mb-1.5">
                  <div className="flex items-center gap-1.5 font-mono text-[10px]">
                    <span className="font-semibold text-primary">#{chunk.chunk_index}</span>
                    <span className="text-muted">•</span>
                    <span className="text-ink dark:text-zinc-300 font-medium">Tr.{chunk.page_number}</span>
                    <span className="text-muted">•</span>
                    <span className="text-muted">{chunk.token_count} toks</span>
                  </div>

                  {chunk.bounding_boxes && chunk.bounding_boxes.length > 0 && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onNavigatePage(chunk.page_number);
                        if (onHighlightBbox && chunk.bounding_boxes[0]) {
                          onHighlightBbox(chunk.bounding_boxes[0]);
                        }
                      }}
                      title="Nhảy tới vị trí trên PDF Canvas"
                      className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-surface-card dark:bg-[#1a1917] border border-hairline dark:border-[#3d3832] text-primary hover:bg-primary hover:text-white transition-colors flex items-center gap-0.5"
                    >
                      <FileText className="w-2.5 h-2.5" />
                      <span>Tr.{chunk.page_number}</span>
                      <ArrowUpRight className="w-2.5 h-2.5" />
                    </button>
                  )}
                </div>

                {chunk.content && (
                  <p className="font-serif text-[11px] leading-relaxed text-muted line-clamp-3 group-hover:text-ink dark:group-hover:text-zinc-200 transition-colors">
                    {chunk.content}
                  </p>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Pagination Footer */}
      {totalChunkPages > 1 && (
        <div className="h-10 px-3 border-t border-hairline dark:border-[#2f2b26] flex items-center justify-between text-[11px] font-mono bg-canvas dark:bg-[#181715] shrink-0">
          <button
            type="button"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage <= 1 || isChunksLoading}
            className="p-1 rounded hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 disabled:pointer-events-none cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="text-muted">
            Trang <strong className="text-ink dark:text-zinc-200">{currentPage}</strong> / {totalChunkPages}
          </span>

          <button
            type="button"
            onClick={() => setCurrentPage((p) => Math.min(totalChunkPages, p + 1))}
            disabled={currentPage >= totalChunkPages || isChunksLoading}
            className="p-1 rounded hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 disabled:pointer-events-none cursor-pointer"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
