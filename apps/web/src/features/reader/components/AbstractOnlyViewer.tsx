import React, { useState, useRef } from "react";
import { Upload, ExternalLink, Loader2, AlertCircle } from "lucide-react";
import { documentsApi } from "@/features/documents/api/documentsApi";
import type { DocumentDetailResponseData } from "@/types/document";
import { cn } from "@/lib/utils";

interface AbstractOnlyViewerProps {
  document: DocumentDetailResponseData;
  onPdfAttached?: () => void;
}

export function AbstractOnlyViewer({ document, onPdfAttached }: AbstractOnlyViewerProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const title = document.title || document.filename;
  const authorsText = document.authors && document.authors.length > 0 ? document.authors.join(", ") : null;
  const publicationYear = document.publication_year;
  const abstractText =
    document.abstract ||
    document.parsed_metadata?.abstract ||
    "Chưa có thông tin tóm tắt cho bài báo này.";

  // DOI URL resolution
  const doiUrl = document.doi
    ? document.doi.startsWith("http")
      ? document.doi
      : `https://doi.org/${document.doi}`
    : null;

  // arXiv URL resolution
  const arxivId = document.parsed_metadata?.arxiv_id;
  const arxivUrl = arxivId ? `https://arxiv.org/abs/${arxivId}` : null;

  const handleProcessFile = async (file: File) => {
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setUploadError("Vui lòng chọn tệp định dạng PDF.");
      return;
    }

    setUploadError(null);
    setIsUploading(true);

    try {
      await documentsApi.attachPdf(document.id, file);
      onPdfAttached?.();
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "Không thể tải lên tệp PDF. Vui lòng thử lại.";
      setUploadError(message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleProcessFile(file);
    }
    // Reset input value to allow selecting the same file again if needed
    e.target.value = "";
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleProcessFile(file);
    }
  };

  return (
    <div className="flex-1 w-full h-full overflow-y-auto bg-[#faf8f4] dark:bg-[#141311] p-6 sm:p-10 flex justify-center">
      <div className="w-full max-w-3xl flex flex-col space-y-8 my-auto py-6">
        {/* Academic Metadata Header */}
        <header className="space-y-4 border-b border-zinc-200/80 dark:border-zinc-800 pb-6">
          <div className="flex items-center gap-2">
            <span className="text-zinc-600 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 text-xs font-medium px-2 py-0.5 rounded">
              Tóm tắt
            </span>
            {document.parsed_metadata?.venue && (
              <span className="text-zinc-500 dark:text-zinc-400 text-xs truncate max-w-md">
                {document.parsed_metadata.venue}
              </span>
            )}
          </div>

          <h2 className="font-serif font-medium text-xl sm:text-2xl text-zinc-900 dark:text-zinc-100 tracking-tight leading-snug">
            {title}
          </h2>

          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-zinc-600 dark:text-zinc-400">
            {authorsText && <span>{authorsText}</span>}
            {authorsText && publicationYear && <span>•</span>}
            {publicationYear && <span>{publicationYear}</span>}
          </div>

          {/* External Citation Links */}
          {(doiUrl || arxivUrl) && (
            <div className="flex items-center gap-3 pt-1">
              {doiUrl && (
                <a
                  href={doiUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-primary dark:text-primary-foreground/80 hover:underline"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>DOI</span>
                </a>
              )}
              {arxivUrl && (
                <a
                  href={arxivUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-primary dark:text-primary-foreground/80 hover:underline"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>arXiv</span>
                </a>
              )}
            </div>
          )}
        </header>

        {/* Abstract Content Block */}
        <section className="space-y-3">
          <h3 className="text-xs font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Tóm tắt bài báo
          </h3>
          <div className="text-ink/80 dark:text-zinc-300 leading-relaxed font-sans text-sm bg-white dark:bg-[#1a1917] p-6 rounded-lg border border-zinc-200/60 dark:border-zinc-800/80 shadow-sm whitespace-pre-line">
            {abstractText}
          </div>
        </section>

        {/* Attachment Upload Area */}
        <section className="space-y-3">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            data-testid="pdf-upload-input"
            onChange={handleFileInputChange}
            disabled={isUploading}
          />

          <div
            data-testid="pdf-dropzone"
            onClick={() => !isUploading && fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
              "border-2 border-dashed rounded-lg p-6 sm:p-8 text-center transition-colors cursor-pointer flex flex-col items-center justify-center space-y-3",
              isDragOver
                ? "border-primary bg-primary/5 dark:bg-primary/10"
                : "border-zinc-300 dark:border-zinc-700 bg-white/50 dark:bg-[#1a1917]/50 hover:border-zinc-400 dark:hover:border-zinc-500",
              isUploading && "pointer-events-none opacity-80"
            )}
          >
            {isUploading ? (
              <div className="flex flex-col items-center space-y-2 py-2">
                <Loader2 className="w-7 h-7 text-primary animate-spin" />
                <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                  Đang tải lên và xử lý...
                </p>
              </div>
            ) : (
              <>
                <div className="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-600 dark:text-zinc-300">
                  <Upload className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                    Đính kèm bản PDF đầy đủ
                  </p>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">
                    Kéo thả hoặc nhấn để chọn tệp PDF
                  </p>
                </div>
              </>
            )}
          </div>

          {uploadError && (
            <div className="flex items-center gap-2 text-xs text-amber-600 dark:text-amber-500 pt-1">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
