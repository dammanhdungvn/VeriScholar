import { DemoPaperViewer } from "./DemoPaperViewer";
import { DemoChatPanel } from "./DemoChatPanel";
import { useLandingStore } from "../stores/useLandingStore";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";

export function InteractiveDemo() {
  const activePaperId = useLandingStore((s) => s.activePaperId);
  const activePaper = MOCK_DEMO_PAPERS.find((p) => p.id === activePaperId) || MOCK_DEMO_PAPERS[0];

  return (
    <section id="interactive-demo" className="relative pb-16 sm:pb-24 overflow-hidden scroll-mt-20">
      <div className="max-w-7xl xl:max-w-[1380px] mx-auto px-4 sm:px-6 relative z-10">
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

          {/* Dual-Pane Studio Body: Expansive 50/50 Split with Ample Space */}
          <div className="p-3 sm:p-4 lg:p-5 bg-[#181715]">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-5 min-h-[640px] lg:h-[760px]">
              {/* Left Column: PDF Paper Canvas Viewer */}
              <div className="h-[540px] lg:h-full min-h-0">
                <DemoPaperViewer />
              </div>

              {/* Right Column: Socratic AI Chat Workspace */}
              <div className="h-[540px] lg:h-full min-h-0">
                <DemoChatPanel />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
