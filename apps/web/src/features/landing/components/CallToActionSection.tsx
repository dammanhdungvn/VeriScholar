import { ArrowRight, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLandingStore } from "../stores/useLandingStore";

export function CallToActionSection() {
  const setUploadModalOpen = useLandingStore((s) => s.setUploadModalOpen);

  return (
    <section className="py-14 md:py-18 bg-canvas">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="bg-primary text-on-primary rounded-2xl p-8 sm:p-12 text-center shadow-lg relative overflow-hidden">
          {/* Subtle Background Radial Pattern */}
          <div className="absolute inset-0 opacity-10 pointer-events-none bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:16px_16px]" />

          <div className="relative z-10 max-w-2xl mx-auto">
            {/* Minimalist Headline */}
            <h2 className="font-display text-3xl sm:text-4xl md:text-5xl font-normal tracking-tight leading-tight text-white mb-3">
              Nghiên Cứu Chính Xác Tuyệt Đối.
            </h2>

            <p className="text-white/90 text-sm sm:text-base font-mono max-w-md mx-auto mb-8">
              Triệt tiêu 100% ảo giác. Bảo chứng tọa độ bài báo.
            </p>

            {/* Inverted Button on Coral Surface */}
            <div className="flex items-center justify-center">
              <Button
                variant="coral-inverted"
                size="lg"
                onClick={() => setUploadModalOpen(true)}
                className="h-12 px-8 text-sm font-medium shadow-md group cursor-pointer text-ink bg-canvas hover:bg-surface-soft"
              >
                <span>Bắt Đầu Nghiên Cứu — Miễn Phí</span>
                <ArrowRight className="w-4 h-4 text-primary transition-transform group-hover:translate-x-1" />
              </Button>
            </div>

            {/* Minimalist Footnote */}
            <div className="mt-7 pt-5 border-t border-white/20 flex items-center justify-center gap-2 text-xs text-white/80 font-mono">
              <ShieldCheck className="w-3.5 h-3.5 text-white shrink-0" />
              <span>Zero-Retention: Tuyệt đối không dùng bản thảo để huấn luyện AI.</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
