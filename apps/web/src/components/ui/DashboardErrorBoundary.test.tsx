import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import * as React from "react";
import { DashboardErrorBoundary } from "./DashboardErrorBoundary";

import { ApiError } from "@/lib/api-client";

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

  it("renders error tracking code when ApiError with requestId is caught and handles copy", () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
      },
    });

    function ApiErrorThrower(): React.ReactNode {
      throw new ApiError(
        "Máy chủ gián đoạn dịch vụ",
        "SERVICE_UNAVAILABLE",
        null,
        null,
        503,
        "trace-req-abc-123"
      );
    }

    render(
      <DashboardErrorBoundary>
        <ApiErrorThrower />
      </DashboardErrorBoundary>
    );

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("Máy chủ gián đoạn dịch vụ")).toBeInTheDocument();
    expect(screen.getByText(/Mã tra cứu:/i)).toBeInTheDocument();
    expect(screen.getByText("REQ-TRACE-RE")).toBeInTheDocument();

    const copyBtn = screen.getByTitle(/Sao chép mã lỗi để gửi kỹ thuật viên/i);
    fireEvent.click(copyBtn);
    expect(writeTextMock).toHaveBeenCalledWith("trace-req-abc-123");
  });
});
