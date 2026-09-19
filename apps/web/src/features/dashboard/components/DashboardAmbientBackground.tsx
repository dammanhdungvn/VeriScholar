import { useTheme } from "@/hooks/useTheme";

interface DashboardAmbientBackgroundProps {
  /**
   * Whether the dashboard is in the Hero / Empty state (where ambient depth is most prominent).
   * When false (in active chat or cowork PDF mode), background gracefully softens for reading focus.
   */
  isHero?: boolean;
}

export function DashboardAmbientBackground({ isHero = true }: DashboardAmbientBackgroundProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div
      data-testid="dashboard-ambient-bg"
      className="pointer-events-none absolute inset-0 overflow-hidden select-none z-0"
      aria-hidden="true"
    >
      {/* 1. Perspective Academic Drafting Grid - Concentrates around center input and fades to edges */}
      <div
        data-testid="dashboard-drafting-grid"
        className={`absolute inset-0 transition-opacity duration-700 ${
          isHero
            ? isDark
              ? "opacity-60"
              : "opacity-45"
            : isDark
            ? "opacity-15"
            : "opacity-15"
        }`}
        style={{
          backgroundImage: isDark
            ? `linear-gradient(to right, rgba(255, 255, 255, 0.12) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(255, 255, 255, 0.12) 1px, transparent 1px)`
            : `linear-gradient(to right, rgba(165, 120, 85, 0.18) 1px, transparent 1px),
               linear-gradient(to bottom, rgba(165, 120, 85, 0.18) 1px, transparent 1px)`,
          backgroundSize: "40px 40px",
          maskImage: "radial-gradient(ellipse 80% 70% at 50% 45%, black 30%, transparent 100%)",
          WebkitMaskImage: "radial-gradient(ellipse 80% 70% at 50% 45%, black 30%, transparent 100%)",
        }}
      />

      {/* 2. Central Warm Ambient Spotlight - Illuminates behind the hero greeting & input container */}
      <div
        data-testid="dashboard-ambient-spotlight"
        className={`absolute inset-0 transition-opacity duration-700 ${
          isHero ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isDark
            ? `radial-gradient(ellipse 750px 480px at 50% 45%, rgba(217, 119, 87, 0.16), transparent 70%)`
            : `radial-gradient(ellipse 750px 480px at 50% 45%, rgba(204, 120, 92, 0.14), transparent 70%)`,
        }}
      />

      {/* 3. Ambient Soft Glowing Orbs - Adds warm academic aura */}
      <div
        data-testid="dashboard-ambient-orb-top"
        className={`absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[350px] blur-3xl rounded-full transition-opacity duration-700 ${
          isHero
            ? isDark
              ? "bg-[#d97757]/12 opacity-100"
              : "bg-[#d97757]/10 opacity-100"
            : "opacity-0"
        }`}
      />
      <div
        data-testid="dashboard-ambient-orb-corner"
        className={`absolute -bottom-24 right-1/4 w-[400px] h-[300px] blur-3xl rounded-full transition-opacity duration-700 ${
          isHero
            ? isDark
              ? "bg-[#e8a55a]/8 opacity-100"
              : "bg-[#e8a55a]/7 opacity-100"
            : "opacity-0"
        }`}
      />
    </div>
  );
}
