import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import * as React from "react";
import { DashboardErrorBoundary } from "./DashboardErrorBoundary";

function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error("Lỗi giả lập trong component con");
  }
  return <div>Nội dung bình thường</div>;
}

function TestHarness() {
  const [hasError, setHasError] = React.useState(true);
  return (
    <DashboardErrorBoundary onReset={() => setHasError(false)}>
      <ThrowingComponent shouldThrow={hasError} />
    </DashboardErrorBoundary>
  );
}

describe("DashboardErrorBoundary component", () => {
  const originalConsoleError = console.error;

  beforeEach(() => {
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  it("renders children when no error thrown", () => {
    render(
      <DashboardErrorBoundary>
        <div>Nội dung bình thường</div>
      </DashboardErrorBoundary>
    );

    expect(screen.getByText("Nội dung bình thường")).toBeInTheDocument();
  });

  it("renders fallback UI and allows retry when error thrown", () => {
    render(<TestHarness />);

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("Đã xảy ra lỗi không gian làm việc")).toBeInTheDocument();
    expect(screen.getByText("Lỗi giả lập trong component con")).toBeInTheDocument();

    const retryBtn = screen.getByRole("button", { name: /thử lại/i });
    fireEvent.click(retryBtn);

    expect(screen.getByText("Nội dung bình thường")).toBeInTheDocument();
  });
});
