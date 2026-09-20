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
  const [winSize, setWinSize] = useState<{ w: number; h: number }>(() =>
    typeof window !== "undefined"
      ? { w: window.innerWidth, h: window.innerHeight }
      : { w: 1440, h: 900 }
  );

  useEffect(() => {
    if (!isHero) return;

    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    const handleResize = () => {
      setWinSize({ w: window.innerWidth, h: window.innerHeight });
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    window.addEventListener("resize", handleResize, { passive: true });
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("resize", handleResize);
    };
  }, [isHero]);

  const hasMouse = mousePos.x > 0 && mousePos.y > 0;
  const parallaxX = hasMouse ? ((mousePos.x - winSize.w / 2) / winSize.w) * 16 : 0;
  const parallaxY = hasMouse ? ((mousePos.y - winSize.h / 2) / winSize.h) * 16 : 0;

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

        /* Astrolabe Rotations */
        @keyframes astrolabeRotateCW {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes astrolabeRotateCCW {
          from { transform: rotate(0deg); }
          to { transform: rotate(-360deg); }
        }

        /* Citation Pulse along edges */
        @keyframes citationFlow {
          0% { stroke-dashoffset: 140; }
          100% { stroke-dashoffset: 0; }
        }

        /* Node Breathing / Twinkle */
        @keyframes nodePulse {
          0%, 100% {
            transform: scale(1);
            opacity: 0.55;
          }
          50% {
            transform: scale(1.4);
            opacity: 1;
          }
        }

        /* Radar Grounding Sweep */
        @keyframes radarSweep {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        /* Micro-float for badges */
        @keyframes floatDrift {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-5px); }
        }

        /* Harmonic wave breathing */
        @keyframes harmonicWave {
          0% { transform: translateY(0) scaleY(0.95); }
          100% { transform: translateY(-6px) scaleY(1.05); }
        }

        @media (prefers-reduced-motion: reduce) {
          .animate-celestial-beam,
          .animate-aurora-one,
          .animate-aurora-two,
          .animate-celestial-mote,
          .animate-astrolabe-cw,
          .animate-astrolabe-ccw,
          .animate-citation-flow,
          .animate-node-pulse,
          .animate-radar-sweep,
          .animate-float-drift,
          .animate-harmonic-wave {
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

      {/* 5.5 Celestial Scholar Motifs: Knowledge Constellation & Astrolabe Matrix */}
      <div
        data-testid="dashboard-scholar-motifs"
        className={`absolute inset-0 transition-opacity duration-1000 pointer-events-none hidden lg:block z-0 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      >
        {/* Left Wing: Knowledge Constellation & Vector Nexus */}
        <div
          className="absolute left-10 xl:left-20 top-1/2 w-[320px] xl:w-[360px] h-[500px] transition-transform duration-300 ease-out"
          style={{
            transform: `translate3d(${parallaxX * 1.2}px, calc(-50% + ${parallaxY * 1.2}px), 0)`,
          }}
        >
          <svg
            viewBox="0 0 360 500"
            className="w-full h-full overflow-visible"
            aria-hidden="true"
          >
            <defs>
              <linearGradient id="citationEdgeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#cc785c" stopOpacity={isDark ? 0.7 : 0.6} />
                <stop offset="100%" stopColor={isDark ? "#93c5fd" : "#d97706"} stopOpacity={isDark ? 0.7 : 0.6} />
              </linearGradient>
            </defs>

            {/* Background static citation edges */}
            <g stroke={isDark ? "rgba(186, 230, 253, 0.15)" : "rgba(204, 120, 92, 0.2)"} strokeWidth="1" strokeDasharray="4 6" fill="none">
              <path d="M 60 70 L 180 110" />
              <path d="M 180 110 L 90 210" />
              <path d="M 180 110 L 250 195" />
              <path d="M 90 210 L 50 330" />
              <path d="M 90 210 L 210 320" />
              <path d="M 250 195 L 210 320" />
              <path d="M 50 330 L 120 440" />
              <path d="M 210 320 L 120 440" />
            </g>

            {/* Animated luminous impulse pulses flowing along citation paths */}
            <g stroke="url(#citationEdgeGrad)" strokeWidth="1.75" fill="none" strokeDasharray="20 100">
              <path d="M 60 70 L 180 110" style={{ animation: "citationFlow 5s linear infinite" }} />
              <path d="M 180 110 L 90 210" style={{ animation: "citationFlow 6s linear infinite 0.8s" }} />
              <path d="M 180 110 L 250 195" style={{ animation: "citationFlow 7s linear infinite 1.6s" }} />
              <path d="M 90 210 L 50 330" style={{ animation: "citationFlow 5.5s linear infinite 0.4s" }} />
              <path d="M 90 210 L 210 320" style={{ animation: "citationFlow 6.5s linear infinite 1.2s" }} />
              <path d="M 250 195 L 210 320" style={{ animation: "citationFlow 6s linear infinite 2.2s" }} />
              <path d="M 50 330 L 120 440" style={{ animation: "citationFlow 5.8s linear infinite 1.5s" }} />
              <path d="M 210 320 L 120 440" style={{ animation: "citationFlow 6.2s linear infinite 2.8s" }} />
            </g>

            {/* Graph Nodes with breathing pulse */}
            {/* Node 1: Origin Hypothesis */}
            <g transform="translate(60, 70)">
              <circle r="12" fill={isDark ? "rgba(147, 197, 253, 0.12)" : "rgba(204, 120, 92, 0.12)"} style={{ animation: "nodePulse 4s ease-in-out infinite" }} />
              <circle r="4" fill={isDark ? "#93c5fd" : "#cc785c"} />
              <text x="-8" y="-14" fill={isDark ? "#93c5fd" : "#cc785c"} className="font-mono text-[9px] tracking-wider" opacity="0.85">
                §1 HYPOTHESIS
              </text>
            </g>

            {/* Node 2: Vector Space Embedding */}
            <g transform="translate(180, 110)">
              <circle r="15" fill={isDark ? "rgba(251, 191, 36, 0.12)" : "rgba(217, 119, 87, 0.12)"} style={{ animation: "nodePulse 4.5s ease-in-out infinite 0.7s" }} />
              <circle r="4.5" fill={isDark ? "#fbbf24" : "#d97706"} />
              <text x="12" y="4" fill={isDark ? "#e0f2fe" : "#252523"} className="font-mono text-[9px] tracking-wider" opacity="0.8">
                vec: ℝ¹⁵³⁶
              </text>
            </g>

            {/* Node 3: Grounded Bounding Box Target (Framed Reticle) */}
            <g transform="translate(90, 210)">
              <circle r="16" fill="rgba(204, 120, 92, 0.16)" style={{ animation: "nodePulse 3.8s ease-in-out infinite 1.2s" }} />
              <circle r="5" fill="#cc785c" />
              {/* Corner reticle framing [x0, y0] */}
              <path d="M -14 -8 L -14 -14 L -8 -14 M 14 -8 L 14 -14 L 8 -14 M -14 8 L -14 14 L -8 14 M 14 8 L 14 14 L 8 14" stroke="#cc785c" strokeWidth="1.5" fill="none" opacity="0.8" />
              <g transform="translate(18, 4)">
                <rect x="0" y="-10" width="128" height="18" rx="4" fill={isDark ? "rgba(24, 23, 21, 0.8)" : "rgba(250, 249, 245, 0.9)"} stroke={isDark ? "rgba(204, 120, 92, 0.4)" : "rgba(204, 120, 92, 0.3)"} strokeWidth="1" />
                <text x="6" y="3" fill="#cc785c" className="font-mono text-[9px] font-medium tracking-tight">
                  ⚑ BBOX [0.12, 0.45]
                </text>
              </g>
            </g>

            {/* Node 4: Cross-Encoder Rerank */}
            <g transform="translate(250, 195)">
              <circle r="13" fill={isDark ? "rgba(129, 140, 248, 0.14)" : "rgba(204, 120, 92, 0.12)"} style={{ animation: "nodePulse 5s ease-in-out infinite 1.8s" }} />
              <circle r="4" fill={isDark ? "#818cf8" : "#cc785c"} />
              <text x="10" y="4" fill={isDark ? "#cbd5e1" : "#6c6a64"} className="font-mono text-[9px] tracking-wider" opacity="0.8">
                Rerank: σ(z)
              </text>
            </g>

            {/* Node 5: Formal Lemma & Axiom */}
            <g transform="translate(50, 330)">
              <circle r="12" fill={isDark ? "rgba(147, 197, 253, 0.12)" : "rgba(204, 120, 92, 0.12)"} style={{ animation: "nodePulse 4.2s ease-in-out infinite 2.1s" }} />
              <circle r="3.5" fill={isDark ? "#93c5fd" : "#cc785c"} />
              <text x="-6" y="18" fill={isDark ? "#93c5fd" : "#8e8b82"} className="font-mono text-[9px] tracking-wider" opacity="0.8">
                ∇·E = 0
              </text>
            </g>

            {/* Node 6: Citation Anchor */}
            <g transform="translate(210, 320)">
              <circle r="15" fill={isDark ? "rgba(251, 191, 36, 0.15)" : "rgba(245, 158, 11, 0.15)"} style={{ animation: "nodePulse 4.4s ease-in-out infinite 0.5s" }} />
              <circle r="4.5" fill={isDark ? "#fbbf24" : "#d97706"} />
              <g transform="translate(14, 4)">
                <rect x="0" y="-10" width="112" height="18" rx="4" fill={isDark ? "rgba(24, 23, 21, 0.8)" : "rgba(250, 249, 245, 0.9)"} stroke={isDark ? "rgba(251, 191, 36, 0.35)" : "rgba(217, 119, 87, 0.3)"} strokeWidth="1" />
                <text x="6" y="3" fill={isDark ? "#fbbf24" : "#b45309"} className="font-mono text-[9px] font-medium tracking-tight">
                  arXiv:2403.09841
                </text>
              </g>
            </g>

            {/* Node 7: Verified Synthesis */}
            <g transform="translate(120, 440)">
              <circle r="16" fill={isDark ? "rgba(52, 211, 153, 0.14)" : "rgba(16, 185, 129, 0.14)"} style={{ animation: "nodePulse 4.6s ease-in-out infinite 2.5s" }} />
              <circle r="5" fill={isDark ? "#34d399" : "#059669"} />
              <text x="14" y="4" fill={isDark ? "#34d399" : "#059669"} className="font-mono text-[9px] font-medium tracking-wider" opacity="0.9">
                ✓ GROUNDED 99.4%
              </text>
            </g>
          </svg>
        </div>

        {/* Right Wing: Celestial Astrolabe & Grounding Radar */}
        <div
          className="absolute right-6 xl:right-16 top-1/2 w-[340px] xl:w-[380px] h-[500px] transition-transform duration-300 ease-out"
          style={{
            transform: `translate3d(${-parallaxX * 1.2}px, calc(-50% + ${-parallaxY * 1.2}px), 0)`,
          }}
        >
          <svg
            viewBox="0 0 380 500"
            className="w-full h-full overflow-visible"
            aria-hidden="true"
          >
            <defs>
              <radialGradient id="radarSweepGradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#cc785c" stopOpacity="0.35" />
                <stop offset="60%" stopColor="#cc785c" stopOpacity="0.12" />
                <stop offset="100%" stopColor="#cc785c" stopOpacity="0" />
              </radialGradient>
              <linearGradient id="astrolabeRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#cc785c" stopOpacity={isDark ? 0.45 : 0.35} />
                <stop offset="50%" stopColor={isDark ? "#93c5fd" : "#d97706"} stopOpacity={isDark ? 0.4 : 0.3} />
                <stop offset="100%" stopColor="#cc785c" stopOpacity={isDark ? 0.2 : 0.15} />
              </linearGradient>
            </defs>

            {/* Static Coordinate Axes & Crosshairs centered at (200, 250) */}
            <g stroke={isDark ? "rgba(186, 230, 253, 0.12)" : "rgba(204, 120, 92, 0.16)"} strokeWidth="1">
              <line x1="200" y1="70" x2="200" y2="430" strokeDasharray="3 5" />
              <line x1="40" y1="250" x2="360" y2="250" strokeDasharray="3 5" />
              {/* Diagonal axes */}
              <line x1="80" y1="130" x2="320" y2="370" strokeDasharray="2 6" opacity="0.6" />
              <line x1="80" y1="370" x2="320" y2="130" strokeDasharray="2 6" opacity="0.6" />
            </g>

            {/* Central Grounding Radar Beam (Rotating 360deg) */}
            <g style={{ transformOrigin: "200px 250px", animation: "radarSweep 16s linear infinite" }}>
              <path
                d="M 200 250 L 350 250 A 150 150 0 0 0 306 144 Z"
                fill="url(#radarSweepGradient)"
              />
              <line x1="200" y1="250" x2="350" y2="250" stroke="#cc785c" strokeWidth="1.5" strokeOpacity="0.7" />
            </g>

            {/* 1. Outer Astrolabe Ring (Radius 150px, rotates CW) */}
            <g style={{ transformOrigin: "200px 250px", animation: "astrolabeRotateCW 80s linear infinite" }}>
              <circle
                cx="200"
                cy="250"
                r="150"
                fill="none"
                stroke="url(#astrolabeRingGrad)"
                strokeWidth="1.2"
                strokeDasharray="4 8"
              />
              {/* Outer tick marks at 12 positions */}
              {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => (
                <line
                  key={deg}
                  x1="200"
                  y1="94"
                  x2="200"
                  y2="103"
                  stroke={isDark ? "rgba(147, 197, 253, 0.4)" : "rgba(204, 120, 92, 0.4)"}
                  strokeWidth="1.2"
                  transform={`rotate(${deg} 200 250)`}
                />
              ))}
              {/* Cardinal Greek markers */}
              <text x="200" y="88" textAnchor="middle" fill="#cc785c" className="font-mono text-[10px]" opacity="0.8">
                α · 0°
              </text>
              <text x="364" y="254" textAnchor="start" fill="#cc785c" className="font-mono text-[10px]" opacity="0.8">
                β · 90°
              </text>
              <text x="200" y="420" textAnchor="middle" fill="#cc785c" className="font-mono text-[10px]" opacity="0.8">
                γ · 180°
              </text>
              <text x="36" y="254" textAnchor="end" fill="#cc785c" className="font-mono text-[10px]" opacity="0.8">
                δ · 270°
              </text>
            </g>

            {/* 2. Middle Orbital Ring (Radius 105px, rotates CCW) */}
            <g style={{ transformOrigin: "200px 250px", animation: "astrolabeRotateCCW 55s linear infinite" }}>
              <circle
                cx="200"
                cy="250"
                r="105"
                fill="none"
                stroke={isDark ? "rgba(147, 197, 253, 0.25)" : "rgba(204, 120, 92, 0.25)"}
                strokeWidth="1.5"
                strokeDasharray="14 7 2 7"
              />
              <circle cx="200" cy="145" r="3.5" fill={isDark ? "#93c5fd" : "#cc785c"} />
              <circle cx="291" cy="197" r="2.5" fill={isDark ? "#fbbf24" : "#d97706"} />
              <circle cx="110" cy="305" r="3" fill={isDark ? "#34d399" : "#059669"} />
            </g>

            {/* 3. Inner Precision Ring (Radius 58px, rotates CW) */}
            <g style={{ transformOrigin: "200px 250px", animation: "astrolabeRotateCW 35s linear infinite" }}>
              <circle
                cx="200"
                cy="250"
                r="58"
                fill="none"
                stroke={isDark ? "rgba(251, 191, 36, 0.35)" : "rgba(217, 119, 87, 0.35)"}
                strokeWidth="1"
                strokeDasharray="5 5"
              />
              <polygon points="200,198 203,201 200,204 197,201" fill={isDark ? "#fbbf24" : "#d97706"} />
              <polygon points="260,250 257,253 254,250 257,247" fill={isDark ? "#fbbf24" : "#d97706"} />
              <polygon points="200,302 203,299 200,296 197,299" fill={isDark ? "#fbbf24" : "#d97706"} />
              <polygon points="140,250 143,253 146,250 143,247" fill={isDark ? "#fbbf24" : "#d97706"} />
            </g>

            {/* Center Core Reticle with pulsing beacon */}
            <g transform="translate(200, 250)">
              <circle r="16" fill="rgba(204, 120, 92, 0.15)" style={{ animation: "nodePulse 3.5s ease-in-out infinite" }} />
              <circle r="4" fill="#cc785c" />
              <circle r="1" fill="#fff" />
            </g>

            {/* Floating Scientific Micro-Badges & Formulas in 4 Open Corners */}
            {/* Top-Right Corner: Cosine Similarity Badge */}
            <g transform="translate(225, 45)">
              <g style={{ animation: "floatDrift 7s ease-in-out infinite alternate" }}>
                <rect x="0" y="-10" width="134" height="20" rx="4" fill={isDark ? "rgba(24, 23, 21, 0.85)" : "rgba(250, 249, 245, 0.9)"} stroke={isDark ? "rgba(147, 197, 253, 0.35)" : "rgba(204, 120, 92, 0.3)"} strokeWidth="1" />
                <text x="8" y="4" fill={isDark ? "#93c5fd" : "#cc785c"} className="font-mono text-[9px] font-medium tracking-tight">
                  COSINE SIM: 0.942
                </text>
              </g>
            </g>

            {/* Top-Left Corner: Quantum/Wave Formula */}
            <g transform="translate(45, 55)">
              <g opacity="0.8" style={{ animation: "floatDrift 8s ease-in-out infinite alternate 0.8s" }}>
                <text x="0" y="0" fill={isDark ? "#93c5fd" : "#8e8b82"} className="font-mono text-[10px]">
                  ∇²Ψ = -ρ / ε₀
                </text>
              </g>
            </g>

            {/* Bottom-Right Corner: Coordinate Origin Badge */}
            <g transform="translate(205, 450)">
              <g style={{ animation: "floatDrift 8.5s ease-in-out infinite alternate 1.5s" }}>
                <rect x="0" y="-10" width="146" height="20" rx="4" fill={isDark ? "rgba(24, 23, 21, 0.85)" : "rgba(250, 249, 245, 0.9)"} stroke={isDark ? "rgba(204, 120, 92, 0.35)" : "rgba(204, 120, 92, 0.25)"} strokeWidth="1" />
                <text x="8" y="4" fill="#cc785c" className="font-mono text-[9px] font-medium tracking-tight">
                  TOP-LEFT [0.0, 1.0]
                </text>
              </g>
            </g>

            {/* Bottom-Left Corner: Wavelength & Grounding */}
            <g transform="translate(35, 455)">
              <g opacity="0.8" style={{ animation: "floatDrift 9s ease-in-out infinite alternate 2.2s" }}>
                <text x="0" y="0" fill={isDark ? "#34d399" : "#059669"} className="font-mono text-[9px]">
                  λ = 540nm · Verified
                </text>
              </g>
            </g>
          </svg>
        </div>

        {/* Bottom Horizon: Harmonic Latent Embedding Wave */}
        <div className="absolute bottom-0 left-0 right-0 h-28 pointer-events-none overflow-hidden opacity-35 dark:opacity-25">
          <svg
            viewBox="0 0 1440 110"
            preserveAspectRatio="none"
            className="w-full h-full"
            aria-hidden="true"
          >
            <path
              d="M 0 60 Q 360 20 720 60 T 1440 60 L 1440 110 L 0 110 Z"
              fill="none"
              stroke={isDark ? "rgba(147, 197, 253, 0.25)" : "rgba(204, 120, 92, 0.25)"}
              strokeWidth="1.5"
              style={{ animation: "harmonicWave 10s ease-in-out infinite alternate" }}
            />
            <path
              d="M 0 75 Q 360 45 720 75 T 1440 75 L 1440 110 L 0 110 Z"
              fill="none"
              stroke={isDark ? "rgba(204, 120, 92, 0.2)" : "rgba(217, 119, 87, 0.2)"}
              strokeWidth="1"
              strokeDasharray="4 6"
              style={{ animation: "harmonicWave 13s ease-in-out infinite alternate 1.5s" }}
            />
          </svg>
        </div>
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
