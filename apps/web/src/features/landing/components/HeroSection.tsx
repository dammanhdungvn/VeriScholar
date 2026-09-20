import { useState, useRef, type MouseEvent } from "react";

export function HeroSection() {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [sheen, setSheen] = useState({ x: 50, y: 50, active: false });
  const plaqueRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!plaqueRef.current) return;
    const rect = plaqueRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const mouseX = e.clientX - centerX;
    const mouseY = e.clientY - centerY;

    // Subtle, prestigious tilt angles
    const rotateY = Math.max(-6, Math.min(6, (mouseX / (rect.width / 2)) * 6));
    const rotateX = Math.max(-5, Math.min(5, -(mouseY / (rect.height / 2)) * 5));

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
    <section className="relative pt-12 pb-8 sm:pt-20 sm:pb-12 overflow-hidden select-none">
      <div
        className="max-w-4xl mx-auto px-4 sm:px-6 text-center relative z-10"
        style={{ perspective: 1200 }}
      >
        {/* 3D Floating Scholarly Monolith Plaque */}
        <div
          ref={plaqueRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          style={{
            transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale(${sheen.active ? 1.015 : 1})`,
            transformStyle: "preserve-3d",
            transition: sheen.active
              ? "transform 0.12s ease-out, box-shadow 0.2s ease-out"
              : "transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.5s ease-out",
            boxShadow: sheen.active
              ? `${-tilt.y * 2.5}px ${tilt.x * 2.5 + 24}px 48px rgba(0,0,0,0.08), 0 0 35px rgba(204,120,92,0.12)`
              : undefined,
          }}
          className="relative inline-block px-7 py-7 sm:px-16 sm:py-12 rounded-3xl border border-[#cc785c]/30 dark:border-[#cc785c]/25 bg-white/65 dark:bg-[#1c1a17]/65 backdrop-blur-xl shadow-lg dark:shadow-[0_25px_60px_rgba(0,0,0,0.5)] cursor-default overflow-hidden"
        >
          {/* Dynamic Specular Sheen Layer (Glides with cursor) */}
          <div
            className="absolute inset-0 rounded-3xl pointer-events-none transition-opacity duration-300"
            style={{
              opacity: sheen.active ? 1 : 0,
              background: `radial-gradient(circle 380px at ${sheen.x}% ${sheen.y}%, rgba(204,120,92,0.14), transparent 75%)`,
            }}
          />

          {/* 4 Architectural Precision Coordinate Brackets with 3D Parallax Depth */}
          <span
            className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2 border-[#cc785c] pointer-events-none"
            style={{ transform: "translateZ(22px)" }}
          />
          <span
            className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2 border-[#cc785c] pointer-events-none"
            style={{ transform: "translateZ(22px)" }}
          />
          <span
            className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2 border-[#cc785c] pointer-events-none"
            style={{ transform: "translateZ(22px)" }}
          />
          <span
            className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2 border-[#cc785c] pointer-events-none"
            style={{ transform: "translateZ(22px)" }}
          />

          {/* Slogan Quote with 2-Tone Logo Color Harmony (Veri Ink & Scholar Coral) */}
          <blockquote
            className="space-y-4 sm:space-y-5 relative z-10"
            style={{ transform: "translateZ(14px)" }}
          >
            <h1 className="font-quote text-3xl sm:text-5xl md:text-6xl font-normal leading-[1.15] text-ink tracking-tight">
              <span className="block text-ink dark:text-zinc-100">“What I cannot create,</span>{" "}
              <span className="block mt-1 sm:mt-2 italic bg-gradient-to-r from-[#cc785c] via-[#d97757] to-[#e8a55a] bg-clip-text text-transparent">
                I do not understand.”
              </span>
            </h1>

            {/* Author Attribution with Academic Hairline Dividers */}
            <footer className="flex items-center justify-center gap-3 pt-2 text-xs sm:text-sm font-mono text-muted dark:text-zinc-400 uppercase tracking-[0.2em] font-medium">
              <span className="w-6 sm:w-10 h-[1px] bg-primary/40 dark:bg-zinc-700" />
              <span>Richard Feynman</span>
              <span className="w-6 sm:w-10 h-[1px] bg-primary/40 dark:bg-zinc-700" />
            </footer>
          </blockquote>
        </div>
      </div>
    </section>
  );
}
