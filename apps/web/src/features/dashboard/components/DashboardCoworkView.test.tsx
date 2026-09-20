import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DashboardCoworkView } from "./DashboardCoworkView";

describe("DashboardCoworkView component", () => {
  beforeEach(() => {
    // Mock navigator.clipboard
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined)
      }
    });
  });

  it("renders Work Intake header, execution steps, and artifact", () => {
    render(<DashboardCoworkView />);

    expect(screen.getByText("Kế Hoạch Thực Thi")).toBeInTheDocument();
    expect(screen.getByText(/Thu thập số liệu từ Table 1/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Bảng Đối Chiếu: Self-Attention vs Recurrence/i).length).toBeGreaterThanOrEqual(1);
  });

  it("approves waiting task when clicking Phê duyệt button", () => {
    render(<DashboardCoworkView />);

    const approveBtn = screen.getByRole("button", { name: /phê duyệt/i });
    expect(approveBtn).toBeInTheDocument();

    fireEvent.click(approveBtn);

    // Approval gate disappears after being approved
    expect(screen.queryByRole("button", { name: /phê duyệt/i })).not.toBeInTheDocument();
  });

  it("copies artifact content when clicking Sao chép button", () => {
    render(<DashboardCoworkView />);

    const copyBtn = screen.getByTitle("Sao chép nội dung");
    fireEvent.click(copyBtn);

    expect(navigator.clipboard.writeText).toHaveBeenCalled();
  });
});
