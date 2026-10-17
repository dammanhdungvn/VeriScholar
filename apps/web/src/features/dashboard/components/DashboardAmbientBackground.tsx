import { useEffect, useRef, useState } from "react";
import { useTheme } from "@/hooks/useTheme";

interface DashboardAmbientBackgroundProps {
  /**
   * Whether the dashboard is in the Hero / Standby state.
   * When false (in active chat or cowork PDF mode), all ambient animations gracefully fade to 0% for pure reading focus.
   */
  isHero?: boolean;
}

const MAX_METEORS = 8;
const MAX_SYNAPTIC_PULSES = 8;

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

    let rafId: number | null = null;
    const handleWindowMouseMove = (e: MouseEvent) => {
      mousePosRef.current = { x: e.clientX, y: e.clientY };
      if (rafId === null) {
        rafId = requestAnimationFrame(() => {
          setMousePos({ x: e.clientX, y: e.clientY });
          rafId = null;
        });
      }
    };

    const handleWindowMouseLeave = () => {
      mousePosRef.current = { x: -1000, y: -1000 };
      setMousePos({ x: -1000, y: -1000 });
    };

    window.addEventListener("mousemove", handleWindowMouseMove, { passive: true });
    window.addEventListener("mouseleave", handleWindowMouseLeave);
    return () => {
      if (rafId !== null) cancelAnimationFrame(rafId);
      window.removeEventListener("mousemove", handleWindowMouseMove);
      window.removeEventListener("mouseleave", handleWindowMouseLeave);
    };
  }, [isHero]);

  // Particle & Meteor Animation Engine adapted for Dashboard with Tab Visibility Controls
  useEffect(() => {
    if (!isHero) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number | null = null;
    let meteorInterval: ReturnType<typeof setInterval> | null = null;
    let pulseInterval: ReturnType<typeof setInterval> | null = null;
    let initialTimeout: ReturnType<typeof setTimeout> | null = null;
    let isRunning = true;
    let lastFrameTime = performance.now();

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", handleResize);

    // Effect 1: Neural Nodes (65 in Dark Mode, 52 in Light Mode)
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

    // Effect 2: 6s Periodic Meteors (Capped at MAX_METEORS to prevent runaway background accumulation)
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
      if (document.hidden) return;
      if (meteors.length >= MAX_METEORS) return;

      const count = Math.min(Math.floor(Math.random() * 2) + 2, MAX_METEORS - meteors.length);
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

    // Effect 3: Light Mode Synaptic Pulse Packets
    const synapticPulses: Array<{
      fromIdx: number;
      toIdx: number;
      progress: number;
      speed: number;
    }> = [];

    const spawnSynapticPulse = () => {
      if (document.hidden || isDarkRef.current) return;
      if (synapticPulses.length >= MAX_SYNAPTIC_PULSES) return;

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

    const startIntervals = () => {
      stopIntervals();
      meteorInterval = setInterval(spawnMeteorShowerWave, 6000);
      pulseInterval = setInterval(spawnSynapticPulse, 900);
      initialTimeout = setTimeout(spawnMeteorShowerWave, 1000);
    };

    const stopIntervals = () => {
      if (meteorInterval) {
        clearInterval(meteorInterval);
        meteorInterval = null;
      }
      if (pulseInterval) {
        clearInterval(pulseInterval);
        pulseInterval = null;
      }
      if (initialTimeout) {
        clearTimeout(initialTimeout);
        initialTimeout = null;
      }
    };

    const render = (currentTime: number) => {
      if (!isRunning) return;

      const elapsed = currentTime - lastFrameTime;
      lastFrameTime = currentTime;
      const deltaFactor = Math.min(Math.max(elapsed / 16.67, 0.1), 2.0);

      ctx.clearRect(0, 0, width, height);
      const m = mousePosRef.current;
      const currentIsDark = isDarkRef.current;

      // 1. Meteors Rendering
      for (let i = meteors.length - 1; i >= 0; i--) {
        const star = meteors[i];
        const tailX = star.x - Math.cos(star.angle) * star.length;
        const tailY = star.y - Math.sin(star.angle) * star.length;

        const grad = ctx.createLinearGradient(star.x, star.y, tailX, tailY);
        grad.addColorStop(0, `rgba(255, 255, 255, ${star.opacity})`);
        if (currentIsDark) {
          grad.addColorStop(0.2, `rgba(255, 220, 190, ${star.opacity * 0.85})`);
          grad.addColorStop(0.65, `rgba(217, 119, 87, ${star.opacity * 0.35})`);
        } else {
          grad.addColorStop(0.25, `rgba(255, 200, 160, ${star.opacity * 0.8})`);
          grad.addColorStop(0.7, `rgba(184, 75, 42, ${star.opacity * 0.3})`);
        }
        grad.addColorStop(1, "rgba(217, 119, 87, 0)");

        ctx.beginPath();
        ctx.moveTo(star.x, star.y);
        ctx.lineTo(tailX, tailY);
        ctx.lineWidth = star.width;
        ctx.strokeStyle = grad;
        ctx.lineCap = "round";

        ctx.shadowBlur = 16;
        ctx.shadowColor = currentIsDark ? "#e89b82" : "#b84b2a";
        ctx.stroke();
        ctx.shadowBlur = 0;

        star.x += Math.cos(star.angle) * star.speed * deltaFactor;
        star.y += Math.sin(star.angle) * star.speed * deltaFactor;
        star.opacity -= 0.0035 * deltaFactor;

        if (star.opacity <= 0 || star.y > height + 250 || star.x > width + 250) {
          meteors.splice(i, 1);
        }
      }

      // 2. Neural Nodes & Synapses
      const activeCount = currentIsDark ? totalParticleCount : 52;
      const speedScale = (currentIsDark ? 1.0 : 0.7) * deltaFactor;

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

      // 3. Light Mode Synaptic Pulse Packets
      if (!currentIsDark) {
        for (let k = synapticPulses.length - 1; k >= 0; k--) {
          const pulse = synapticPulses[k];
          pulse.progress += pulse.speed * deltaFactor;
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

    // Page Lifecycle: Pause when tab is backgrounded
    const handleVisibilityChange = () => {
      if (document.hidden) {
        isRunning = false;
        if (animationFrameId !== null) {
          cancelAnimationFrame(animationFrameId);
          animationFrameId = null;
        }
        stopIntervals();
        meteors.length = 0;
        synapticPulses.length = 0;
      } else {
        isRunning = true;
        lastFrameTime = performance.now();
        startIntervals();
        if (animationFrameId === null) {
          animationFrameId = requestAnimationFrame(render);
        }
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    if (!document.hidden) {
      startIntervals();
      animationFrameId = requestAnimationFrame(render);
    }

    return () => {
      isRunning = false;
      window.removeEventListener("resize", handleResize);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      stopIntervals();
      if (animationFrameId !== null) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
    };
  }, [isHero]);

  return (
    <div
      data-testid="dashboard-ambient-bg"
      className="pointer-events-none absolute inset-0 overflow-hidden select-none z-0"
      aria-hidden="true"
    >
      {/* 1. Drafting Grid Container */}
      <div
        data-testid="dashboard-drafting-grid"
        className={`absolute inset-0 pointer-events-none transition-opacity duration-700 ${
          isHero
            ? isDark
              ? "opacity-50"
              : "opacity-40"
            : isDark
            ? "opacity-12"
            : "opacity-12"
        }`}
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

      {/* 5. Celestial Motes Container */}
      <div
        data-testid="dashboard-celestial-motes"
        className={`absolute inset-0 transition-opacity duration-700 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
      />

      {/* 5.5 Interactive Particles & Meteor Canvas */}
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
