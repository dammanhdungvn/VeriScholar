import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RegisterForm } from "./RegisterForm";
import { useAuthStore } from "../stores/useAuthStore";

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
});
