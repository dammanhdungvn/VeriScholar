import { ArrowRight, ShieldCheck, Target, BookOpen, CheckCircle2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLandingStore } from "../stores/useLandingStore";

export function HeroSection() {
  const setUploadModalOpen = useLandingStore((s) => s.setUploadModalOpen);

  return (
    <section className="relative pt-20 pb-12 sm:pt-28 sm:pb-16 overflow-hidden">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center relative z-10">
        {/* Keyword Category Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-card/90 border border-hairline text-xs font-mono text-body shadow-xs mb-8 backdrop-blur-md whitespace-nowrap">
          <Sparkles className="w-3.5 h-3.5 text-primary shrink-0 animate-pulse" />
          <span className="font-semibold text-ink">ISO 32000-1</span>
          <span className="text-hairline">•</span>
          <span className="text-primary font-medium">Zero-Hallucination</span>
          <span className="text-hairline">•</span>
          <span className="text-muted">ACID CAS</span>
        </div>

        {/* Display Headline with Gradient Italic Highlight */}
        <h1 className="font-display text-3xl sm:text-4xl md:text-5xl lg:text-[54px] font-normal text-ink tracking-tight leading-[1.2] max-w-5xl mx-auto mb-6">
          <span>Nền tảng Trợ lý AI Hỗ trợ Nghiên cứu</span>{" "}
          <br className="hidden sm:inline" />
          <span className="italic font-normal bg-gradient-to-r from-[#d97757] via-[#e8a55a] to-[#cc785c] bg-clip-text text-transparent">
            và Soạn thảo Khoa học
          </span>
        </h1>

        {/* Ultra-Short Keyword Lead */}
        <p className="font-sans text-base sm:text-lg md:text-xl text-body max-w-xl mx-auto leading-relaxed mb-10 font-normal">
          Bảo chứng tọa độ nhị phân. Loại bỏ hoàn toàn ảo giác học thuật.
        </p>

        {/* Action Button Row */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 sm:gap-4 mb-12">
          <Button
            variant="primary"
            size="lg"
            onClick={() => setUploadModalOpen(true)}
            data-testid="hero-quick-upload-btn"
            className="w-full sm:w-auto h-12 px-7 text-sm font-medium shadow-md group relative overflow-hidden cursor-pointer"
          >
            <span className="relative z-10 flex items-center gap-2">
              <span>Bắt đầu Nghiên cứu — Miễn phí</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </span>
            <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent pointer-events-none" />
          </Button>

          <a href="#interactive-demo" className="w-full sm:w-auto">
            <Button
              variant="secondary"
              size="lg"
              className="w-full sm:w-auto h-12 px-6 text-sm bg-surface-card/90 hover:bg-surface-cream-strong border border-hairline shadow-xs cursor-pointer"
            >
              <BookOpen className="w-4 h-4 text-muted" />
              <span>Xem Trình Diễn</span>
            </Button>
          </a>
        </div>

        {/* 3 Technical Trust Keyword Pills */}
        <div className="pt-6 border-t border-hairline/60 max-w-2xl mx-auto flex flex-wrap items-center justify-center gap-4 text-xs font-mono text-body">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-card/60 border border-hairline">
            <ShieldCheck className="w-3.5 h-3.5 text-primary shrink-0" />
            <span>Triệt tiêu 100% Ảo giác</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-card/60 border border-hairline">
            <Target className="w-3.5 h-3.5 text-accent-amber shrink-0" />
            <span>Bounding Box [0.0, 1.0]</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-card/60 border border-hairline">
            <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0" />
            <span>Zero-Retention Bản quyền</span>
          </div>
        </div>
      </div>
    </section>
  );
}
