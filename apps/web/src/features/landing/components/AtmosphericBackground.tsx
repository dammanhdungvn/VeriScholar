import { useEffect, useRef, useState } from "react";

export function AtmosphericBackground() {
  const [mousePos, setMousePos] = useState({ x: -1000, y: -1000 });
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const mousePosRef = useRef({ x: -1000, y: -1000 });

  useEffect(() => {
    const handleWindowMouseMove = (e: MouseEvent) => {
      const pos = { x: e.clientX, y: e.clientY };
      setMousePos(pos);
      mousePosRef.current = pos;
    };

    window.addEventListener("mousemove", handleWindowMouseMove);
    return () => window.removeEventListener("mousemove", handleWindowMouseMove);
  }, []);

  useEffect(() => {
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

    // Effect 1: Constellation Particles
    const particleCount = 65;
    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      radius: number;
      opacity: number;
    }> = [];

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.6,
        vy: (Math.random() - 0.5) * 0.6,
        radius: Math.random() * 1.6 + 0.8,
        opacity: Math.random() * 0.4 + 0.3,
      });
    }

    // Effect 2: 6s Periodic Meteors
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
    const initialTimeout = setTimeout(spawnMeteorShowerWave, 1200);

    const render = () => {
      ctx.clearRect(0, 0, width, height);
      const m = mousePosRef.current;

      // Render Meteors
      for (let i = meteors.length - 1; i >= 0; i--) {
        const star = meteors[i];
        const tailX = star.x - Math.cos(star.angle) * star.length;
        const tailY = star.y - Math.sin(star.angle) * star.length;

        const grad = ctx.createLinearGradient(star.x, star.y, tailX, tailY);
        grad.addColorStop(0, `rgba(255, 255, 255, ${star.opacity})`);
        grad.addColorStop(0.2, `rgba(245, 230, 220, ${star.opacity * 0.85})`);
        grad.addColorStop(0.65, `rgba(217, 119, 87, ${star.opacity * 0.3})`);
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

        star.x += Math.cos(star.angle) * star.speed;
        star.y += Math.sin(star.angle) * star.speed;
        star.opacity -= 0.0035;

        if (star.opacity <= 0 || star.y > height + 250 || star.x > width + 250) {
          meteors.splice(i, 1);
        }
      }

      // Render Constellation Particles
      for (let i = 0; i < particleCount; i++) {
        const p1 = particles[i];
        p1.x += p1.vx;
        p1.y += p1.vy;

        if (p1.x < 0 || p1.x > width) p1.vx *= -1;
        if (p1.y < 0 || p1.y > height) p1.vy *= -1;

        ctx.beginPath();
        ctx.arc(p1.x, p1.y, p1.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(232, 155, 130, ${p1.opacity})`;
        ctx.shadowBlur = 8;
        ctx.shadowColor = "#d97757";
        ctx.fill();
        ctx.shadowBlur = 0;

        for (let j = i + 1; j < particleCount; j++) {
          const p2 = particles[j];
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            const lineAlpha = (1 - dist / 120) * 0.25;
            ctx.strokeStyle = `rgba(217, 119, 87, ${lineAlpha})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }

        if (m.x > 0 && m.y > 0) {
          const mDx = p1.x - m.x;
          const mDy = p1.y - m.y;
          const mDist = Math.sqrt(mDx * mDx + mDy * mDy);

          if (mDist < 160) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(m.x, m.y);
            const mAlpha = (1 - mDist / 160) * 0.45;
            ctx.strokeStyle = `rgba(240, 180, 160, ${mAlpha})`;
            ctx.lineWidth = 1.1;
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", handleResize);
      clearInterval(meteorInterval);
      clearTimeout(initialTimeout);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {/* Perspective Grid Background */}
      <div
        className="absolute inset-0 opacity-15"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px)
          `,
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse 80% 60% at 50% 25%, black 40%, transparent 100%)",
          WebkitMaskImage: "radial-gradient(ellipse 80% 60% at 50% 25%, black 40%, transparent 100%)",
        }}
      />

      {/* Interactive Mouse Spotlight Follower */}
      <div
        className="absolute inset-0 transition-opacity duration-300"
        style={{
          background: `radial-gradient(650px circle at ${mousePos.x}px ${mousePos.y}px, rgba(217, 119, 87, 0.12), transparent 60%)`,
        }}
      />

      {/* Ambient Rotating Glow Orbs */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-b from-[#d97757]/18 via-[#e89b82]/6 to-transparent blur-3xl rounded-full pointer-events-none animate-pulse duration-10000" />
      <div className="absolute top-1/4 -left-40 w-80 h-80 bg-[#d97757]/10 blur-3xl rounded-full pointer-events-none" />
      <div className="absolute bottom-1/3 -right-40 w-80 h-80 bg-[#e8a55a]/10 blur-3xl rounded-full pointer-events-none" />

      {/* Interactive Canvas */}
      <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none z-10" />
    </div>
  );
}
