import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { OtpVerificationModal } from "./OtpVerificationModal";

describe("OtpVerificationModal component", () => {
  it("renders 6 digit input boxes and target email in registration mode", () => {
    render(
      <OtpVerificationModal
        open={true}
        onOpenChange={vi.fn()}
        email="scholar@stanford.edu"
        mode="registration"
        onVerify={vi.fn()}
      />
    );

    expect(screen.getByText("Xác thực Email học thuật")).toBeInTheDocument();
    expect(screen.getByText("scholar@stanford.edu")).toBeInTheDocument();

    for (let i = 0; i < 6; i++) {
      expect(screen.getByTestId(`otp-input-${i}`)).toBeInTheDocument();
    }

    const submitBtn = screen.getByRole("button", { name: "Xác nhận & Kích hoạt" });
    expect(submitBtn).toBeDisabled();
  });

  it("allows entering 6 digits and submits OTP", async () => {
    const handleVerify = vi.fn().mockResolvedValue(undefined);
    render(
      <OtpVerificationModal
        open={true}
        onOpenChange={vi.fn()}
        email="scholar@stanford.edu"
        mode="registration"
        onVerify={handleVerify}
      />
    );

    // Enter digits 123456
    for (let i = 0; i < 6; i++) {
      fireEvent.change(screen.getByTestId(`otp-input-${i}`), {
        target: { value: String(i + 1) },
      });
    }

    const submitBtn = screen.getByRole("button", { name: "Xác nhận & Kích hoạt" });
    expect(submitBtn).not.toBeDisabled();

    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(handleVerify).toHaveBeenCalledWith("123456", undefined);
    });
  });

  it("handles pasting 6-digit OTP code", () => {
    render(
      <OtpVerificationModal
        open={true}
        onOpenChange={vi.fn()}
        email="scholar@stanford.edu"
        mode="registration"
        onVerify={vi.fn()}
      />
    );

    const firstInput = screen.getByTestId("otp-input-0");
    fireEvent.paste(firstInput, {
      clipboardData: {
        getData: () => "654321",
      },
    });

    for (let i = 0; i < 6; i++) {
      const input = screen.getByTestId(`otp-input-${i}`) as HTMLInputElement;
      expect(input.value).toBe(String("654321"[i]));
    }
  });

  it("renders password reset inputs in forgot_password mode", () => {
    render(
      <OtpVerificationModal
        open={true}
        onOpenChange={vi.fn()}
        email="scholar@stanford.edu"
        mode="forgot_password"
        onVerify={vi.fn()}
      />
    );

    expect(screen.getByText("Khôi phục mật khẩu tài khoản")).toBeInTheDocument();
    expect(screen.getByLabelText(/^Mật khẩu mới/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Xác nhận mật khẩu mới/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Đặt lại mật khẩu" })).toBeInTheDocument();
  });

  it("displays error alert when onVerify rejects with invalid/expired OTP", async () => {
    const handleVerify = vi.fn().mockRejectedValueOnce(
      new Error("Mã OTP không chính xác hoặc đã hết hiệu lực. Vui lòng thử lại.")
    );

    render(
      <OtpVerificationModal
        open={true}
        onOpenChange={vi.fn()}
        email="scholar@stanford.edu"
        mode="registration"
        onVerify={handleVerify}
      />
    );

    for (let i = 0; i < 6; i++) {
      fireEvent.change(screen.getByTestId(`otp-input-${i}`), {
        target: { value: "9" },
      });
    }

    const submitBtn = screen.getByRole("button", { name: "Xác nhận & Kích hoạt" });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Mã OTP không chính xác hoặc đã hết hiệu lực. Vui lòng thử lại."
      );
    });
  });

  it("validates password mismatch and strength in forgot_password mode", async () => {
    const handleVerify = vi.fn();
    render(
      <OtpVerificationModal
        open={true}
        onOpenChange={vi.fn()}
        email="scholar@stanford.edu"
        mode="forgot_password"
        onVerify={handleVerify}
      />
    );

    for (let i = 0; i < 6; i++) {
      fireEvent.change(screen.getByTestId(`otp-input-${i}`), {
        target: { value: "1" },
      });
    }

    // 1. Weak password
    fireEvent.change(screen.getByLabelText(/^Mật khẩu mới/i), {
      target: { value: "weak" },
    });
    fireEvent.change(screen.getByLabelText(/^Xác nhận mật khẩu mới/i), {
      target: { value: "weak" },
    });

    const submitBtn = screen.getByRole("button", { name: "Đặt lại mật khẩu" });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Mật khẩu mới cần tối thiểu 8 ký tự");
    });

    // 2. Mismatch password
    fireEvent.change(screen.getByLabelText(/^Mật khẩu mới/i), {
      target: { value: "StrongPass123@" },
    });
    fireEvent.change(screen.getByLabelText(/^Xác nhận mật khẩu mới/i), {
      target: { value: "DifferentPass123@" },
    });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Mật khẩu xác nhận không khớp.");
    });
  });
});
