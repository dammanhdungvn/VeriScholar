import { Target, Sparkles, ShieldCheck } from "lucide-react";
import { DemoPaperViewer } from "./DemoPaperViewer";
import { DemoChatPanel } from "./DemoChatPanel";
import { useLandingStore } from "../stores/useLandingStore";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";

export function InteractiveDemo() {
  const activePaperId = useLandingStore((s) => s.activePaperId);
  const activePaper = MOCK_DEMO_PAPERS.find((p) => p.id === activePaperId) || MOCK_DEMO_PAPERS[0];

  return (
    <section id="interactive-demo" className="relative pb-16 sm:pb-24 overflow-hidden scroll-mt-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10">
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
              <span>{activePaper.title}</span>
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

        {/* 3 Core Value Cards Distilled from PRD */}
        <div id="features" className="w-full grid grid-cols-1 sm:grid-cols-3 gap-4 mt-12 text-left">
          <div className="p-5 rounded-2xl bg-surface-card/60 border border-hairline hover:border-primary/40 hover:-translate-y-0.5 transition-all duration-300 shadow-2xs group">
            <Target className="w-5 h-5 text-primary mb-3 group-hover:scale-105 transition-transform" />
            <h3 className="text-sm font-semibold text-ink mb-1.5">Visual Grounding</h3>
            <p className="text-xs text-body leading-relaxed">Đối soát tức thì từng công thức, bảng biểu và số liệu trên trang PDF gốc. Triệt tiêu hoàn toàn rủi ro bịa nguồn.</p>
          </div>

          <div className="p-5 rounded-2xl bg-surface-card/60 border border-hairline hover:border-accent-amber/40 hover:-translate-y-0.5 transition-all duration-300 shadow-2xs group">
            <Sparkles className="w-5 h-5 text-accent-amber mb-3 group-hover:scale-105 transition-transform" />
            <h3 className="text-sm font-semibold text-ink mb-1.5">Socratic Copilot</h3>
            <p className="text-xs text-body leading-relaxed">Phát hiện tiền đề sai lệch, uốn nắn ngộ nhận và dẫn dắt đào sâu bản chất phương pháp thay vì suy diễn vô căn cứ.</p>
          </div>

          <div className="p-5 rounded-2xl bg-surface-card/60 border border-hairline hover:border-success/40 hover:-translate-y-0.5 transition-all duration-300 shadow-2xs group">
            <ShieldCheck className="w-5 h-5 text-success mb-3 group-hover:scale-105 transition-transform" />
            <h3 className="text-sm font-semibold text-ink mb-1.5">Zero-Retention</h3>
            <p className="text-xs text-body leading-relaxed">Bảo vệ toàn vẹn bản thảo chưa công bố: cam kết không dùng dữ liệu để huấn luyện AI, xóa sạch vĩnh viễn theo yêu cầu.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
