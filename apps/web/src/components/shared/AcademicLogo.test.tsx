import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AcademicLogo } from "./AcademicLogo";

describe("AcademicLogo component", () => {
  it("renders light logo SVG image by default for light backgrounds", () => {
    render(<AcademicLogo />);
    const img = screen.getByRole("img", { name: /VeriScholar/i });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("src", "/images/VeriScholar_logo_light.svg");
    expect(screen.getByText(/Veri/i)).toBeInTheDocument();
    expect(screen.getByText(/Scholar/i)).toBeInTheDocument();
  });

  it("renders dark logo SVG image when inverted is true for dark backgrounds", () => {
    render(<AcademicLogo inverted />);
    const img = screen.getByRole("img", { name: /VeriScholar/i });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("src", "/images/VeriScholar_logo_dark.svg");
  });

  it("hides wordmark when showWordmark is false", () => {
    render(<AcademicLogo showWordmark={false} />);
    expect(screen.queryByText(/Scholar/i)).not.toBeInTheDocument();
  });
});
