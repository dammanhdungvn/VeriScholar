import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { HeroSection } from "./HeroSection";

describe("HeroSection component", () => {
  it("renders the Richard Feynman academic slogan quote", () => {
    render(<HeroSection />);
    const quote = screen.getByRole("heading", { level: 1 });
    expect(quote).toBeInTheDocument();
    expect(quote.textContent).toContain("What I cannot create, I do not understand");

    expect(screen.getByText(/Richard Feynman/i)).toBeInTheDocument();
  });
});
