import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { HeroSection } from "./HeroSection";
import { useLandingStore } from "../stores/useLandingStore";

describe("HeroSection component", () => {
  beforeEach(() => {
    useLandingStore.getState().setUploadModalOpen(false);
  });

  it("renders the primary academic headline and lead text", () => {
    render(<HeroSection />);
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading.textContent).toContain("Nền tảng Trợ lý AI Hỗ trợ Nghiên cứu");

    expect(screen.getByText(/Triệt tiêu 100%/i)).toBeInTheDocument();
  });

  it("triggers upload modal when clicking the primary CTA button", () => {
    render(<HeroSection />);
    const ctaButton = screen.getByTestId("hero-quick-upload-btn");

    expect(useLandingStore.getState().isUploadModalOpen).toBe(false);
    fireEvent.click(ctaButton);
    expect(useLandingStore.getState().isUploadModalOpen).toBe(true);
  });
});
