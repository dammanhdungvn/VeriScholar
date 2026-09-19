import { useEffect, useState } from "react";
import { useTheme } from "@/hooks/useTheme";

interface DashboardAmbientBackgroundProps {
  /**
   * Whether the dashboard is in the Hero / Empty state (where "Ánh Nắng & Ánh Trăng" celestial aura is active).
   * When false (in active chat or cowork PDF mode), all ambient animations gracefully fade to 0% for pure reading focus.
   */
  isHero?: boolean;
}

const CELESTIAL_MOTES = [
  { top: "28%", left: "42%", size: 4, delay: "0s", duration: "11s" },
  { top: "34%", left: "62%", size: 3, delay: "2.5s", duration: "13s" },
  { top: "48%", left: "36%", size: 5, delay: "4.8s", duration: "14s" },
  { top: "22%", left: "74%", size: 3.5, delay: "1.2s", duration: "10s" },
  { top: "62%", left: "58%", size: 4, delay: "6.1s", duration: "12s" },
  { top: "42%", left: "78%", size: 3, delay: "3.7s", duration: "15s" },
];

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
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [isHero]);

  return (
    <div
      data-testid="dashboard-ambient-bg"
      className="pointer-events-none absolute inset-0 overflow-hidden select-none z-0"
      aria-hidden="true"
    >
      <style>{`
        /* Slow, graceful floating of sun/moon dust motes in the celestial ray */
        @keyframes floatMote {
          0%, 100% {
            transform: translate(0, 0) scale(0.85);
            opacity: 0.25;
          }
          50% {
            transform: translate(6px, -18px) scale(1.2);
            opacity: 0.85;
          }
        }

        /* Organic drift for the celestial beam */
        @keyframes celestialBeamDrift {
          0%, 100% {
            transform: rotate(-18deg) translate(0, 0) scale(1);
            opacity: 0.82;
          }
          50% {
            transform: rotate(-16deg) translate(15px, -10px) scale(1.05);
            opacity: 1;
          }
        }

        /* Primary Aurora Ribbon Drift */
        @keyframes auroraDriftOne {
          0%, 100% {
            transform: translate(-50%, -50%) scale(0.96);
            opacity: 0.75;
          }
          50% {
            transform: translate(-48%, -52%) scale(1.08);
            opacity: 1;
          }
        }

        /* Secondary Aurora Ribbon Drift */
        @keyframes auroraDriftTwo {
          0%, 100% {
            transform: translate(0, 0) scale(1);
            opacity: 0.7;
          }
          50% {
            transform: translate(-20px, 15px) scale(1.06);
            opacity: 0.95;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .animate-celestial-beam,
          .animate-aurora-one,
          .animate-aurora-two,
          .animate-celestial-mote {
            animation: none !important;
          }
        }
      `}</style>

      {/* 1. Underlying Academic Drafting Grid (Parchment in Light, Obsidian in Dark) */}
      <div
        data-testid="dashboard-drafting-grid"
        className={`absolute inset-0 transition-opacity duration-700 ${
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
            ? `linear-gradient(to right, rgba(186, 230, 253, 0.10) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(186, 230, 253, 0.10) 1px, transparent 1px)`
            : `linear-gradient(to right, rgba(217, 119, 87, 0.16) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(217, 119, 87, 0.16) 1px, transparent 1px)`,
          backgroundSize: "40px 40px",
          maskImage: "radial-gradient(ellipse 85% 75% at 50% 45%, black 30%, transparent 100%)",
          WebkitMaskImage: "radial-gradient(ellipse 85% 75% at 50% 45%, black 30%, transparent 100%)",
        }}
      />

      {/* 2. Celestial Light Ray (Angled Sunbeam for Light mode, Silver Moonbeam for Dark mode) */}
      <div
        data-testid="dashboard-celestial-beam"
        className={`absolute -top-32 -right-20 w-[950px] h-[750px] blur-3xl pointer-events-none transition-opacity duration-700 animate-celestial-beam ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? /* Moonbeam: Silver lunar blue light streaming from nocturnal sky */
              `radial-gradient(ellipse at 80% 20%, rgba(186, 230, 253, 0.24) 0%, rgba(147, 197, 253, 0.14) 35%, rgba(99, 102, 241, 0.06) 65%, transparent 80%)`
            : /* Sunbeam: Golden morning sun ray streaming through library arch window */
              `radial-gradient(ellipse at 80% 20%, rgba(253, 230, 138, 0.32) 0%, rgba(251, 191, 36, 0.18) 35%, rgba(245, 158, 11, 0.08) 65%, transparent 80%)`,
          animation: "celestialBeamDrift 18s ease-in-out infinite",
          transformOrigin: "top right",
        }}
      />

      {/* 3. Primary Central Aurora Veil (Warm Sunlight Glow vs Serene Moonlight Pool) */}
      <div
        data-testid="dashboard-celestial-aurora-primary"
        className={`absolute top-1/2 left-1/2 w-[760px] h-[460px] blur-3xl rounded-full transition-opacity duration-700 pointer-events-none animate-aurora-one ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? /* Dark Mode: Moonlight reservoir around workspace center */
              `radial-gradient(ellipse at center, rgba(147, 197, 253, 0.18) 0%, rgba(129, 140, 248, 0.09) 45%, transparent 72%)`
            : /* Light Mode: Warm sunlight reservoir around workspace center */
              `radial-gradient(ellipse at center, rgba(252, 211, 77, 0.22) 0%, rgba(245, 158, 11, 0.11) 45%, transparent 72%)`,
          animation: "auroraDriftOne 14s ease-in-out infinite",
          transformOrigin: "center center",
        }}
      />

      {/* 4. Secondary Celestial Aurora Ribbon (Diffused corner glow) */}
      <div
        data-testid="dashboard-celestial-aurora-secondary"
        className={`absolute top-1/4 left-1/3 w-[580px] h-[360px] blur-3xl rounded-full transition-opacity duration-700 pointer-events-none animate-aurora-two ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? /* Dark Mode: Cool indigo/cyan twilight shimmer */
              `radial-gradient(ellipse at center, rgba(56, 189, 248, 0.12) 0%, rgba(99, 102, 241, 0.06) 50%, transparent 68%)`
            : /* Light Mode: Soft amber/terracotta sun-kissed shimmer */
              `radial-gradient(ellipse at center, rgba(251, 146, 60, 0.14) 0%, rgba(217, 119, 87, 0.08) 50%, transparent 68%)`,
          animation: "auroraDriftTwo 19s ease-in-out infinite",
        }}
      />

      {/* 5. Floating Celestial Dust Motes (Sunlight motes in Light, Moonlight dust in Dark) */}
      <div
        data-testid="dashboard-celestial-motes"
        className={`absolute inset-0 transition-opacity duration-700 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      >
        {CELESTIAL_MOTES.map((mote, i) => (
          <div
            key={i}
            className="absolute rounded-full pointer-events-none animate-celestial-mote"
            style={{
              top: mote.top,
              left: mote.left,
              width: `${mote.size}px`,
              height: `${mote.size}px`,
              background: isDark
                ? "rgba(224, 242, 254, 0.85)"
                : "rgba(245, 158, 11, 0.75)",
              boxShadow: isDark
                ? "0 0 10px 2px rgba(186, 230, 253, 0.6)"
                : "0 0 10px 2px rgba(252, 211, 77, 0.6)",
              animation: `floatMote ${mote.duration} ease-in-out infinite`,
              animationDelay: mote.delay,
            }}
          />
        ))}
      </div>

      {/* 6. Interactive Cursor Celestial Glow (Warm Amber in Light, Cool Silver-Blue in Dark) */}
      {mousePos.x > 0 && mousePos.y > 0 && (
        <div
          data-testid="dashboard-mouse-bloom"
          className={`absolute inset-0 transition-opacity duration-300 pointer-events-none ${
            isHero ? "opacity-100" : "opacity-0"
          }`}
          style={{
            background: isDark
              ? `radial-gradient(400px circle at ${mousePos.x}px ${mousePos.y}px, rgba(147, 197, 253, 0.10), transparent 60%)`
              : `radial-gradient(400px circle at ${mousePos.x}px ${mousePos.y}px, rgba(251, 191, 36, 0.10), transparent 60%)`,
          }}
        />
      )}
    </div>
  );
}
