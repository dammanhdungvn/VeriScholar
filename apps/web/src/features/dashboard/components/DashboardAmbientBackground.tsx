import { useEffect, useRef, useState } from "react";
import { useTheme } from "@/hooks/useTheme";

interface DashboardAmbientBackgroundProps {
  /**
   * Whether the dashboard is in the Hero / Standby state.
   * When false (in active chat or cowork PDF mode), all ambient animations gracefully fade to 0% for pure reading focus.
   */
  isHero?: boolean;
}

export function DashboardAmbientBackground({ isHero = true }: DashboardAmbientBackgroundProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const isDarkRef = useRef(isDark);

  useEffect(() => {
    isDarkRef.current = isDark;
  }, [isDark]);

  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({ x: -1000, y: -1000 });
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const mousePosRef = useRef({ x: -1000, y: -1000 });

  useEffect(() => {
    if (!isHero) return;

    const handleWindowMouseMove = (e: MouseEvent) => {
      const pos = { x: e.clientX, y: e.clientY };
      setMousePos(pos);
      mousePosRef.current = pos;
    };

    const handleWindowMouseLeave = () => {
      const pos = { x: -1000, y: -1000 };
      setMousePos(pos);
      mousePosRef.current = pos;
    };

    window.addEventListener("mousemove", handleWindowMouseMove);
    window.addEventListener("mouseleave", handleWindowMouseLeave);
    return () => {
      window.removeEventListener("mousemove", handleWindowMouseMove);
      window.removeEventListener("mouseleave", handleWindowMouseLeave);
    };
  }, [isHero]);

  // Landing Page Particle & Meteor Animation Engine adapted for Dashboard
  useEffect(() => {
    if (!isHero) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", handleResize);

    // Effect 1: Neural Nodes (65 in Dark Mode for Cosmic Constellation, 52 in Light Mode for Silk Attention Mesh)
    const totalParticleCount = 65;
    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      radius: number;
      opacity: number;
    }> = [];

    for (let i = 0; i < totalParticleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.55,
        vy: (Math.random() - 0.5) * 0.55,
        radius: Math.random() * 1.6 + 0.8,
        opacity: Math.random() * 0.4 + 0.3,
      });
    }

    // Effect 2: 6s Periodic Meteors (Shooting Stars Wave)
    const meteors: Array<{
      x: number;
      y: number;
      length: number;
      speed: number;
      opacity: number;
      angle: number;
      width: number;
    }> = [];

    const spawnMeteorShowerWave = () => {
      // Spawn meteors with vibrant color trail in dark mode, and warm terracotta in light mode
      const count = Math.floor(Math.random() * 2) + 2;
      for (let mIdx = 0; mIdx < count; mIdx++) {
        const angle = Math.random() * 0.85 + 0.35;
        const startX = Math.random() * (width * 1.2) - width * 0.1;
        const startY = Math.random() * (height * 0.35) - 80;

        meteors.push({
          x: startX,
          y: startY,
          length: Math.random() * 180 + 80,
          speed: Math.random() * 4.0 + 3.0,
          opacity: 0.9,
          angle: angle,
          width: Math.random() * 2.0 + 1.2,
        });
      }
    };

    const meteorInterval = setInterval(spawnMeteorShowerWave, 6000);
    const initialTimeout = setTimeout(spawnMeteorShowerWave, 1000);

    // Effect 3: Light Mode Synaptic Pulse Packets
    const synapticPulses: Array<{
      fromIdx: number;
      toIdx: number;
      progress: number;
      speed: number;
    }> = [];

    const spawnSynapticPulse = () => {
      if (isDarkRef.current) return;
      if (synapticPulses.length >= 8) return;
      const lightNodeCount = 52;
      for (let attempt = 0; attempt < 10; attempt++) {
        const i = Math.floor(Math.random() * lightNodeCount);
        for (let j = 0; j < lightNodeCount; j++) {
          if (i === j) continue;
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist > 30 && dist < 140) {
            synapticPulses.push({
              fromIdx: i,
              toIdx: j,
              progress: 0,
              speed: Math.random() * 0.014 + 0.009,
            });
            return;
          }
        }
      }
    };

    const pulseInterval = setInterval(spawnSynapticPulse, 900);

    const render = () => {
      ctx.clearRect(0, 0, width, height);
      const m = mousePosRef.current;
      const currentIsDark = isDarkRef.current;

      // 1. Meteors Rendering (Glowing Shooting Stars)
      for (let i = meteors.length - 1; i >= 0; i--) {
        const star = meteors[i];
        const tailX = star.x - Math.cos(star.angle) * star.length;
        const tailY = star.y - Math.sin(star.angle) * star.length;

        const grad = ctx.createLinearGradient(star.x, star.y, tailX, tailY);
        if (currentIsDark) {
          grad.addColorStop(0, `rgba(255, 255, 255, ${star.opacity})`);
          grad.addColorStop(0.2, `rgba(255, 220, 190, ${star.opacity * 0.85})`);
          grad.addColorStop(0.65, `rgba(217, 119, 87, ${star.opacity * 0.35})`);
          grad.addColorStop(1, "rgba(217, 119, 87, 0)");
        } else {
          grad.addColorStop(0, `rgba(217, 119, 87, ${star.opacity})`);
          grad.addColorStop(0.25, `rgba(245, 158, 11, ${star.opacity * 0.8})`);
          grad.addColorStop(0.7, `rgba(204, 120, 92, ${star.opacity * 0.3})`);
          grad.addColorStop(1, "rgba(204, 120, 92, 0)");
        }

        ctx.beginPath();
        ctx.moveTo(star.x, star.y);
        ctx.lineTo(tailX, tailY);
        ctx.lineWidth = star.width;
        ctx.strokeStyle = grad;
        ctx.lineCap = "round";

        ctx.shadowBlur = 16;
        ctx.shadowColor = currentIsDark ? "#e89b82" : "rgba(204, 120, 92, 0.6)";
        ctx.stroke();
        ctx.shadowBlur = 0;

        star.x += Math.cos(star.angle) * star.speed;
        star.y += Math.sin(star.angle) * star.speed;
        star.opacity -= 0.0035;

        if (star.opacity <= 0 || star.y > height + 250 || star.x > width + 250) {
          meteors.splice(i, 1);
        }
      }

      // 2. Neural Nodes & Synaptic Constellation Lines
      const activeCount = currentIsDark ? totalParticleCount : 52;
      const speedScale = currentIsDark ? 1.0 : 0.7;

      for (let i = 0; i < activeCount; i++) {
        const p1 = particles[i];
        p1.x += p1.vx * speedScale;
        p1.y += p1.vy * speedScale;

        if (p1.x < 0 || p1.x > width) p1.vx *= -1;
        if (p1.y < 0 || p1.y > height) p1.vy *= -1;

        if (currentIsDark) {
          ctx.beginPath();
          ctx.arc(p1.x, p1.y, p1.radius, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(232, 155, 130, ${p1.opacity})`;
          ctx.shadowBlur = 8;
          ctx.shadowColor = "#d97757";
          ctx.fill();
          ctx.shadowBlur = 0;
        } else {
          ctx.beginPath();
          ctx.arc(p1.x, p1.y, p1.radius * 1.1, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(184, 75, 42, ${Math.min(0.85, p1.opacity * 1.3)})`;
          ctx.fill();
        }

        // Synaptic connection lines between nodes
        const maxDist = currentIsDark ? 120 : 135;
        for (let j = i + 1; j < activeCount; j++) {
          const p2 = particles[j];
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < maxDist) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            if (currentIsDark) {
              const lineAlpha = (1 - dist / maxDist) * 0.25;
              ctx.strokeStyle = `rgba(217, 119, 87, ${lineAlpha})`;
              ctx.lineWidth = 0.8;
            } else {
              const lineAlpha = Math.pow(1 - dist / maxDist, 1.1) * 0.38;
              ctx.strokeStyle = `rgba(184, 80, 48, ${lineAlpha})`;
              ctx.lineWidth = 0.95;
            }
            ctx.stroke();
          }
        }

        // Interactive Mouse Query Attention Beam
        if (m.x > 0 && m.y > 0) {
          const mDx = p1.x - m.x;
          const mDy = p1.y - m.y;
          const mDist = Math.sqrt(mDx * mDx + mDy * mDy);

          if (mDist < 175) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(m.x, m.y);
            if (currentIsDark) {
              const mAlpha = (1 - mDist / 175) * 0.45;
              ctx.strokeStyle = `rgba(240, 180, 160, ${mAlpha})`;
              ctx.lineWidth = 1.1;
            } else {
              const mAlpha = (1 - mDist / 175) * 0.55;
              ctx.strokeStyle = `rgba(195, 75, 35, ${mAlpha})`;
              ctx.lineWidth = 1.1;
            }
            ctx.stroke();
          }
        }
      }

      // 3. Light Mode Synaptic Pulse Packets along active lines
      if (!currentIsDark) {
        for (let k = synapticPulses.length - 1; k >= 0; k--) {
          const pulse = synapticPulses[k];
          pulse.progress += pulse.speed;
          if (pulse.progress >= 1) {
            synapticPulses.splice(k, 1);
            continue;
          }
          const pFrom = particles[pulse.fromIdx];
          const pTo = particles[pulse.toIdx];
          if (!pFrom || !pTo) {
            synapticPulses.splice(k, 1);
            continue;
          }
          const curX = pFrom.x + (pTo.x - pFrom.x) * pulse.progress;
          const curY = pFrom.y + (pTo.y - pFrom.y) * pulse.progress;
          const pulseAlpha = Math.sin(pulse.progress * Math.PI) * 0.85;

          ctx.beginPath();
          ctx.arc(curX, curY, 2.2, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(204, 80, 35, ${pulseAlpha})`;
          ctx.shadowBlur = 4;
          ctx.shadowColor = "rgba(217, 105, 55, 0.4)";
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", handleResize);
      clearInterval(meteorInterval);
      clearInterval(pulseInterval);
      clearTimeout(initialTimeout);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isHero]);

  return (
    <div
      data-testid="dashboard-ambient-bg"
      className="pointer-events-none absolute inset-0 overflow-hidden select-none z-0"
      aria-hidden="true"
    >
      {/* 1. Perspective Grid Background (Maintained with exact test classes opacity-50/opacity-40 and opacity-12) */}
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
            ? `linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px)`
            : `linear-gradient(to right, rgba(165, 120, 85, 0.16) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(165, 120, 85, 0.16) 1px, transparent 1px)`,
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse 80% 60% at 50% 25%, black 40%, transparent 100%)",
          WebkitMaskImage: "radial-gradient(ellipse 80% 60% at 50% 25%, black 40%, transparent 100%)",
        }}
      />

      {/* 2. Top-Center Ambient Glow Orb */}
      <div
        data-testid="dashboard-celestial-beam"
        className={`absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] blur-3xl rounded-full pointer-events-none transition-opacity duration-700 ${
          isHero ? "opacity-100" : "opacity-0"
        } ${
          isDark
            ? "bg-gradient-to-b from-[#d97757]/18 via-[#e89b82]/6 to-transparent"
            : "bg-gradient-to-b from-[#d97757]/14 via-[#e89b82]/5 to-transparent"
        }`}
      />

      {/* 3. Top-Left Diffused Ambient Glow */}
      <div
        data-testid="dashboard-celestial-aurora-primary"
        className={`absolute top-1/4 -left-40 w-80 h-80 blur-3xl rounded-full pointer-events-none transition-opacity duration-700 ${
          isHero ? "opacity-100" : "opacity-0"
        } ${isDark ? "bg-[#d97757]/10" : "bg-[#d97757]/6"}`}
      />

      {/* 4. Bottom-Right Diffused Amber Glow */}
      <div
        data-testid="dashboard-celestial-aurora-secondary"
        className={`absolute bottom-1/3 -right-40 w-80 h-80 blur-3xl rounded-full pointer-events-none transition-opacity duration-700 ${
          isHero ? "opacity-100" : "opacity-0"
        } ${isDark ? "bg-[#e8a55a]/10" : "bg-[#e8a55a]/6"}`}
      />

      {/* 5. Celestial Motes Container (kept for test contract) */}
      <div
        data-testid="dashboard-celestial-motes"
        className={`absolute inset-0 transition-opacity duration-700 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      />

      {/* 5.5 Interactive Particles & Meteor Canvas (Synced with Landing Page) */}
      <div
        data-testid="dashboard-scholar-motifs"
        className={`absolute inset-0 transition-opacity duration-700 pointer-events-none z-0 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      >
        <canvas ref={canvasRef} className="w-full h-full block" />
      </div>

      {/* 6. Interactive Mouse Spotlight Follower */}
      {mousePos.x > 0 && mousePos.y > 0 && (
        <div
          data-testid="dashboard-mouse-bloom"
          className={`absolute inset-0 transition-opacity duration-300 pointer-events-none ${
            isHero ? "opacity-100" : "opacity-0"
          }`}
          style={{
            background: isDark
              ? `radial-gradient(650px circle at ${mousePos.x}px ${mousePos.y}px, rgba(217, 119, 87, 0.12), transparent 60%)`
              : `radial-gradient(650px circle at ${mousePos.x}px ${mousePos.y}px, rgba(204, 110, 75, 0.10), transparent 60%)`,
          }}
        />
      )}
    </div>
  );
}
