import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SocialAuthButtons } from "./SocialAuthButtons";

describe("SocialAuthButtons component", () => {
  it("renders Google and ORCID SSO buttons", () => {
    render(<SocialAuthButtons />);

    expect(screen.getByRole("button", { name: "Google" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ORCID" })).toBeInTheDocument();
  });

  it("calls onSocialAuth with 'google' when clicking Google button", () => {
    const handleSocialAuth = vi.fn();
    render(<SocialAuthButtons onSocialAuth={handleSocialAuth} />);

    fireEvent.click(screen.getByRole("button", { name: "Google" }));
    expect(handleSocialAuth).toHaveBeenCalledWith("google");
  });

  it("calls onSocialAuth with 'orcid' when clicking ORCID button", () => {
    const handleSocialAuth = vi.fn();
    render(<SocialAuthButtons onSocialAuth={handleSocialAuth} />);

    fireEvent.click(screen.getByRole("button", { name: "ORCID" }));
    expect(handleSocialAuth).toHaveBeenCalledWith("orcid");
  });

  it("disables buttons when disabled or isLoading is true", () => {
    const handleSocialAuth = vi.fn();
    const { rerender } = render(
      <SocialAuthButtons onSocialAuth={handleSocialAuth} disabled={true} />
    );

    const googleBtn = screen.getByRole("button", { name: "Google" });
    const orcidBtn = screen.getByRole("button", { name: "ORCID" });

    expect(googleBtn).toBeDisabled();
    expect(orcidBtn).toBeDisabled();

    fireEvent.click(googleBtn);
    expect(handleSocialAuth).not.toHaveBeenCalled();

    rerender(<SocialAuthButtons onSocialAuth={handleSocialAuth} isLoading={true} />);
    expect(googleBtn).toBeDisabled();
    expect(orcidBtn).toBeDisabled();
  });
});
