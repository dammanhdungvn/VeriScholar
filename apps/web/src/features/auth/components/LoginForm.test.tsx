import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LoginForm } from "./LoginForm";
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

describe("LoginForm component", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
  });

  it("renders login form with all elements properly", () => {
    renderWithProviders(<LoginForm />);

    expect(screen.getByRole("heading", { name: "Đăng nhập" })).toBeInTheDocument();
    expect(screen.getByLabelText(/^Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Mật khẩu/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Đăng nhập$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Google/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /ORCID/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Đăng ký tài khoản" })).toHaveAttribute("href", "/register");
  });

  it("opens SocialConnectModal when clicking ORCID button", () => {
    renderWithProviders(<LoginForm />);

    const orcidBtn = screen.getByRole("button", { name: /ORCID/i });
    fireEvent.click(orcidBtn);

    expect(screen.getByText(/Liên kết định danh học thuật ORCID/i)).toBeInTheDocument();
  });

  it("warns about disposable emails on blur", () => {
    renderWithProviders(<LoginForm />);

    const emailInput = screen.getByLabelText(/^Email/i);
    fireEvent.change(emailInput, { target: { value: "hacker@tempmail.com" } });
    fireEvent.blur(emailInput);

    expect(screen.getByText(/dịch vụ email tạm thời/i)).toBeInTheDocument();
  });

  it("toggles password visibility when clicking eye button", () => {
    renderWithProviders(<LoginForm />);

    const passwordInput = screen.getByLabelText(/^Mật khẩu/i) as HTMLInputElement;
    expect(passwordInput.type).toBe("password");

    const toggleBtn = screen.getByRole("button", { name: /Hiện mật khẩu/i });
    fireEvent.click(toggleBtn);

    expect(passwordInput.type).toBe("text");

    const hideBtn = screen.getByRole("button", { name: /Ẩn mật khẩu/i });
    fireEvent.click(hideBtn);

    expect(passwordInput.type).toBe("password");
  });

  it("authenticates via Google when token is submitted from modal", async () => {
    const googleLoginSpy = vi.spyOn(authApi, "googleLogin").mockResolvedValueOnce({
      user: {
        id: "mock-google-id",
        email: "scholar@oxford.ac.uk",
        full_name: "Prof. Oxford",
        role: "researcher",
        is_verified: true,
        created_at: new Date().toISOString(),
      },
      tokens: {
        access_token: "mock-access-token",
        refresh_token: "mock-refresh-token",
        token_type: "bearer",
        expires_in: 3600,
      },
      message: "Success",
    });

    renderWithProviders(<LoginForm />);

    const googleBtn = screen.getByRole("button", { name: /Google/i });
    fireEvent.click(googleBtn);

    const tokenInput = screen.getByPlaceholderText(/mock_google:scholar@oxford\.ac\.uk/i);
    fireEvent.change(tokenInput, { target: { value: "mock_google_id_token" } });

    const submitBtn = screen.getByRole("button", { name: /Xác nhận/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(googleLoginSpy).toHaveBeenCalledWith("mock_google_id_token");
    });
  });

  it("validates empty email and password on form submission, showing error alert", () => {
    renderWithProviders(<LoginForm />);

    const form = screen.getByRole("button", { name: /^Đăng nhập$/i }).closest("form")!;
    fireEvent.submit(form);

    expect(screen.getByRole("alert")).toHaveTextContent("Vui lòng nhập đầy đủ Email và Mật khẩu.");
  });

  it("validates non-whitelisted email domain on submission and shows error", () => {
    renderWithProviders(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/^Email/i), {
      target: { value: "user@disposable-unknown.xyz" },
    });
    fireEvent.change(screen.getByLabelText(/^Mật khẩu/i), {
      target: { value: "ValidPassword123!" },
    });

    const form = screen.getByRole("button", { name: /^Đăng nhập$/i }).closest("form")!;
    fireEvent.submit(form);

    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("displays error alert when login API fails with 401 Unauthorized or 500", async () => {
    vi.spyOn(authApi, "login").mockRejectedValueOnce(
      new Error("Email hoặc mật khẩu không chính xác.")
    );

    renderWithProviders(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/^Email/i), {
      target: { value: "scholar@stanford.edu" },
    });
    fireEvent.change(screen.getByLabelText(/^Mật khẩu/i), {
      target: { value: "WrongPassword123!" },
    });

    const form = screen.getByRole("button", { name: /^Đăng nhập$/i }).closest("form")!;
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Email hoặc mật khẩu không chính xác.");
    });
  });

  it("submits valid credentials successfully and updates useAuthStore", async () => {
    const loginSpy = vi.spyOn(authApi, "login").mockResolvedValueOnce({
      user: {
        id: "usr-real-123",
        email: "prof@oxford.ac.uk",
        full_name: "Prof. John Doe",
        role: "researcher",
        is_verified: true,
        created_at: new Date().toISOString(),
      },
      tokens: {
        access_token: "jwt-token-123",
        refresh_token: "refresh-token-123",
        token_type: "bearer",
        expires_in: 3600,
      },
      message: "Đăng nhập thành công",
    });

    renderWithProviders(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/^Email/i), {
      target: { value: "prof@oxford.ac.uk" },
    });
    fireEvent.change(screen.getByLabelText(/^Mật khẩu/i), {
      target: { value: "StrongPass123@" },
    });

    const form = screen.getByRole("button", { name: /^Đăng nhập$/i }).closest("form")!;
    fireEvent.submit(form);

    await waitFor(() => {
      expect(loginSpy).toHaveBeenCalledWith({
        email: "prof@oxford.ac.uk",
        password: "StrongPass123@",
        remember_me: true,
      });
      expect(useAuthStore.getState().user?.email).toBe("prof@oxford.ac.uk");
    });
  });
});
