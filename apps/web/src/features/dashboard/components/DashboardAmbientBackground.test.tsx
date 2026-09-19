import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardAmbientBackground } from "./DashboardAmbientBackground";

describe("DashboardAmbientBackground component", () => {
  it("renders with prominent opacity in hero mode", () => {
    render(<DashboardAmbientBackground isHero={true} />);

    const container = screen.getByTestId("dashboard-ambient-bg");
    expect(container).toBeInTheDocument();

    const grid = screen.getByTestId("dashboard-drafting-grid");
    expect(grid).toBeInTheDocument();
    expect(grid.className).toMatch(/opacity-(45|60)/);

    const spotlight = screen.getByTestId("dashboard-ambient-spotlight");
    expect(spotlight).toHaveClass("opacity-100");
  });

  it("reduces opacity gracefully when not in hero mode to preserve reading focus", () => {
    render(<DashboardAmbientBackground isHero={false} />);

    const grid = screen.getByTestId("dashboard-drafting-grid");
    expect(grid).toHaveClass("opacity-15");

    const spotlight = screen.getByTestId("dashboard-ambient-spotlight");
    expect(spotlight).toHaveClass("opacity-0");
  });
});
