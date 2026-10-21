import { useState, useRef, type MouseEvent } from "react";
import { DemoPaperViewer } from "./DemoPaperViewer";
import { DemoChatPanel } from "./DemoChatPanel";
import { useLandingStore } from "../stores/useLandingStore";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";

export function InteractiveDemo() {
  const activePaperId = useLandingStore((s) => s.activePaperId);
  const activePaper = MOCK_DEMO_PAPERS.find((p) => p.id === activePaperId) || MOCK_DEMO_PAPERS[0];

  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [glare, setGlare] = useState({ x: 50, y: 20, active: false });
  const studioRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!studioRef.current) return;
    const rect = studioRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const mouseX = e.clientX - centerX;
    const mouseY = e.clientY - centerY;

    // Subtle, grand hardware perspective tilt: max 2.5deg horizontally, 2.0deg vertically
    const rotateY = Math.max(-2.5, Math.min(2.5, (mouseX / (rect.width / 2)) * 2.5));
    const rotateX = Math.max(-2.0, Math.min(2.0, -(mouseY / (rect.height / 2)) * 2.0));

    const glareX = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
    const glareY = Math.max(0, Math.min(100, ((e.clientY - rect.top) / rect.height) * 100));

    setTilt({ x: rotateX, y: rotateY });
    setGlare({ x: glareX, y: glareY, active: true });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
    setGlare((g) => ({ ...g, active: false }));
  };

  return (
    <section
      id="interactive-demo"
      className="relative pb-16 sm:pb-24 overflow-hidden scroll-mt-20 select-none"
    >
      <div
        className="max-w-7xl xl:max-w-[1380px] mx-auto px-4 sm:px-6 relative z-10"
        style={{ perspective: 1800 }}
      >
        {/* Mac Studio Window Wrapper - 3D Hardware Frame with Subtle Perspective Tilt */}
        <div
          ref={studioRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          style={{
            transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
            transformStyle: "preserve-3d",
            transition: glare.active
              ? "transform 0.15s ease-out, box-shadow 0.25s ease-out"
              : "transform 0.6s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.6s ease-out",
            boxShadow: glare.active
              ? `${-tilt.y * 6}px ${tilt.x * 6 + 32}px 65px rgba(0,0,0,0.18), 0 0 50px rgba(217,119,87,0.08)`
              : undefined,
          }}
          className="relative rounded-2xl border border-[#d8d4cb] dark:border-[#3d372e] bg-[#edeae3] dark:bg-[#24211d] shadow-2xl dark:shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5),0_0_30px_rgba(217,119,87,0.06)] transition-colors duration-300 overflow-hidden"
        >
          {/* Subtle Ambient Glass Glare Overlay */}
          <div
            className="absolute inset-0 pointer-events-none rounded-2xl z-20 transition-opacity duration-300"
            style={{
              opacity: glare.active ? 1 : 0,
              background: `radial-gradient(circle 700px at ${glare.x}% ${glare.y}%, rgba(255,255,255,0.07), transparent 70%)`,
            }}
          />

          {/* Mac Studio Window Top Bar - Clean & Dignified */}
          <div className="flex items-center justify-between px-3 sm:px-4 py-2.5 bg-[#e4dfd6] dark:bg-[#2a2722] border-b border-[#d8d3c7] dark:border-[#383229] transition-colors duration-300 relative z-10">
            {/* macOS Window Control Dots */}
            <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
              <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-[#ff5f56] border border-[#e0443e]" />
              <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-[#ffbd2e] border border-[#dea123]" />
              <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-[#27c93f] border border-[#1aab29]" />
            </div>

            {/* Dynamic Document Name Pill */}
            <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1 rounded-full bg-[#f6f3ed] dark:bg-[#1f1d19] border border-[#dcd7cc] dark:border-[#383229] text-2xs sm:text-xs font-mono text-[#3d3a35] dark:text-zinc-300 transition-colors duration-300 truncate max-w-[200px] sm:max-w-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-[#d97757] shrink-0" />
              <span className="truncate">{activePaper.title}</span>
            </div>

            <div className="w-8 sm:w-12 shrink-0" />
          </div>

          {/* Dual-Pane Studio Body: Expansive 50/50 Split with Ample Space */}
          <div className="p-4 sm:p-5 bg-[#dfdad0] dark:bg-[#1c1a17] transition-colors duration-300 relative z-10 select-text overflow-hidden max-w-full">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-5 min-h-[560px] lg:h-[760px] max-w-full">
              {/* Left Column: PDF Paper Canvas Viewer */}
              <div className="h-[480px] sm:h-[540px] lg:h-full min-h-0 max-w-full overflow-hidden">
                <DemoPaperViewer />
              </div>

              {/* Right Column: Socratic AI Chat Workspace */}
              <div className="h-[520px] sm:h-[540px] lg:h-full min-h-0 max-w-full overflow-hidden">
                <DemoChatPanel />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
