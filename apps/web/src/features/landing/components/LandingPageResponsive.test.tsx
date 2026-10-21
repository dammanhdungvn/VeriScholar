import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { LandingNavbar } from "./LandingNavbar";
import { HeroSection } from "./HeroSection";
import { InteractiveDemo } from "./InteractiveDemo";

describe("Landing Page Responsive Audit (Mobile, Tablet, Desktop)", () => {
  it("verifies Navbar mobile touch target and responsive brand container", () => {
    render(
      <MemoryRouter>
        <LandingNavbar />
      </MemoryRouter>
    );

    const tryBtn = screen.getByTestId("nav-try-btn");
    expect(tryBtn).toBeInTheDocument();
    // Verify touch target ergonomics
    expect(tryBtn.className).toContain("px-3");
    expect(tryBtn.className).toContain("h-8");
  });

  it("verifies HeroSection monumental headline clamp and zero-overflow layout", () => {
    const { container } = render(<HeroSection />);

    const heroSection = container.querySelector("section");
    expect(heroSection).toHaveClass("overflow-hidden");

    // Feynman quote heading with responsive clamp font classes
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading.className).toContain("text-3xl");
    expect(heading.className).toContain("sm:text-5xl");
    expect(heading.className).toContain("md:text-6xl");
  });

  it("verifies InteractiveDemo dual-pane studio layout adapts on mobile vs desktop", () => {
    const { container } = render(<InteractiveDemo />);

    const demoSection = container.querySelector("#interactive-demo");
    expect(demoSection).toBeInTheDocument();
    expect(demoSection).toHaveClass("overflow-hidden");

    // Grid adapts: 1 column on mobile, 2 columns on desktop
    const grid = container.querySelector(".grid");
    expect(grid).toBeInTheDocument();
    expect(grid?.className).toContain("grid-cols-1");
    expect(grid?.className).toContain("lg:grid-cols-2");
  });
});
