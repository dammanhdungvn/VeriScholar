import { useState, useEffect } from "react";
import {
  FileText,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";

interface WritingPreviewPaneProps {
  onSelectionAddToChat?: (selectedText: string) => void;
}

export function WritingPreviewPane({
  onSelectionAddToChat: _onSelectionAddToChat,
}: WritingPreviewPaneProps) {
  const {
    activeDraftId,
    previewPdfBlobUrl,
    setPreviewPdfBlobUrl,
    isCompiling,
  } = useWritingStore();

  const [zoomLevel, setZoomLevel] = useState(100);
  const [loadError, setLoadError] = useState<string | null>(null);


  // Load preview PDF when activeDraftId changes or after compile
  useEffect(() => {
    let active = true;
    if (!activeDraftId) return;

    async function loadPdf() {
      try {
        setLoadError(null);
        const blob = await draftsApi.getPreviewPdfBlob(activeDraftId!);
        if (active) {
          const url = URL.createObjectURL(blob);
          setPreviewPdfBlobUrl(url);
        }
      } catch {
        if (active) {
          setLoadError("Chưa có bản xem trước. Hãy bấm 'Biên dịch' để tạo PDF.");
        }
      }

    }

    loadPdf();

    return () => {
      active = false;
    };
  }, [activeDraftId, setPreviewPdfBlobUrl]);

  const handleZoomIn = () => setZoomLevel((z) => Math.min(z + 15, 200));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(z - 15, 50));
  const handleResetZoom = () => setZoomLevel(100);

  const effectivePdfUrl =
    previewPdfBlobUrl ||
    (activeDraftId ? draftsApi.getPreviewPdfUrl(activeDraftId) : null);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#f4f2ed] dark:bg-[#121110] border-r border-[#e8e4dc] dark:border-[#2e2b26] overflow-hidden relative">
      {/* Sub-header Controls */}
      <div className="h-9 px-4 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1e1c19] flex items-center justify-between text-xs text-muted dark:text-zinc-400 select-none">
        <div className="flex items-center gap-2 font-mono">
          <FileText className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
          <span>Bản Dựng PDF Trực Tiếp</span>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={handleZoomOut}
            className="p-1 rounded hover:bg-[#ece8df] dark:hover:bg-[#282623] transition-colors cursor-pointer"
            title="Thu nhỏ"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={handleResetZoom}
            className="text-[11px] font-mono px-1.5 py-0.5 rounded hover:bg-[#ece8df] dark:hover:bg-[#282623] transition-colors cursor-pointer"
            title="Đặt lại 100%"
          >
            {zoomLevel}%
          </button>
          <button
            type="button"
            onClick={handleZoomIn}
            className="p-1 rounded hover:bg-[#ece8df] dark:hover:bg-[#282623] transition-colors cursor-pointer"
            title="Phóng to"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Preview Container */}
      <div className="flex-1 overflow-auto flex items-center justify-center p-4 relative">
        {isCompiling ? (
          <div className="flex flex-col items-center gap-2 text-muted dark:text-zinc-400">
            <RefreshCw className="w-6 h-6 animate-spin text-coral-500" />
            <span className="text-xs font-anthropic-serif">Đang biên dịch bản thảo trong sandbox...</span>
          </div>
        ) : loadError ? (
          <div className="flex flex-col items-center gap-2 text-center max-w-sm p-6 rounded-xl bg-white/60 dark:bg-[#1a1917]/60 border border-[#e2dcd2] dark:border-[#2e2b26]">
            <AlertCircle className="w-8 h-8 text-amber-500 mb-1" />
            <span className="text-xs font-medium text-ink dark:text-zinc-200">{loadError}</span>
            <span className="text-[11px] text-muted dark:text-zinc-400">
              Biên dịch mã nguồn LaTeX sang PDF để kích hoạt đồng bộ hiển thị và trích dẫn.
            </span>
          </div>
        ) : effectivePdfUrl ? (
          <div
            className="w-full h-full relative flex items-center justify-center transition-all duration-200"
            style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: "top center" }}
          >
            <object
              data={effectivePdfUrl}
              type="application/pdf"
              className="w-full h-full rounded shadow-md border border-[#e2dcd2] dark:border-[#2e2b26]"
            >
              <iframe
                src={effectivePdfUrl}
                title="Draft PDF Preview"
                className="w-full h-full rounded border-0"
              />
            </object>
          </div>
        ) : (
          <div className="text-xs text-muted dark:text-zinc-500">
            Chưa có tài liệu được chọn.
          </div>
        )}
      </div>
    </div>
  );
}
