import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RegisterForm } from "./RegisterForm";
import { useAuthStore } from "../stores/useAuthStore";
import { authApi } from "../api/authApi";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("RegisterForm component", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
  });

  it("renders streamlined registration form with 3 core fields and social SSO", () => {
    renderWithProviders(<RegisterForm />);

    expect(screen.getByRole("heading", { name: "Đăng ký" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Google/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /ORCID/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Họ và tên/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Mật khẩu/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Đăng ký$/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Đăng nhập" })).toHaveAttribute("href", "/login");
  });

  it("enforces terms acceptance and password strength before submit button can be enabled", () => {
    renderWithProviders(<RegisterForm />);

    const submitBtn = screen.getByRole("button", { name: /^Đăng ký$/i });
    expect(submitBtn).toBeDisabled();

    // Fill in valid fields
    fireEvent.change(screen.getByLabelText(/Họ và tên/i), {
      target: { value: "GS.TS. Nguyen Van A" },
    });
    fireEvent.change(screen.getByLabelText(/^Email/i), {
      target: { value: "nguyenvana@oxford.ac.uk" },
    });
    fireEvent.change(screen.getByLabelText(/^Mật khẩu/i), {
      target: { value: "StrongPassword123!" },
    });

    // Still disabled because accept-terms is false
    expect(submitBtn).toBeDisabled();

    // Toggle accept-terms
    const termsCheckbox = screen.getByRole("checkbox");
    fireEvent.click(termsCheckbox);

    // Now submit button should be enabled
    expect(submitBtn).not.toBeDisabled();
  });

  it("validates full name requiring at least 2 words", () => {
    renderWithProviders(<RegisterForm />);

    const fullNameInput = screen.getByLabelText(/Họ và tên/i);
    fireEvent.change(fullNameInput, { target: { value: "SingleWord" } });
    fireEvent.blur(fullNameInput);

    expect(screen.getByText(/tối thiểu 2 từ/i)).toBeInTheDocument();
  });

  it("blocks disposable email addresses in real time", () => {
    renderWithProviders(<RegisterForm />);

    const emailInput = screen.getByLabelText(/^Email/i);
    fireEvent.change(emailInput, { target: { value: "fake@mailinator.com" } });
    fireEvent.blur(emailInput);

    expect(screen.getByText(/dịch vụ email tạm thời/i)).toBeInTheDocument();
  });

  it("opens SocialConnectModal when clicking Google SSO button", () => {
    renderWithProviders(<RegisterForm />);

    const googleBtn = screen.getByRole("button", { name: /Google/i });
    fireEvent.click(googleBtn);

    expect(screen.getByText(/Xác thực qua Google Workspace/i)).toBeInTheDocument();
  });

  it("opens OtpVerificationModal on valid submission after calling register API", async () => {
    const registerSpy = vi.spyOn(authApi, "register").mockResolvedValueOnce({
      user: {
        id: "mock-uid-123",
        email: "nguyenvanb@hcmut.edu.vn",
        full_name: "Nguyen Van B",
        role: "researcher",
        is_verified: false,
        created_at: new Date().toISOString(),
      },
      tokens: {
        access_token: "mock-access-token",
        refresh_token: "mock-refresh-token",
        token_type: "bearer",
        expires_in: 3600,
      },
      message: "Khởi tạo tài khoản thành công",
    });

    renderWithProviders(<RegisterForm />);

    fireEvent.change(screen.getByLabelText(/Họ và tên/i), {
      target: { value: "Nguyen Van B" },
    });
    fireEvent.change(screen.getByLabelText(/^Email/i), {
      target: { value: "nguyenvanb@hcmut.edu.vn" },
    });
    fireEvent.change(screen.getByLabelText(/^Mật khẩu/i), {
      target: { value: "StrongPass123@" },
    });
    fireEvent.click(screen.getByRole("checkbox"));

    const submitBtn = screen.getByRole("button", { name: /^Đăng ký$/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(registerSpy).toHaveBeenCalledWith({
        full_name: "Nguyen Van B",
        email: "nguyenvanb@hcmut.edu.vn",
        password: "StrongPass123@",
        accept_terms: true,
      });
      expect(screen.getByText("Xác thực Email học thuật")).toBeInTheDocument();
      expect(screen.getByText("nguyenvanb@hcmut.edu.vn")).toBeInTheDocument();
    });
  });

  it("toggles password visibility when clicking eye button", () => {
    renderWithProviders(<RegisterForm />);

    const passwordInput = screen.getByLabelText(/^Mật khẩu/i) as HTMLInputElement;
    expect(passwordInput.type).toBe("password");

    const toggleBtn = screen.getByRole("button", { name: /Hiện mật khẩu/i });
    fireEvent.click(toggleBtn);

    expect(passwordInput.type).toBe("text");

    const hideBtn = screen.getByRole("button", { name: /Ẩn mật khẩu/i });
    fireEvent.click(hideBtn);

    expect(passwordInput.type).toBe("password");
  });

  it("displays error alert when register API fails with 400/500 error", async () => {
    vi.spyOn(authApi, "register").mockRejectedValueOnce(
      new Error("Email này đã được đăng ký bởi một tài khoản khác.")
    );

    renderWithProviders(<RegisterForm />);

    fireEvent.change(screen.getByLabelText(/Họ và tên/i), {
      target: { value: "Tran Thi B" },
    });
    fireEvent.change(screen.getByLabelText(/^Email/i), {
      target: { value: "tranthib@hcmut.edu.vn" },
    });
    fireEvent.change(screen.getByLabelText(/^Mật khẩu/i), {
      target: { value: "StrongPass123@" },
    });
    fireEvent.click(screen.getByRole("checkbox"));

    const submitBtn = screen.getByRole("button", { name: /^Đăng ký$/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Email này đã được đăng ký bởi một tài khoản khác.");
      expect(screen.queryByText("Xác thực Email học thuật")).not.toBeInTheDocument();
    });
  });

  it("strictly blocks non-whitelisted domains like maxxspace.com at UI layer", async () => {
    renderWithProviders(<RegisterForm />);

    const emailInput = screen.getByLabelText(/^Email/i);
    fireEvent.change(emailInput, {
      target: { value: "admin@maxxspace.com" },
    });
    fireEvent.blur(emailInput);

    expect(screen.getByText(/không thuộc danh mục được phép/i)).toBeInTheDocument();

    const submitBtn = screen.getByRole("button", { name: /^Đăng ký$/i });
    expect(submitBtn).toBeDisabled();
  });
});
