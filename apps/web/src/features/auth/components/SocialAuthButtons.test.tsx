import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SocialAuthButtons } from "./SocialAuthButtons";

describe("SocialAuthButtons component", () => {
  it("renders Google, GitHub and ORCID SSO buttons", () => {
    render(<SocialAuthButtons />);

    expect(screen.getByRole("button", { name: "Google" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "GitHub" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ORCID" })).toBeInTheDocument();
  });

  it("calls onSocialAuth with 'google' when clicking Google button", () => {
    const handleSocialAuth = vi.fn();
    render(<SocialAuthButtons onSocialAuth={handleSocialAuth} />);

    fireEvent.click(screen.getByRole("button", { name: "Google" }));
    expect(handleSocialAuth).toHaveBeenCalledWith("google");
  });

  it("calls onSocialAuth with 'github' when clicking GitHub button", () => {
    const handleSocialAuth = vi.fn();
    render(<SocialAuthButtons onSocialAuth={handleSocialAuth} />);

    fireEvent.click(screen.getByRole("button", { name: "GitHub" }));
    expect(handleSocialAuth).toHaveBeenCalledWith("github");
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
    const githubBtn = screen.getByRole("button", { name: "GitHub" });
    const orcidBtn = screen.getByRole("button", { name: "ORCID" });

    expect(googleBtn).toBeDisabled();
    expect(githubBtn).toBeDisabled();
    expect(orcidBtn).toBeDisabled();

    fireEvent.click(googleBtn);
    fireEvent.click(githubBtn);
    expect(handleSocialAuth).not.toHaveBeenCalled();

    rerender(<SocialAuthButtons onSocialAuth={handleSocialAuth} isLoading={true} />);
    expect(googleBtn).toBeDisabled();
    expect(githubBtn).toBeDisabled();
    expect(orcidBtn).toBeDisabled();
  });
});
