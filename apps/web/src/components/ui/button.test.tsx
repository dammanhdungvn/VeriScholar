import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "./button";

describe("Button component", () => {
  it("renders with default primary variant and text", () => {
    render(<Button>Bắt đầu ngay</Button>);
    const button = screen.getByRole("button", { name: /Bắt đầu ngay/i });
    expect(button).toBeInTheDocument();
    expect(button.className).toContain("bg-primary");
  });

  it("renders secondary variant correctly", () => {
    render(<Button variant="secondary">Tải PDF</Button>);
    const button = screen.getByRole("button", { name: /Tải PDF/i });
    expect(button.className).toContain("bg-canvas");
    expect(button.className).toContain("border-hairline");
  });

  it("fires onClick handler when clicked", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Nhấp vào đây</Button>);
    const button = screen.getByRole("button", { name: /Nhấp vào đây/i });

    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("does not fire onClick when disabled", () => {
    const handleClick = vi.fn();
    render(
      <Button disabled onClick={handleClick}>
        Vô hiệu hóa
      </Button>
    );
    const button = screen.getByRole("button", { name: /Vô hiệu hóa/i });

    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
    expect(button).toBeDisabled();
  });
});
