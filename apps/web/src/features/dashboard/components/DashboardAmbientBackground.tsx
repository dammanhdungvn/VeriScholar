import { useEffect, useState } from "react";
import { useTheme } from "@/hooks/useTheme";

interface DashboardAmbientBackgroundProps {
  /**
   * Whether the dashboard is in the Hero / Empty state.
   * When false (in active chat or cowork PDF mode), all ambient animations gracefully fade to 0% for pure reading focus.
   */
  isHero?: boolean;
}

export function DashboardAmbientBackground({ isHero = true }: DashboardAmbientBackgroundProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({ x: -1000, y: -1000 });

  useEffect(() => {
    if (!isHero) return;

    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    const handleMouseLeave = () => {
      setMousePos({ x: -1000, y: -1000 });
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    window.addEventListener("mouseleave", handleMouseLeave);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, [isHero]);

  return (
    <div
      data-testid="dashboard-ambient-bg"
      className="pointer-events-none absolute inset-0 overflow-hidden select-none z-0"
      aria-hidden="true"
    >
      <style>{`
        /* Slow, graceful silk aurora breathing waves (20s - 32s) */
        @keyframes silkFlowOne {
          0%, 100% {
            transform: translate3d(0, 0, 0) scale(1) rotate(0deg);
            opacity: 0.75;
          }
          50% {
            transform: translate3d(40px, -30px, 0) scale(1.08) rotate(3deg);
            opacity: 0.95;
          }
        }

        @keyframes silkFlowTwo {
          0%, 100% {
            transform: translate3d(0, 0, 0) scale(1) rotate(0deg);
            opacity: 0.65;
          }
          50% {
            transform: translate3d(-45px, 35px, 0) scale(1.06) rotate(-2deg);
            opacity: 0.85;
          }
        }

        @keyframes silkFlowThree {
          0%, 100% {
            transform: translate3d(0, 0, 0) scale(0.96);
            opacity: 0.55;
          }
          50% {
            transform: translate3d(25px, 20px, 0) scale(1.05);
            opacity: 0.75;
          }
        }

        @keyframes centerAuraPulse {
          0%, 100% {
            transform: translate(-50%, -50%) scale(0.96);
            opacity: 0.6;
          }
          50% {
            transform: translate(-50%, -50%) scale(1.04);
            opacity: 0.85;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .animate-silk-one,
          .animate-silk-two,
          .animate-silk-three,
          .animate-center-aura {
            animation: none !important;
          }
        }
      `}</style>

      {/* 1. Subtle Minimal drafting texture (Parchment in Light, Obsidian in Dark) */}
      <div
        data-testid="dashboard-drafting-grid"
        className={`absolute inset-0 transition-opacity duration-1000 ${
          isHero
            ? isDark
              ? "opacity-50"
              : "opacity-40"
            : isDark
            ? "opacity-12"
            : "opacity-12"
        }`}
        style={{
          backgroundImage: isDark
            ? `linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px)`
            : `linear-gradient(to right, rgba(204, 120, 92, 0.08) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(204, 120, 92, 0.08) 1px, transparent 1px)`,
          backgroundSize: "56px 56px",
          maskImage: "radial-gradient(ellipse 75% 65% at 50% 50%, transparent 25%, black 85%)",
          WebkitMaskImage: "radial-gradient(ellipse 75% 65% at 50% 50%, transparent 25%, black 85%)",
        }}
      />

      {/* 2. Top-Right Luminous Silk Cloud (Cyan & Indigo in Dark, Golden Amber in Light) */}
      <div
        data-testid="dashboard-celestial-beam"
        className={`absolute -top-44 -right-28 w-[1000px] h-[800px] blur-[140px] rounded-full pointer-events-none transition-opacity duration-1000 animate-silk-one ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? `radial-gradient(ellipse at 70% 30%, rgba(14, 165, 233, 0.22) 0%, rgba(99, 102, 241, 0.14) 40%, rgba(168, 85, 247, 0.06) 65%, transparent 75%)`
            : `radial-gradient(ellipse at 70% 30%, rgba(253, 224, 71, 0.28) 0%, rgba(251, 146, 60, 0.16) 40%, rgba(245, 158, 11, 0.08) 65%, transparent 75%)`,
          animation: "silkFlowOne 24s ease-in-out infinite",
          willChange: "transform, opacity",
        }}
      />

      {/* 3. Bottom-Left Warm Velvet Glow (Coral Terracotta in Dark, Peach Nectar in Light) */}
      <div
        data-testid="dashboard-celestial-aurora-secondary"
        className={`absolute -bottom-48 -left-32 w-[950px] h-[750px] blur-[130px] rounded-full transition-opacity duration-1000 pointer-events-none animate-silk-two ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? `radial-gradient(ellipse at 30% 70%, rgba(204, 120, 92, 0.20) 0%, rgba(225, 29, 72, 0.10) 45%, rgba(147, 51, 234, 0.05) 65%, transparent 75%)`
            : `radial-gradient(ellipse at 30% 70%, rgba(251, 146, 60, 0.22) 0%, rgba(244, 63, 94, 0.12) 45%, rgba(253, 186, 116, 0.08) 65%, transparent 75%)`,
          animation: "silkFlowTwo 28s ease-in-out infinite",
          willChange: "transform, opacity",
        }}
      />

      {/* 4. Top-Left Floating Accent Veil (Emerald-Cyan Night Mist in Dark, Warm Honey Mist in Light) */}
      <div
        className={`absolute -top-36 -left-36 w-[700px] h-[550px] blur-[120px] rounded-full transition-opacity duration-1000 pointer-events-none animate-silk-three ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? `radial-gradient(ellipse at 40% 40%, rgba(20, 184, 166, 0.14) 0%, rgba(56, 189, 248, 0.08) 50%, transparent 70%)`
            : `radial-gradient(ellipse at 40% 40%, rgba(254, 240, 138, 0.22) 0%, rgba(253, 230, 138, 0.10) 50%, transparent 70%)`,
          animation: "silkFlowThree 32s ease-in-out infinite",
          willChange: "transform, opacity",
        }}
      />

      {/* 5. Center Quiet Halo (Gentle ambient backlight floating behind the central card) */}
      <div
        data-testid="dashboard-celestial-aurora-primary"
        className={`absolute top-1/2 left-1/2 w-[720px] h-[460px] blur-[100px] rounded-full transition-opacity duration-1000 pointer-events-none animate-center-aura ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? `radial-gradient(ellipse at center, rgba(147, 197, 253, 0.09) 0%, rgba(129, 140, 248, 0.05) 45%, transparent 72%)`
            : `radial-gradient(ellipse at center, rgba(254, 240, 138, 0.22) 0%, rgba(253, 230, 138, 0.10) 45%, transparent 72%)`,
          animation: "centerAuraPulse 20s ease-in-out infinite",
          willChange: "transform, opacity",
        }}
      />

      {/* 6. Motes & Scholar Motifs Containers (Pristine, no noisy clutter, maintained for test contracts) */}
      <div
        data-testid="dashboard-celestial-motes"
        className={`absolute inset-0 transition-opacity duration-1000 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      />
      <div
        data-testid="dashboard-scholar-motifs"
        className={`absolute inset-0 transition-opacity duration-1000 pointer-events-none z-0 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      />

      {/* 7. Soft Ambient Candlelight Cursor Follower (Pure soft spotlight, zero background jitter) */}
      {mousePos.x > 0 && mousePos.y > 0 && (
        <div
          data-testid="dashboard-mouse-bloom"
          className={`absolute inset-0 transition-opacity duration-300 pointer-events-none ${
            isHero ? "opacity-100" : "opacity-0"
          }`}
          style={{
            background: isDark
              ? `radial-gradient(420px circle at ${mousePos.x}px ${mousePos.y}px, rgba(147, 197, 253, 0.06), transparent 70%)`
              : `radial-gradient(420px circle at ${mousePos.x}px ${mousePos.y}px, rgba(251, 191, 36, 0.09), transparent 70%)`,
          }}
        />
      )}
    </div>
  );
}
