import { Activity } from "lucide-react";
import { DemoPaperViewer } from "./DemoPaperViewer";
import { DemoChatPanel } from "./DemoChatPanel";
import { useLandingStore } from "../stores/useLandingStore";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";

export function InteractiveDemo() {
  const activePaperId = useLandingStore((s) => s.activePaperId);
  const activePaper = MOCK_DEMO_PAPERS.find((p) => p.id === activePaperId) || MOCK_DEMO_PAPERS[0];

  return (
    <section id="interactive-demo" className="relative py-12 md:py-20 overflow-hidden scroll-mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10">
        {/* Customer-First Section Heading - Clean & Clear Value */}
        <div className="text-center max-w-2xl mx-auto mb-8">
          <div className="inline-flex items-center gap-1.5 mb-3 px-3 py-1 rounded-full bg-[#1e1d1a]/80 border border-[#38342e] text-xs font-mono text-[#e8a55a] shadow-sm backdrop-blur-sm">
            <Activity className="w-3.5 h-3.5 text-[#d97757] animate-pulse" />
            <span>Trải nghiệm Trực tiếp</span>
          </div>

          <h2 className="font-display text-3xl sm:text-4xl md:text-[44px] font-normal text-ink tracking-tight leading-[1.15]">
            Đọc Sâu & Đối Thoại Có Căn Cứ
          </h2>

          <p className="mt-2 text-sm sm:text-base text-body font-sans max-w-md mx-auto">
            Đối thoại trực tiếp với tài liệu — kiểm chứng chính xác từng luận điểm trên trang giấy gốc.
          </p>
        </div>

        {/* Mac Studio Window Wrapper - Warm Anthracite Tone */}
        <div className="rounded-2xl border border-[#36322b] bg-[#1c1b18] shadow-2xl overflow-hidden">
          {/* Mac Studio Window Top Bar - Clean & Dignified */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-[#22201d] border-b border-[#2d2a25]">
            {/* macOS Window Control Dots */}
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#ff5f56] border border-[#e0443e]" />
              <div className="w-3 h-3 rounded-full bg-[#ffbd2e] border border-[#dea123]" />
              <div className="w-3 h-3 rounded-full bg-[#27c93f] border border-[#1aab29]" />
            </div>

            {/* Dynamic Document Name Pill */}
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#181715] border border-[#2d2a25] text-xs font-mono text-zinc-300">
              <span className="w-1.5 h-1.5 rounded-full bg-[#d97757]" />
              <span>{activePaper.title} ({activePaper.venue_year})</span>
            </div>

            <div className="w-12" />
          </div>

          {/* Dual-Pane Studio Body */}
          <div className="p-3 sm:p-4 bg-[#181715]">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 sm:gap-4 h-[640px] sm:h-[660px]">
              {/* Left Column: PDF Paper Canvas Viewer (7 cols) */}
              <div className="lg:col-span-7 h-full min-h-[300px]">
                <DemoPaperViewer />
              </div>

              {/* Right Column: Socratic AI Chat Workspace (5 cols) */}
              <div className="lg:col-span-5 h-full min-h-[320px]">
                <DemoChatPanel />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
