import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ReasoningPopover } from "../components/ReasoningPopover";
import { useDashboardStore } from "../stores/useDashboardStore";

describe("ReasoningPopover Component", () => {
  beforeEach(() => {
    useDashboardStore.setState({
      reasoningEffort: "light",
      isReasoningEnabled: false,
      selectedModel: "5.6 Luna",
    });
  });

  it("renders 4 levels: Light, Medium, High, Extra High and defaults to Light", () => {
    render(<ReasoningPopover isOpen={true} onClose={vi.fn()} />);

    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("Light");
    expect(screen.getByTestId("reasoning-step-light")).toBeInTheDocument();
    expect(screen.getByTestId("reasoning-step-medium")).toBeInTheDocument();
    expect(screen.getByTestId("reasoning-step-high")).toBeInTheDocument();
    expect(screen.getByTestId("reasoning-step-extra_high")).toBeInTheDocument();
  });

  it("changes level when clicking a specific step", () => {
    render(<ReasoningPopover isOpen={true} onClose={vi.fn()} />);

    fireEvent.click(screen.getByTestId("reasoning-step-high"));
    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("High");
    expect(useDashboardStore.getState().reasoningEffort).toBe("high");
  });

  it("resets back to Light when clicking reset button", () => {
    useDashboardStore.setState({ reasoningEffort: "extra_high" });
    render(<ReasoningPopover isOpen={true} onClose={vi.fn()} />);

    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("Extra High");
    fireEvent.click(screen.getByTestId("reasoning-reset-btn"));

    expect(screen.getByTestId("reasoning-effort-label")).toHaveTextContent("Light");
    expect(useDashboardStore.getState().reasoningEffort).toBe("light");
  });

  it("updates level when dragging the slider horizontally", () => {
    render(<ReasoningPopover isOpen={true} onClose={vi.fn()} />);

    const slider = screen.getByTestId("reasoning-slider");

    // Mock getBoundingClientRect
    vi.spyOn(slider, "getBoundingClientRect").mockReturnValue({
      left: 0,
      width: 300,
      top: 0,
      bottom: 20,
      right: 300,
      height: 20,
      x: 0,
      y: 0,
      toJSON: () => {},
    });

    // Mock setPointerCapture and releasePointerCapture
    slider.setPointerCapture = vi.fn();
    slider.releasePointerCapture = vi.fn();

    // Drag to 66% (High) - 200 / 300 = 0.666 -> step index 2 (High)
    fireEvent.mouseDown(slider, { clientX: 200 });
    expect(useDashboardStore.getState().reasoningEffort).toBe("high");

    // Drag to 100% (Extra High)
    fireEvent.mouseMove(slider, { clientX: 300 });
    expect(useDashboardStore.getState().reasoningEffort).toBe("extra_high");

    // Drag left to 0% (Light)
    fireEvent.mouseMove(slider, { clientX: 0 });
    expect(useDashboardStore.getState().reasoningEffort).toBe("light");

    fireEvent.mouseUp(slider);
  });
});
