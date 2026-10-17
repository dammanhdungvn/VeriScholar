import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SocialConnectModal } from "./SocialConnectModal";

describe("SocialConnectModal component", () => {
  it("renders Google Workspace notice when provider is google", () => {
    const handleClose = vi.fn();
    render(
      <SocialConnectModal
        open={true}
        onOpenChange={handleClose}
        provider="google"
      />
    );

    expect(screen.getByText(/Xác thực qua Google Workspace/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Google Workspace for Education \(OAuth 2\.0\)/i)
    ).toBeInTheDocument();
  });

  it("renders ORCID notice when provider is orcid", () => {
    const handleClose = vi.fn();
    render(
      <SocialConnectModal
        open={true}
        onOpenChange={handleClose}
        provider="orcid"
      />
    );

    expect(
      screen.getByText(/Liên kết định danh học thuật ORCID/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/ORCID Member API/i)).toBeInTheDocument();
  });

  it("calls onAcknowledge and onOpenChange when user clicks acknowledgment button", () => {
    const handleOpenChange = vi.fn();
    const handleAcknowledge = vi.fn();

    render(
      <SocialConnectModal
        open={true}
        onOpenChange={handleOpenChange}
        provider="google"
        onAcknowledge={handleAcknowledge}
      />
    );

    const btn = screen.getByRole("button", {
      name: /Tôi đã hiểu, quay lại biểu mẫu/i,
    });
    fireEvent.click(btn);

    expect(handleOpenChange).toHaveBeenCalledWith(false);
    expect(handleAcknowledge).toHaveBeenCalled();
  });

  it("submits Google token when onGoogleTokenSubmit is provided", () => {
    const handleTokenSubmit = vi.fn();
    render(
      <SocialConnectModal
        open={true}
        onOpenChange={vi.fn()}
        provider="google"
        onGoogleTokenSubmit={handleTokenSubmit}
      />
    );

    const input = screen.getByPlaceholderText(/mock_google:scholar@oxford\.ac\.uk/i);
    fireEvent.change(input, { target: { value: "test-token-777" } });

    const submitBtn = screen.getByRole("button", { name: /Xác nhận/i });
    fireEvent.click(submitBtn);

    expect(handleTokenSubmit).toHaveBeenCalledWith("test-token-777");
  });
});
