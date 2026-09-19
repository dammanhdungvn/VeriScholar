import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LoginForm } from "./LoginForm";
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
    expect(screen.getByTestId("quick-fill-demo-btn")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Đăng ký tài khoản" })).toHaveAttribute("href", "/register");
  });

  it("populates demo account details when clicking quick fill button", () => {
    renderWithProviders(<LoginForm />);

    const quickFillBtn = screen.getByTestId("quick-fill-demo-btn");
    fireEvent.click(quickFillBtn);

    const emailInput = screen.getByLabelText(/^Email/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/^Mật khẩu/i) as HTMLInputElement;

    expect(emailInput.value).toBe("scholar@verischolar.ai");
    expect(passwordInput.value).toBe("VeriScholar2026!");
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
});
