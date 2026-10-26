import { useState, useRef } from "react";
import { X, Upload, FileText, AlertCircle, Loader2 } from "lucide-react";
import { documentsApi } from "../api/documentsApi";
import type { DocumentUploadResponseData } from "@/types/document";

export const MAX_PDF_FILE_SIZE = 50 * 1024 * 1024; // 50MB

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess?: (doc: DocumentUploadResponseData) => void;
  sessionId?: string;
}

export function DocumentUploadModal({
  isOpen,
  onClose,
  onUploadSuccess,
  sessionId,
}: DocumentUploadModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const validateAndSelectFile = (file: File) => {
    setErrorMessage(null);

    if (file.size > MAX_PDF_FILE_SIZE) {
      setErrorMessage("Dung lượng tệp vượt quá giới hạn tối đa 50MB.");
      setSelectedFile(null);
      return false;
    }

    if (file.type && file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Định dạng tệp không hợp lệ. Vui lòng chỉ tải lên tài liệu định dạng PDF.");
      setSelectedFile(null);
      return false;
    }

    setSelectedFile(file);
    return true;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSelectFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      validateAndSelectFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setIsUploading(true);
      setErrorMessage(null);
      setUploadProgress(30);

      const result = await documentsApi.uploadDocument(selectedFile, sessionId);
      setUploadProgress(100);

      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
      onClose();
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "Tải lên thất bại. Vui lòng thử lại sau."
      );
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="w-full max-w-lg rounded-2xl bg-[#fdfcf9] dark:bg-[#181715] border border-hairline shadow-2xl overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-hairline flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center">
              <Upload className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
                Tải lên tài liệu PDF
              </h2>
              <p className="text-[11px] text-muted dark:text-zinc-400">
                Hỗ trợ tệp PDF học thuật tối đa 50MB (tối đa 100 trang)
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-md text-muted hover:text-ink dark:hover:text-zinc-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          {/* Drag & Drop Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${
              isDragging
                ? "border-coral-500 bg-coral-500/5"
                : "border-hairline hover:border-zinc-400 dark:hover:border-zinc-600 bg-[#f8f6f0] dark:bg-[#1f1e1a]"
            }`}
          >
            <input
              ref={fileInputRef}
              data-testid="pdf-file-input"
              type="file"
              accept="application/pdf,.pdf"
              className="hidden"
              onChange={handleFileChange}
            />
            <div className="w-12 h-12 rounded-full bg-white dark:bg-[#282622] border border-hairline flex items-center justify-center mb-3 shadow-xs">
              <FileText className="w-6 h-6 text-coral-600 dark:text-coral-400" />
            </div>
            <p className="text-xs font-medium text-ink dark:text-zinc-200">
              Kéo thả tệp PDF vào đây hoặc <span className="text-coral-600 hover:underline">chọn từ thiết bị</span>
            </p>
            <p className="text-[11px] text-muted dark:text-zinc-400 mt-1">
              Chỉ chấp nhận tệp có lớp văn bản số hóa (Digital PDF)
            </p>
          </div>

          {/* Selected File Details */}
          {selectedFile && (
            <div className="flex items-center justify-between p-3 rounded-lg border border-hairline bg-white dark:bg-[#201f1b]">
              <div className="flex items-center gap-2.5 overflow-hidden">
                <FileText className="w-4 h-4 text-muted shrink-0" />
                <span className="text-xs font-mono text-ink dark:text-zinc-200 truncate">
                  {selectedFile.name}
                </span>
              </div>
              <span className="text-[11px] font-mono text-muted shrink-0 ml-2">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </span>
            </div>
          )}

          {/* Upload Progress Bar */}
          {isUploading && (
            <div className="space-y-1.5">
              <div className="flex justify-between text-[11px] font-mono text-muted">
                <span>Đang tải lên và tính hàm băm...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-zinc-200 dark:bg-zinc-800 overflow-hidden">
                <div
                  className="h-full bg-coral-500 transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {errorMessage && (
            <div
              role="alert"
              className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2 font-sans"
            >
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 border-t border-hairline bg-[#f8f6f0] dark:bg-[#1a1916] flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            disabled={isUploading}
            className="px-4 py-2 rounded-lg text-xs font-medium text-zinc-600 dark:text-zinc-400 hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors"
          >
            Hủy
          </button>
          <button
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className="px-4 py-2 rounded-lg text-xs font-medium bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 disabled:opacity-50 transition-colors flex items-center gap-1.5"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Đang tải lên...</span>
              </>
            ) : (
              <span>Tải lên</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
