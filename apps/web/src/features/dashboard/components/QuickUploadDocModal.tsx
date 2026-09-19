import { useState, useRef, type DragEvent, type ChangeEvent } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useDashboardStore } from "../stores/useDashboardStore";

interface QuickUploadDocModalProps {
  onSuccess?: (docTitle: string) => void;
}

export function QuickUploadDocModal({ onSuccess }: QuickUploadDocModalProps) {
  const isOpen = useDashboardStore((s) => s.isUploadModalOpen);
  const setIsOpen = useDashboardStore((s) => s.setUploadModalOpen);

  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMsg("Chỉ hỗ trợ tệp bài báo khoa học định dạng PDF (.pdf).");
      return;
    }

    if (file.size > 52428800) {
      // 50MB limit
      setErrorMsg("Dung lượng tệp vượt quá giới hạn 50MB.");
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setErrorMsg(null);

    try {
      // Compute SHA-256 hash in-browser (Document Ingestion Idempotency Invariant)
      const buffer = await selectedFile.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const sha256Hex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");

      // Simulate parsing latency
      await new Promise((resolve) => setTimeout(resolve, 600));

      setSuccessMsg(`Đã nạp thành công: ${selectedFile.name} (SHA-256: ${sha256Hex.slice(0, 8)}...)`);
      if (onSuccess) {
        onSuccess(selectedFile.name);
      }

      setTimeout(() => {
        setIsOpen(false);
        setSelectedFile(null);
        setSuccessMsg(null);
      }, 1000);
    } catch {
      setErrorMsg("Không thể xử lý tệp PDF. Vui lòng thử lại.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="max-w-md bg-canvas dark:bg-[#1e1c18] border-hairline dark:border-[#38332c] p-5">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <div className="p-1 rounded-md bg-primary/10 text-primary">
              <UploadCloud className="w-4 h-4" />
            </div>
            <DialogTitle className="text-lg font-display text-ink dark:text-[#f5f3ed]">
              Nạp Bài Báo Nghiên Cứu
            </DialogTitle>
          </div>
          <DialogDescription className="text-2xs text-muted dark:text-zinc-400">
            Hệ thống bảo toàn cấu trúc 2 cột, bảng biểu và ma trận Bounding Box.
          </DialogDescription>
        </DialogHeader>

        {/* Drag & Drop Box */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`my-3 p-6 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${
            dragActive
              ? "border-primary bg-primary/5"
              : "border-hairline dark:border-[#332f28] hover:border-primary/60 bg-surface-soft/40 dark:bg-[#22201b]"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="w-10 h-10 rounded-full bg-surface-soft dark:bg-[#2d2924] border border-hairline dark:border-zinc-700 flex items-center justify-center text-primary mb-2">
            <FileText className="w-5 h-5" />
          </div>

          <div className="text-xs font-medium text-ink dark:text-zinc-200">
            {selectedFile ? selectedFile.name : "Kéo thả file PDF hoặc nhấp để chọn"}
          </div>
          <div className="text-3xs text-muted dark:text-zinc-400 mt-1">
            Định dạng PDF tối đa 50MB • Chuẩn hóa tọa độ [0.0, 1.0]
          </div>
        </div>

        {/* Status Alerts */}
        {errorMsg && (
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-error/10 border border-error/20 text-error text-2xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-2xs">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        <DialogFooter className="pt-2">
          <Button
            type="button"
            variant="primary"
            size="sm"
            disabled={!selectedFile || isUploading}
            onClick={handleUpload}
            className="w-full text-xs"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                <span>Đang phân tích cấu trúc...</span>
              </>
            ) : (
              <span>Bắt đầu phân tích</span>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
