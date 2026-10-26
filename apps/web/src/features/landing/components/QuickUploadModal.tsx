import * as React from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useLandingStore } from "../stores/useLandingStore";
import { useQuickUploadDocument } from "../hooks/useLandingApi";

export function QuickUploadModal() {
  const isUploadModalOpen = useLandingStore((s) => s.isUploadModalOpen);
  const setUploadModalOpen = useLandingStore((s) => s.setUploadModalOpen);

  const [dragActive, setDragActive] = React.useState(false);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [successInfo, setSuccessInfo] = React.useState<{ id: string; filename: string } | null>(null);

  const uploadMutation = useQuickUploadDocument();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    setErrorMessage(null);
    setSuccessInfo(null);

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Chỉ hỗ trợ định dạng tệp PDF bài báo khoa học (.pdf).");
      return;
    }

    if (file.size > 52428800) {
      // 50MB
      setErrorMessage("Tệp PDF vượt quá dung lượng tối đa cho phép (50MB).");
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      const result = await uploadMutation.mutateAsync(selectedFile);
      setSuccessInfo(result);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Đã xảy ra lỗi trong quá trình tải lên.";
      setErrorMessage(msg);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setErrorMessage(null);
    setSuccessInfo(null);
    setUploadModalOpen(false);
  };

  return (
    <Dialog open={isUploadModalOpen} onOpenChange={setUploadModalOpen}>
      <DialogContent className="max-w-md sm:max-w-lg bg-canvas border border-hairline p-6 rounded-xl">
        <DialogHeader>
          <DialogTitle className="font-display text-2xl text-ink font-normal">
            Bắt Đầu Đọc Sâu Bài Báo
          </DialogTitle>
          <DialogDescription className="text-xs sm:text-sm text-muted font-sans mt-1">
            Tải lên bản thảo hoặc bài báo khoa học PDF để bắt đầu đối thoại có bảo chứng Bounding Box.
          </DialogDescription>
        </DialogHeader>

        {/* Upload State or Success State */}
        {!successInfo ? (
          <div className="space-y-4 pt-2">
            {/* Drop Zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-6 sm:p-8 text-center transition-all cursor-pointer ${
                dragActive
                  ? "border-primary bg-primary/5"
                  : "border-hairline bg-surface-soft hover:bg-surface-card"
              }`}
              onClick={() => document.getElementById("pdf-file-input")?.click()}
            >
              <input
                id="pdf-file-input"
                type="file"
                accept=".pdf,application/pdf"
                className="hidden"
                onChange={handleFileChange}
              />

              <div className="w-12 h-12 rounded-full bg-canvas border border-hairline flex items-center justify-center mx-auto text-primary mb-3 shadow-2xs">
                <UploadCloud className="w-6 h-6" />
              </div>

              {selectedFile ? (
                <div className="space-y-1">
                  <div className="flex items-center justify-center gap-1.5 text-sm font-sans font-medium text-ink">
                    <FileText className="w-4 h-4 text-primary" />
                    <span className="truncate max-w-[280px]">{selectedFile.name}</span>
                  </div>
                  <p className="text-xs text-muted font-mono">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div className="space-y-1">
                  <p className="text-sm font-sans font-medium text-ink">
                    Kéo thả tệp PDF vào đây, hoặc <span className="text-primary underline">chọn từ máy tính</span>
                  </p>
                  <p className="text-xs text-muted font-sans">
                    Hỗ trợ tệp PDF tối đa 50MB
                  </p>
                </div>
              )}
            </div>

            {/* Error Message if any */}
            {errorMessage && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md flex items-start gap-2 text-xs text-red-700">
                <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-2 pt-2">
              <Button variant="secondary" size="md" onClick={handleClose}>
                Hủy bỏ
              </Button>
              <Button
                variant="primary"
                size="md"
                disabled={!selectedFile || uploadMutation.isPending}
                onClick={handleUpload}
                className="min-w-[120px]"
              >
                {uploadMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Đang nạp...</span>
                  </>
                ) : (
                  <span>Nạp Bài Báo</span>
                )}
              </Button>
            </div>
          </div>
        ) : (
          /* Success Screen */
          <div className="pt-4 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-green-100 border border-green-200 flex items-center justify-center mx-auto text-success">
              <CheckCircle2 className="w-6 h-6" />
            </div>

            <div>
              <h3 className="font-display text-xl text-ink font-normal">
                Nạp Tài Liệu Thành Công!
              </h3>
              <p className="text-xs sm:text-sm text-body font-sans mt-1">
                Tài liệu <strong className="font-medium text-ink">{successInfo.filename}</strong> đã sẵn sàng cho quy trình đọc sâu và bóc tách Bounding Box.
              </p>
            </div>

            <div className="pt-3 flex justify-center gap-3">
              <Button variant="primary" size="md" onClick={handleClose}>
                Mở Trong Không Gian Nghiên Cứu
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
