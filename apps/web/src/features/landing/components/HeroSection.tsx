import { useState, useRef, type MouseEvent } from "react";

export function HeroSection() {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [sheen, setSheen] = useState({ x: 50, y: 50, active: false });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const mouseX = e.clientX - centerX;
    const mouseY = e.clientY - centerY;

    // Majestic, subtle typographic tilt (free of boxy card constraints)
    const rotateY = Math.max(-5, Math.min(5, (mouseX / (rect.width / 2)) * 5));
    const rotateX = Math.max(-4, Math.min(4, -(mouseY / (rect.height / 2)) * 4));

    const sheenX = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
    const sheenY = Math.max(0, Math.min(100, ((e.clientY - rect.top) / rect.height) * 100));

    setTilt({ x: rotateX, y: rotateY });
    setSheen({ x: sheenX, y: sheenY, active: true });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
    setSheen((s) => ({ ...s, active: false }));
  };

  return (
    <section className="relative pt-10 pb-8 sm:pt-18 sm:pb-14 overflow-hidden select-none">
      <div
        className="max-w-5xl mx-auto px-4 sm:px-6 text-center relative z-10"
        style={{ perspective: 1200 }}
      >
        {/* 3D Typographical Scholarly Inscription (Dignified & Cardless) */}
        <div
          ref={containerRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          style={{
            transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
            transformStyle: "preserve-3d",
            transition: sheen.active
              ? "transform 0.12s ease-out"
              : "transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
          }}
          className="relative inline-flex flex-col items-center justify-center cursor-default max-w-4xl py-4 sm:py-6"
        >
          {/* Ambient Warm Scholarly Light Aura following cursor */}
          <div
            className="absolute -inset-10 sm:-inset-16 rounded-full pointer-events-none transition-opacity duration-500 blur-3xl -z-10"
            style={{
              opacity: sheen.active ? 1 : 0.45,
              background: `radial-gradient(circle 480px at ${sheen.x}% ${sheen.y}%, rgba(204,120,92,0.18), transparent 70%)`,
            }}
          />

          {/* Academic Epigraph Seal Badge */}
          <div
            className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full border border-[#cc785c]/30 dark:border-[#cc785c]/25 bg-[#cc785c]/6 dark:bg-[#cc785c]/10 text-[10.5px] sm:text-[11px] font-mono uppercase tracking-[0.24em] text-[#b85532] dark:text-[#e89b82] mb-5 sm:mb-7 shadow-2xs"
            style={{ transform: "translateZ(18px)" }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#cc785c] animate-pulse" />
            <span>Nguyên lý kiểm chứng nền tảng</span>
          </div>

          {/* Slogan Quote with Unconfined, Monumental Academic Typography */}
          <blockquote
            className="space-y-4 sm:space-y-6 relative"
            style={{ transform: "translateZ(24px)" }}
          >
            {/* Monumental Headline */}
            <h1 className="font-quote text-3xl sm:text-5xl md:text-6xl lg:text-[4.25rem] font-normal leading-[1.12] text-ink tracking-tight">
              <span className="block text-ink dark:text-[#f4f2eb] drop-shadow-2xs">
                “What I cannot create,
              </span>{" "}
              <span className="block mt-2 sm:mt-3.5 italic font-serif bg-gradient-to-r from-[#b85d3b] via-[#cc785c] to-[#e89b52] dark:from-[#f09f85] dark:via-[#e58a69] dark:to-[#f5c796] bg-clip-text text-transparent">
                I do not understand.”
              </span>
            </h1>

            {/* Author Attribution with Engraved Hairline Rules & Caltech Historical Inscription */}
            <footer className="flex flex-col items-center justify-center gap-2.5 pt-3 sm:pt-4">
              <div className="flex items-center justify-center gap-3.5 text-xs sm:text-sm font-mono text-[#4a453c] dark:text-[#c4bdb2] uppercase tracking-[0.25em] font-medium">
                <span className="w-8 sm:w-16 h-[1px] bg-gradient-to-r from-transparent to-[#cc785c]/60 dark:to-[#cc785c]/50" />
                <span className="font-semibold text-[#322e28] dark:text-[#eae6de]">Richard Feynman</span>
                <span className="w-8 sm:w-16 h-[1px] bg-gradient-to-l from-transparent to-[#cc785c]/60 dark:to-[#cc785c]/50" />
              </div>
              <span className="text-[10px] sm:text-[11px] font-mono text-muted/80 dark:text-zinc-400 uppercase tracking-[0.2em]">
                Caltech, 1988 • Di bút trên bảng đen
              </span>
            </footer>
          </blockquote>
        </div>
      </div>
    </section>
  );
}
