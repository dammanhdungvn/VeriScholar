import { useEffect, useState } from "react";
import { useTheme } from "@/hooks/useTheme";

interface DashboardAmbientBackgroundProps {
  /**
   * Whether the dashboard is in the Hero / Empty state (where ambient breathing aura is active).
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

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, [isHero]);

  return (
    <div
      data-testid="dashboard-ambient-bg"
      className="pointer-events-none absolute inset-0 overflow-hidden select-none z-0"
      aria-hidden="true"
    >
      <style>{`
        /* Slow, peaceful breathing cycles for the celestial caustics (24s - 32s) */
        @keyframes causticBreatheOne {
          0%, 100% {
            transform: translate(0, 0) scale(1);
            opacity: 0.85;
          }
          50% {
            transform: translate(30px, -20px) scale(1.08);
            opacity: 1;
          }
        }

        @keyframes causticBreatheTwo {
          0%, 100% {
            transform: translate(0, 0) scale(1);
            opacity: 0.75;
          }
          50% {
            transform: translate(-35px, 25px) scale(1.06);
            opacity: 0.95;
          }
        }

        @keyframes causticBreatheCenter {
          0%, 100% {
            transform: translate(-50%, -50%) scale(0.96);
            opacity: 0.7;
          }
          50% {
            transform: translate(-50%, -50%) scale(1.05);
            opacity: 0.95;
          }
        }

        /* Subtle horizon latent wave */
        @keyframes horizonHarmonic {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-5px);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .animate-caustic-one,
          .animate-caustic-two,
          .animate-caustic-center,
          .animate-harmonic-wave {
            animation: none !important;
          }
        }
      `}</style>

      {/* 1. Underlying Academic Drafting Grid (Parchment in Light, Obsidian in Dark) */}
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
            ? `linear-gradient(to right, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(255, 255, 255, 0.04) 1px, transparent 1px)`
            : `linear-gradient(to right, rgba(204, 120, 92, 0.10) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(204, 120, 92, 0.10) 1px, transparent 1px)`,
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse 70% 60% at 50% 50%, transparent 25%, black 80%)",
          WebkitMaskImage: "radial-gradient(ellipse 70% 60% at 50% 50%, transparent 25%, black 80%)",
        }}
      />

      {/* 2. Top-Right Celestial Caustic Veil (Midnight Cyan/Indigo in Dark, Morning Amber in Light) */}
      <div
        data-testid="dashboard-celestial-beam"
        className={`absolute -top-40 -right-20 w-[900px] h-[750px] blur-[120px] rounded-full pointer-events-none transition-opacity duration-1000 animate-caustic-one ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? `radial-gradient(ellipse at 75% 25%, rgba(14, 165, 233, 0.16) 0%, rgba(99, 102, 241, 0.10) 45%, transparent 72%)`
            : `radial-gradient(ellipse at 75% 25%, rgba(251, 191, 36, 0.22) 0%, rgba(245, 158, 11, 0.11) 45%, transparent 72%)`,
          animation: "causticBreatheOne 24s ease-in-out infinite",
          willChange: "transform, opacity",
        }}
      />

      {/* 3. Bottom-Left Warm Ember Veil (Deep Terracotta in Dark, Golden Peach in Light) */}
      <div
        data-testid="dashboard-celestial-aurora-secondary"
        className={`absolute -bottom-36 -left-20 w-[850px] h-[650px] blur-[110px] rounded-full transition-opacity duration-1000 pointer-events-none animate-caustic-two ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? `radial-gradient(ellipse at 25% 75%, rgba(204, 120, 92, 0.14) 0%, rgba(154, 52, 18, 0.07) 50%, transparent 75%)`
            : `radial-gradient(ellipse at 25% 75%, rgba(251, 146, 60, 0.16) 0%, rgba(217, 119, 87, 0.08) 50%, transparent 75%)`,
          animation: "causticBreatheTwo 28s ease-in-out infinite",
          willChange: "transform, opacity",
        }}
      />

      {/* 4. Center Quiet Halo (Backlight supporting the upload card gently without visual noise) */}
      <div
        data-testid="dashboard-celestial-aurora-primary"
        className={`absolute top-1/2 left-1/2 w-[720px] h-[480px] blur-[95px] rounded-full transition-opacity duration-1000 pointer-events-none animate-caustic-center ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? `radial-gradient(ellipse at center, rgba(147, 197, 253, 0.09) 0%, rgba(129, 140, 248, 0.05) 45%, transparent 75%)`
            : `radial-gradient(ellipse at center, rgba(254, 240, 138, 0.20) 0%, rgba(253, 230, 138, 0.09) 45%, transparent 75%)`,
          animation: "causticBreatheCenter 20s ease-in-out infinite",
          willChange: "transform, opacity",
        }}
      />

      {/* 5. Minimal Motes Container (empty of noisy particles, keeping test contract pristine) */}
      <div
        data-testid="dashboard-celestial-motes"
        className={`absolute inset-0 transition-opacity duration-1000 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      />

      {/* 5.5 Minimal Horizon Harmony Line (Zero clutter, ultra-peaceful) */}
      <div
        data-testid="dashboard-scholar-motifs"
        className={`absolute inset-0 transition-opacity duration-1000 pointer-events-none z-0 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      >
        <div className="absolute bottom-0 left-0 right-0 h-20 pointer-events-none overflow-hidden opacity-25 dark:opacity-15">
          <svg
            viewBox="0 0 1440 80"
            preserveAspectRatio="none"
            className="w-full h-full"
            aria-hidden="true"
          >
            <path
              d="M 0 45 Q 360 25 720 45 T 1440 45 L 1440 80 L 0 80 Z"
              fill="none"
              stroke={isDark ? "rgba(147, 197, 253, 0.3)" : "rgba(204, 120, 92, 0.3)"}
              strokeWidth="1.2"
              style={{ animation: "horizonHarmonic 16s ease-in-out infinite alternate" }}
            />
          </svg>
        </div>
      </div>

      {/* 6. Soft Candlelight Cursor Glow (Only gentle warm pool around mouse, zero background shifting) */}
      {mousePos.x > 0 && mousePos.y > 0 && (
        <div
          data-testid="dashboard-mouse-bloom"
          className={`absolute inset-0 transition-opacity duration-300 pointer-events-none ${
            isHero ? "opacity-100" : "opacity-0"
          }`}
          style={{
            background: isDark
              ? `radial-gradient(450px circle at ${mousePos.x}px ${mousePos.y}px, rgba(147, 197, 253, 0.05), transparent 70%)`
              : `radial-gradient(450px circle at ${mousePos.x}px ${mousePos.y}px, rgba(251, 191, 36, 0.08), transparent 70%)`,
          }}
        />
      )}
    </div>
  );
}
