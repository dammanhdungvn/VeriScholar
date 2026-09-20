import { useState, useRef, type DragEvent, type ChangeEvent, type MouseEvent } from "react";
import { FileUp, AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";

interface HeroUploadDropzoneProps {
  onIngest: (file: File) => void | Promise<void>;
}

export function HeroUploadDropzone({ onIngest }: HeroUploadDropzoneProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  const documentStatus = useWorkspaceStore((s) => s.documentStatus);
  const uploadProgress = useWorkspaceStore((s) => s.uploadProgress);
  const statusStage = useWorkspaceStore((s) => s.statusStage);
  const errorMessage = useWorkspaceStore((s) => s.errorMessage);
  const resetWorkspace = useWorkspaceStore((s) => s.resetWorkspace);

  const isProcessing =
    documentStatus === "uploading" ||
    documentStatus === "validating" ||
    documentStatus === "parsing";

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current || isProcessing || isDragActive) return;
    const rect = cardRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const mouseX = e.clientX - centerX;
    const mouseY = e.clientY - centerY;
    // Calculate tilt: max 5 degrees
    const rotateY = Math.max(-5, Math.min(5, (mouseX / (rect.width / 2)) * 5));
    const rotateX = Math.max(-5, Math.min(5, -(mouseY / (rect.height / 2)) * 5));
    setTilt({ x: rotateX, y: rotateY });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
      setTilt({ x: 0, y: 0 });
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    setTilt({ x: 0, y: 0 });
    if (isProcessing) return;

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processSelectedFile(e.target.files[0]);
    }
  };

  const processSelectedFile = (file: File) => {
    onIngest(file);
  };

  return (
    <div
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="w-full max-w-xl mx-auto flex flex-col items-center justify-center p-4 relative z-10 select-none"
      style={{ perspective: 1000 }}
    >
      {/* 1. Concentric Gravitational Halo Rings */}
      <div
        className={`absolute -inset-4 rounded-3xl border pointer-events-none transition-all duration-500 ${
          isDragActive
            ? "scale-105 border-[#cc785c]/60 shadow-[0_0_35px_rgba(204,120,92,0.3)] opacity-100"
            : "border-[#cc785c]/20 scale-100 opacity-60"
        }`}
      />
      <div
        className={`absolute -inset-8 rounded-[36px] border border-dashed pointer-events-none transition-all duration-700 ${
          isDragActive
            ? "scale-110 border-[#cc785c]/40 opacity-100"
            : "border-[#cc785c]/10 scale-100 opacity-40"
        }`}
      />

      {/* 2. Main 3D Floating Parchment Card */}
      <div
        ref={cardRef}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => {
          if (!isProcessing && documentStatus !== "error") {
            fileInputRef.current?.click();
          }
        }}
        style={{
          transform: isDragActive
            ? "rotateX(0deg) rotateY(0deg) scale(1.02)"
            : `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale(1)`,
          transition: isDragActive
            ? "transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s, box-shadow 0.2s"
            : "transform 0.12s ease-out, border-color 0.2s, box-shadow 0.2s",
        }}
        className={`w-full min-h-[290px] rounded-2xl border-2 transition-all duration-200 flex flex-col items-center justify-center p-8 text-center cursor-pointer relative overflow-hidden backdrop-blur-xl shadow-lg ${
          isDragActive
            ? "border-[#cc785c] bg-[#cc785c]/10 shadow-[0_20px_50px_rgba(204,120,92,0.25)]"
            : "border-[#e6dfd8] dark:border-[#2a2824] bg-white/90 dark:bg-[#1c1b18]/90 hover:border-[#cc785c]/70 hover:shadow-[0_20px_45px_rgba(204,120,92,0.15)]"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          className="hidden"
          data-testid="hero-file-input"
          onChange={handleFileInputChange}
          disabled={isProcessing}
        />

        {/* 4 Architectural Precision Coordinate Brackets */}
        <span className="absolute top-3 left-3 w-3 h-3 border-t-2 border-l-2 border-[#cc785c]/40 rounded-tl-xs pointer-events-none" />
        <span className="absolute top-3 right-3 w-3 h-3 border-t-2 border-r-2 border-[#cc785c]/40 rounded-tr-xs pointer-events-none" />
        <span className="absolute bottom-3 left-3 w-3 h-3 border-b-2 border-l-2 border-[#cc785c]/40 rounded-bl-xs pointer-events-none" />
        <span className="absolute bottom-3 right-3 w-3 h-3 border-b-2 border-r-2 border-[#cc785c]/40 rounded-br-xs pointer-events-none" />

        {/* Dynamic State Overlay */}
        {documentStatus === "error" ? (
          <div
            className="flex flex-col items-center justify-center space-y-3.5 max-w-md animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-12 h-12 rounded-full bg-red-500/10 text-red-500 flex items-center justify-center">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div className="space-y-1 text-center">
              <h3 className="text-base font-semibold text-red-600 dark:text-red-400">
                Lỗi xử lý
              </h3>
              <p className="text-xs sm:text-sm text-ink-muted dark:text-[#a09e99] leading-relaxed">
                {errorMessage}
              </p>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => resetWorkspace()}
              className="border-red-200 dark:border-red-900/50 hover:bg-red-50 dark:hover:bg-red-950/30 gap-1.5 text-xs"
            >
              <RotateCcw className="w-3.5 h-3.5 text-red-500" />
              Thử lại
            </Button>
          </div>
        ) : isProcessing ? (
          <div
            className="flex flex-col items-center justify-center w-full max-w-sm space-y-5 animate-in fade-in duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative flex items-center justify-center">
              <div className="w-14 h-14 rounded-full border-3 border-[#cc785c]/20 border-t-[#cc785c] animate-spin" />
              <FileUp className="w-6 h-6 text-[#cc785c] absolute" />
            </div>

            <div className="w-full space-y-2">
              <div className="flex justify-between text-xs text-ink-muted dark:text-[#a09e99]">
                <span className="font-medium truncate max-w-[240px]">
                  {statusStage || "Đang xử lý..."}
                </span>
                <span className="font-mono font-semibold text-[#cc785c]">
                  {uploadProgress}%
                </span>
              </div>
              <div className="w-full h-1.5 bg-neutral-200 dark:bg-[#2a2824] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#cc785c] transition-all duration-300 rounded-full"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center space-y-3.5">
            {/* Coral Brand Icon with Pulse Ripple */}
            <div className="relative flex items-center justify-center">
              <span className="absolute w-14 h-14 rounded-2xl bg-[#cc785c]/10 animate-ping opacity-25" />
              <div className="w-14 h-14 rounded-2xl bg-[#cc785c]/15 text-[#cc785c] flex items-center justify-center transition-transform group-hover:scale-105 shadow-2xs">
                <FileUp className="w-7 h-7" />
              </div>
            </div>

            {/* Concise Editorial Copy */}
            <div className="space-y-1">
              <h2 className="text-xl sm:text-2xl font-serif font-bold text-ink dark:text-[#f3f2ef] tracking-tight">
                {isDragActive ? "Thả tệp để bắt đầu" : "Tải lên bài báo"}
              </h2>
              <p className="text-xs sm:text-sm font-sans text-ink-muted dark:text-[#a09e99]">
                Kéo thả hoặc chọn tệp PDF
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
