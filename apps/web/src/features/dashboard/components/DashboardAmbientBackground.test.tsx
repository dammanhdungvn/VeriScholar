import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardAmbientBackground } from "./DashboardAmbientBackground";

describe("DashboardAmbientBackground - Idea 3: Sunlight (Light Mode) & Moonlight (Dark Mode)", () => {
  it("renders with celestial beam, aurora veils, and floating motes in hero mode", () => {
    render(<DashboardAmbientBackground isHero={true} />);

    const container = screen.getByTestId("dashboard-ambient-bg");
    expect(container).toBeInTheDocument();

    const grid = screen.getByTestId("dashboard-drafting-grid");
    expect(grid).toBeInTheDocument();
    expect(grid.className).toMatch(/opacity-(40|50)/);

    const beam = screen.getByTestId("dashboard-celestial-beam");
    expect(beam).toHaveClass("opacity-100");

    const auroraPrimary = screen.getByTestId("dashboard-celestial-aurora-primary");
    expect(auroraPrimary).toHaveClass("opacity-100");

    const auroraSecondary = screen.getByTestId("dashboard-celestial-aurora-secondary");
    expect(auroraSecondary).toHaveClass("opacity-100");

    const motes = screen.getByTestId("dashboard-celestial-motes");
    expect(motes).toHaveClass("opacity-100");

    const motifs = screen.getByTestId("dashboard-scholar-motifs");
    expect(motifs).toBeInTheDocument();
    expect(motifs).toHaveClass("opacity-100");
  });

  it("smoothly dissolves all celestial elements to 0% opacity when leaving hero mode for reading focus", () => {
    render(<DashboardAmbientBackground isHero={false} />);

    const grid = screen.getByTestId("dashboard-drafting-grid");
    expect(grid).toHaveClass("opacity-12");

    const beam = screen.getByTestId("dashboard-celestial-beam");
    expect(beam).toHaveClass("opacity-0");

    const auroraPrimary = screen.getByTestId("dashboard-celestial-aurora-primary");
    expect(auroraPrimary).toHaveClass("opacity-0");

    const auroraSecondary = screen.getByTestId("dashboard-celestial-aurora-secondary");
    expect(auroraSecondary).toHaveClass("opacity-0");

    const motes = screen.getByTestId("dashboard-celestial-motes");
    expect(motes).toHaveClass("opacity-0");

    const motifs = screen.getByTestId("dashboard-scholar-motifs");
    expect(motifs).toHaveClass("opacity-0");
  });
});
