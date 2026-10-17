import { useEffect, useRef } from "react";
import { useTheme } from "@/hooks/useTheme";

const MAX_METEORS = 8;
const MAX_SYNAPTIC_PULSES = 8;

export function AtmosphericBackground() {
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const isDarkRef = useRef(isDark);

  useEffect(() => {
    isDarkRef.current = isDark;
  }, [isDark]);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const spotlightRef = useRef<HTMLDivElement | null>(null);
  const mousePosRef = useRef({ x: -1000, y: -1000 });

  // 1. Off-Thread / Direct DOM Spotlight Tracking (0 React Re-renders on mousemove)
  useEffect(() => {
    const handleWindowMouseMove = (e: MouseEvent) => {
      mousePosRef.current = { x: e.clientX, y: e.clientY };
      if (spotlightRef.current) {
        const dark = isDarkRef.current;
        spotlightRef.current.style.background = dark
          ? `radial-gradient(650px circle at ${e.clientX}px ${e.clientY}px, rgba(217, 119, 87, 0.12), transparent 60%)`
          : `radial-gradient(650px circle at ${e.clientX}px ${e.clientY}px, rgba(204, 110, 75, 0.10), transparent 60%)`;
      }
    };

    const handleMouseLeave = () => {
      mousePosRef.current = { x: -1000, y: -1000 };
      if (spotlightRef.current) {
        spotlightRef.current.style.background = "none";
      }
    };

    window.addEventListener("mousemove", handleWindowMouseMove, { passive: true });
    document.addEventListener("mouseleave", handleMouseLeave);
    return () => {
      window.removeEventListener("mousemove", handleWindowMouseMove);
      document.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);

  // 2. High-Performance Particle Engine with Tab-Visibility & Memory Leaking Safeguards
  useEffect(() => {
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

    // Effect 2: Dark Mode 6s Periodic Meteors (Capped at MAX_METEORS to prevent background memory pileup)
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
      // Guard 1: Do not spawn when tab is hidden or in light mode
      if (document.hidden || !isDarkRef.current) return;
      // Guard 2: Hard upper bound - never accumulate runaway meteors
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
      initialTimeout = setTimeout(spawnMeteorShowerWave, 1200);
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

      // Delta time normalization (capped at 2.0x to avoid teleports upon tab reactivation)
      const elapsed = currentTime - lastFrameTime;
      lastFrameTime = currentTime;
      const deltaFactor = Math.min(Math.max(elapsed / 16.67, 0.1), 2.0);

      ctx.clearRect(0, 0, width, height);
      const m = mousePosRef.current;
      const currentIsDark = isDarkRef.current;

      // 1. Dark Mode Meteors Rendering
      if (currentIsDark) {
        for (let i = meteors.length - 1; i >= 0; i--) {
          const star = meteors[i];
          const tailX = star.x - Math.cos(star.angle) * star.length;
          const tailY = star.y - Math.sin(star.angle) * star.length;

          const grad = ctx.createLinearGradient(star.x, star.y, tailX, tailY);
          grad.addColorStop(0, `rgba(255, 255, 255, ${star.opacity})`);
          grad.addColorStop(0.2, `rgba(255, 220, 190, ${star.opacity * 0.85})`);
          grad.addColorStop(0.65, `rgba(217, 119, 87, ${star.opacity * 0.35})`);
          grad.addColorStop(1, "rgba(217, 119, 87, 0)");

          ctx.beginPath();
          ctx.moveTo(star.x, star.y);
          ctx.lineTo(tailX, tailY);
          ctx.lineWidth = star.width;
          ctx.strokeStyle = grad;
          ctx.lineCap = "round";

          ctx.shadowBlur = 16;
          ctx.shadowColor = "#e89b82";
          ctx.stroke();
          ctx.shadowBlur = 0;

          star.x += Math.cos(star.angle) * star.speed * deltaFactor;
          star.y += Math.sin(star.angle) * star.speed * deltaFactor;
          star.opacity -= 0.0035 * deltaFactor;

          if (star.opacity <= 0 || star.y > height + 250 || star.x > width + 250) {
            meteors.splice(i, 1);
          }
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

    // 3. Page Lifecycle / Background Tab Management: Pause completely when tab is hidden
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Tab went to background: pause rendering & stop spawning
        isRunning = false;
        if (animationFrameId !== null) {
          cancelAnimationFrame(animationFrameId);
          animationFrameId = null;
        }
        stopIntervals();
        // Purge any lingering meteors so reactivation is 100% clean and zero-lag
        meteors.length = 0;
        synapticPulses.length = 0;
      } else {
        // Tab became visible again: resume smoothly
        isRunning = true;
        lastFrameTime = performance.now();
        startIntervals();
        if (animationFrameId === null) {
          animationFrameId = requestAnimationFrame(render);
        }
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Initial start if page is visible
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
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {/* Perspective Grid Background */}
      <div
        className={`absolute inset-0 transition-opacity duration-300 ${isDark ? "opacity-15" : "opacity-35"}`}
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

      {/* Interactive Mouse Spotlight Follower (Updated directly via ref to eliminate React render overhead) */}
      <div
        ref={spotlightRef}
        className="absolute inset-0 transition-opacity duration-300"
      />

      {/* Ambient Rotating Glow Orbs */}
      <div
        className={`absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] blur-3xl rounded-full pointer-events-none animate-pulse duration-10000 ${
          isDark
            ? "bg-gradient-to-b from-[#d97757]/18 via-[#e89b82]/6 to-transparent"
            : "bg-gradient-to-b from-[#d97757]/14 via-[#e89b82]/5 to-transparent"
        }`}
      />
      <div
        className={`absolute top-1/4 -left-40 w-80 h-80 blur-3xl rounded-full pointer-events-none ${
          isDark ? "bg-[#d97757]/10" : "bg-[#d97757]/6"
        }`}
      />
      <div
        className={`absolute bottom-1/3 -right-40 w-80 h-80 blur-3xl rounded-full pointer-events-none ${
          isDark ? "bg-[#e8a55a]/10" : "bg-[#e8a55a]/6"
        }`}
      />

      {/* Interactive Canvas */}
      <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none z-10" />
    </div>
  );
}
