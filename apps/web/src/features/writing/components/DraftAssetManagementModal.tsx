import { useState, useEffect, useRef } from "react";
import {
  FolderArchive,
  UploadCloud,
  FileCode,
  Image as ImageIcon,
  BookOpen,
  FileText,
  Copy,
  Check,
  X,
  Loader2,
  Plus,
  AlertCircle,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { formatBytes, generateLatexSnippet } from "../lib/assetUtils";
import type { DraftAsset, DraftAssetType, CreateDraftAssetRequest } from "../types";
import { cn } from "@/lib/utils";

export interface DraftAssetManagementModalProps {
  isOpen?: boolean;
  onClose?: () => void;
  onInsertLatex?: (snippet: string) => void;
  draftId?: string;
}

export function DraftAssetManagementModal({
  isOpen,
  onClose,
  onInsertLatex,
  draftId: propDraftId,
}: DraftAssetManagementModalProps) {
  const storeIsOpen = useWritingStore((s) => s.isAssetModalOpen);
  const storeClose = useWritingStore((s) => s.closeAssetModal);
  const activeDraftId = useWritingStore((s) => s.activeDraftId);
  const editorContent = useWritingStore((s) => s.editorContent);
  const setEditorContent = useWritingStore((s) => s.setEditorContent);
  const selectionRange = useWritingStore((s) => s.selectionRange);

  const effectiveIsOpen = isOpen !== undefined ? isOpen : storeIsOpen;
  const effectiveClose = onClose || storeClose;
  const effectiveDraftId = propDraftId || activeDraftId;

  const [assets, setAssets] = useState<DraftAsset[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [copiedAssetId, setCopiedAssetId] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>("all");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let ignore = false;
    if (effectiveIsOpen && effectiveDraftId) {
      draftsApi
        .listAssets(effectiveDraftId)
        .then((res) => {
          if (!ignore) {
            setAssets(res.items || []);
            setIsLoading(false);
          }
        })
        .catch((err) => {
          if (!ignore) {
            console.error("Failed to list draft assets:", err);
            setErrorMessage("Không thể tải danh sách assets. Vui lòng thử lại.");
            setIsLoading(false);
          }
        });
    }
    return () => {
      ignore = true;
    };
  }, [effectiveIsOpen, effectiveDraftId]);

  // Keyboard shortcut: ESC to close
  useEffect(() => {
    if (!effectiveIsOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") effectiveClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [effectiveIsOpen, effectiveClose]);

  // Determine asset_type from filename
  const getAssetTypeFromFilename = (filename: string): DraftAssetType => {
    const ext = filename.split(".").pop()?.toLowerCase();
    if (["png", "jpg", "jpeg", "webp"].includes(ext || "")) return "image";
    if (ext === "bib") return "bibtex";
    return "supplementary";
  };

  // Upload handler
  const handleUploadFile = async (file: File) => {
    if (!effectiveDraftId) return;

    // Validate extension (.png, .pdf, .bib, .cls, .sty, .jpg, .jpeg)
    const ext = file.name.split(".").pop()?.toLowerCase() || "";
    const allowed = ["png", "jpg", "jpeg", "webp", "pdf", "bib", "cls", "sty", "tex", "csv"];
    if (!allowed.includes(ext)) {
      setErrorMessage(
        `Định dạng .${ext} không được hỗ trợ. Vui lòng tải lên tệp (.png, .pdf, .bib, .cls, .sty).`
      );
      return;
    }

    try {
      setIsUploading(true);
      setErrorMessage(null);

      // Read file to base64
      const base64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const res = reader.result as string;
          const commaIndex = res.indexOf(",");
          resolve(commaIndex !== -1 ? res.slice(commaIndex + 1) : res);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      const assetType = getAssetTypeFromFilename(file.name);
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "");
      const payload: CreateDraftAssetRequest = {
        asset_type: assetType,
        filename: file.name,
        content_base64: base64,
        caption: assetType === "image" ? `Biểu đồ ${file.name}` : undefined,
        latex_label: assetType === "image" ? `fig:${nameWithoutExt}` : undefined,
      };

      const newAsset = await draftsApi.createAsset(effectiveDraftId, payload);
      setAssets((prev) => [newAsset, ...prev]);
    } catch (err) {
      console.error("Failed to upload draft asset:", err);
      setErrorMessage("Tải lên asset thất bại. Vui lòng kiểm tra lại tệp.");
    } finally {
      setIsUploading(false);
    }
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleUploadFile(file);
    }
  };

  // Copy LaTeX code to clipboard
  const handleCopySnippet = (asset: DraftAsset) => {
    const snippet = generateLatexSnippet(asset);
    navigator.clipboard.writeText(snippet);
    setCopiedAssetId(asset.id);
    setTimeout(() => setCopiedAssetId(null), 2000);
  };

  // Insert LaTeX snippet directly into editor
  const handleInsertIntoEditor = (asset: DraftAsset) => {
    const snippet = `\n${generateLatexSnippet(asset)}\n`;
    if (onInsertLatex) {
      onInsertLatex(snippet);
    } else {
      const pos = selectionRange ? selectionRange.start : editorContent.length;
      const safePos = Math.min(Math.max(0, pos), editorContent.length);
      const updated =
        editorContent.slice(0, safePos) + snippet + editorContent.slice(safePos);
      setEditorContent(updated);
    }
    effectiveClose();
  };

  if (!effectiveIsOpen) return null;

  const filteredAssets = assets.filter((asset) => {
    if (selectedFilter === "all") return true;
    if (selectedFilter === "image") return asset.asset_type === "image";
    if (selectedFilter === "bibtex") return asset.asset_type === "bibtex";
    if (selectedFilter === "other")
      return asset.asset_type !== "image" && asset.asset_type !== "bibtex";
    return true;
  });

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Quản lý assets học thuật của bản thảo"
      data-testid="draft-assets-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isUploading) effectiveClose();
      }}
    >
      <div className="w-full max-w-4xl max-h-[85vh] bg-white dark:bg-[#181715] rounded-xl shadow-2xl border border-[#e2dcd2] dark:border-[#2e2b26] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-12 px-5 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center justify-between shrink-0 bg-[#fbf9f5] dark:bg-[#1f1d1a]">
          <div className="flex items-center gap-2">
            <FolderArchive className="w-4 h-4 text-coral-600 dark:text-coral-400" />
            <span className="font-semibold text-sm text-ink dark:text-zinc-100 font-anthropic-serif">
              Quản lý Assets Học Thuật (.png, .pdf, .bib, .cls, .sty)
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded-full bg-zinc-200 dark:bg-zinc-800 text-[10px] font-mono text-zinc-700 dark:text-zinc-300">
              {assets.length} tệp
            </span>

            <button
              type="button"
              onClick={effectiveClose}
              disabled={isUploading}
              aria-label="Đóng"
              className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 cursor-pointer disabled:opacity-50"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Error Message */}
          {errorMessage && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-700 dark:text-rose-300 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
              <button
                type="button"
                onClick={() => setErrorMessage(null)}
                className="text-muted hover:text-ink"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Drag & Drop Upload Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            data-testid="asset-dropzone"
            className={cn(
              "p-6 rounded-xl border-2 border-dashed transition-all flex flex-col items-center justify-center text-center cursor-pointer select-none",
              isDragging
                ? "border-coral-500 bg-coral-500/10 scale-[1.005]"
                : "border-[#e2dcd2] dark:border-[#2e2b26] hover:border-coral-500/50 bg-[#faf8f5] dark:bg-[#1a1917]"
            )}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".png,.jpg,.jpeg,.webp,.pdf,.bib,.cls,.sty,.tex"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleUploadFile(e.target.files[0]);
                  e.target.value = "";
                }
              }}
              className="hidden"
              data-testid="asset-file-input"
            />

            {isUploading ? (
              <div className="flex flex-col items-center space-y-2 py-2">
                <Loader2 className="w-8 h-8 text-coral-500 animate-spin" />
                <span className="font-medium text-ink dark:text-zinc-200">
                  Đang mã hóa & đăng ký asset vào bản thảo...
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center space-y-1.5">
                <div className="w-10 h-10 rounded-full bg-coral-500/10 flex items-center justify-center text-coral-600 dark:text-coral-400 mb-1">
                  <UploadCloud className="w-5 h-5" />
                </div>
                <div className="font-medium text-ink dark:text-zinc-200">
                  Kéo thả tệp vào đây, hoặc{" "}
                  <span className="text-coral-600 dark:text-coral-400 underline">
                    chọn tệp từ máy tính
                  </span>
                </div>
                <p className="text-[11px] text-muted dark:text-zinc-400">
                  Hỗ trợ hình ảnh biểu đồ (.png, .jpg), trích dẫn (.bib), định dạng mẫu (.cls, .sty) và tài liệu đính kèm (.pdf)
                </p>
              </div>
            )}
          </div>

          {/* Filter Bar */}
          <div className="flex items-center justify-between border-b border-[#ece8df] dark:border-[#2a2824] pb-2 text-xs">
            <div className="flex items-center gap-1.5">
              {[
                { id: "all", label: "Tất cả" },
                { id: "image", label: "Hình ảnh (.png/.jpg)" },
                { id: "bibtex", label: "Trích dẫn (.bib)" },
                { id: "other", label: "Khác (.cls/.sty/.pdf)" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setSelectedFilter(tab.id)}
                  className={cn(
                    "px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer text-[11px]",
                    selectedFilter === tab.id
                      ? "bg-coral-500/10 text-coral-600 dark:text-coral-400 font-semibold"
                      : "text-muted hover:text-ink dark:text-zinc-400"
                  )}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <span className="text-[11px] text-zinc-400">
              Hiển thị {filteredAssets.length} / {assets.length} tệp
            </span>
          </div>

          {/* Asset List */}
          {isLoading ? (
            <div className="py-12 flex flex-col items-center justify-center text-zinc-400 space-y-2">
              <Loader2 className="w-6 h-6 animate-spin text-coral-500" />
              <span>Đang tải danh sách assets...</span>
            </div>
          ) : filteredAssets.length > 0 ? (
            <div className="space-y-2.5" data-testid="asset-list-container">
              {filteredAssets.map((asset) => {
                const ext = asset.filename.split(".").pop()?.toLowerCase() || "";
                const isImage = ["png", "jpg", "jpeg", "webp"].includes(ext) || asset.asset_type === "image";
                const isBib = ext === "bib" || asset.asset_type === "bibtex";
                const isCopied = copiedAssetId === asset.id;

                return (
                  <div
                    key={asset.id}
                    data-testid="asset-item-card"
                    className="p-3 rounded-lg bg-[#faf8f5] dark:bg-[#1a1917] border border-[#e2dcd2] dark:border-[#2e2b26] flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-coral-500/40 transition-colors"
                  >
                    {/* Left: Icon & Info */}
                    <div className="flex items-start sm:items-center gap-3 min-w-0">
                      <div className="w-9 h-9 rounded-lg bg-white dark:bg-[#252320] border border-[#e2dcd2] dark:border-[#2e2b26] flex items-center justify-center shrink-0">
                        {isImage ? (
                          <ImageIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                        ) : isBib ? (
                          <BookOpen className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                        ) : ext === "pdf" ? (
                          <FileText className="w-4 h-4 text-rose-600 dark:text-rose-400" />
                        ) : (
                          <FileCode className="w-4 h-4 text-coral-600 dark:text-coral-400" />
                        )}
                      </div>

                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-ink dark:text-zinc-100 font-mono truncate">
                            {asset.filename}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-zinc-200/60 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 font-mono">
                            {formatBytes(asset.file_size_bytes)}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 text-[11px] text-muted dark:text-zinc-400 mt-0.5">
                          {asset.caption && (
                            <span className="truncate italic">
                              "{asset.caption}"
                            </span>
                          )}
                          {asset.latex_label && (
                            <span className="font-mono text-[10px] text-coral-600 dark:text-coral-400 bg-coral-500/10 px-1 rounded">
                              \\ref&#123;{asset.latex_label}&#125;
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
                      <button
                        type="button"
                        onClick={() => handleCopySnippet(asset)}
                        data-testid="copy-latex-btn"
                        className={cn(
                          "px-2.5 py-1.5 rounded-lg border text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer",
                          isCopied
                            ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-400"
                            : "bg-white dark:bg-[#252320] border-[#e2dcd2] dark:border-[#2e2b26] text-ink dark:text-zinc-200 hover:bg-[#ece8df] dark:hover:bg-[#2d2a26]"
                        )}
                        title="Sao chép mã chèn LaTeX vào clipboard"
                      >
                        {isCopied ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-600" />
                            <span>Đã sao chép</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Sao chép mã LaTeX</span>
                          </>
                        )}
                      </button>

                      <button
                        type="button"
                        onClick={() => handleInsertIntoEditor(asset)}
                        data-testid="insert-editor-btn"
                        className="px-2.5 py-1.5 rounded-lg bg-coral-500 hover:bg-coral-600 text-white font-medium text-xs shadow-xs transition-colors flex items-center gap-1 cursor-pointer"
                        title="Chèn mã LaTeX này trực tiếp vào văn bản soạn thảo"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        <span>Chèn vào bài</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 rounded-xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] text-center space-y-2">
              <FolderArchive className="w-8 h-8 text-zinc-400 mx-auto" />
              <p className="font-medium text-ink dark:text-zinc-300">
                Chưa có asset nào trong bản thảo
              </p>
              <p className="text-[11px] text-muted dark:text-zinc-400 max-w-sm mx-auto">
                Kéo thả hình ảnh hoặc tệp .bib vào vùng tải lên ở trên để quản lý và tạo mã chèn LaTeX nhanh.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="h-12 px-5 border-t border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1f1d1a] flex items-center justify-between shrink-0 text-[11px] text-zinc-400">
          <span>
            Hỗ trợ chèn tự động các môi trường figure, bibliography và usepackage
          </span>
          <button
            type="button"
            onClick={effectiveClose}
            className="px-3 py-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#2e2b26] bg-white dark:bg-[#252320] text-ink dark:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5 font-medium cursor-pointer"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
}
