import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { DashboardChatInputBox } from "../components/DashboardChatInputBox";

describe("DashboardChatInputBox Component", () => {
  it("renders pill input without hand icon, opens Reasoning Popover on Brain click, and selects 4-step effort", () => {
    const handleSend = vi.fn();
    const handleChangeText = vi.fn();

    render(
      <DashboardChatInputBox
        inputText="Explain attention mechanism"
        onChangeText={handleChangeText}
        onSend={handleSend}
      />
    );

    // Verify hand icon does NOT exist
    expect(screen.queryByTitle(/bàn tay/i)).not.toBeInTheDocument();
    expect(screen.queryByTestId("hand-tool-btn")).not.toBeInTheDocument();

    // Verify Brain toggle exists
    const brainBtn = screen.getByTestId("toggle-reasoning-btn");
    expect(brainBtn).toBeInTheDocument();

    // Click brain button to open Popover
    fireEvent.click(brainBtn);

    // Popover elements
    expect(screen.getByText(/5.6 Luna/i)).toBeInTheDocument();
    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("High");
    expect(screen.getByTestId("reasoning-slider")).toBeInTheDocument();

    // Select Medium effort
    const mediumStep = screen.getByTestId("reasoning-step-medium");
    fireEvent.click(mediumStep);
    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("Medium");

    // Click Reset button to return to High
    const resetBtn = screen.getByTestId("reasoning-reset-btn");
    fireEvent.click(resetBtn);
    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("High");
  });
});
