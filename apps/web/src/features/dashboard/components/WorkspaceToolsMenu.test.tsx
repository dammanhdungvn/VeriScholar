import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { WorkspaceToolsMenu } from "./WorkspaceToolsMenu";

describe("WorkspaceToolsMenu Component", () => {
  it("renders closed by default", () => {
    render(
      <WorkspaceToolsMenu
        onOpenSettings={vi.fn()}
        isDark={false}
        onToggleTheme={vi.fn()}
      />
    );

    const triggerBtn = screen.getByTestId("workspace-tools-menu-btn");
    expect(triggerBtn).toBeInTheDocument();
    expect(screen.queryByTestId("workspace-tools-popover")).not.toBeInTheDocument();
  });

  it("opens popover menu and triggers actions", () => {
    const onOpenSettings = vi.fn();
    const onToggleTheme = vi.fn();

    render(
      <WorkspaceToolsMenu
        onOpenSettings={onOpenSettings}
        isDark={false}
        onToggleTheme={onToggleTheme}
      />
    );

    const triggerBtn = screen.getByTestId("workspace-tools-menu-btn");
    fireEvent.click(triggerBtn);

    const popover = screen.getByTestId("workspace-tools-popover");
    expect(popover).toBeInTheDocument();

    // Test Settings
    const settingsBtn = screen.getByRole("menuitem", { name: /Cài đặt/i });
    fireEvent.click(settingsBtn);
    expect(onOpenSettings).toHaveBeenCalledTimes(1);
    expect(screen.queryByTestId("workspace-tools-popover")).not.toBeInTheDocument();

    // Reopen and test Theme toggle
    fireEvent.click(triggerBtn);
    const themeBtn = screen.getByRole("menuitem", { name: /Giao diện tối/i });
    fireEvent.click(themeBtn);
    expect(onToggleTheme).toHaveBeenCalledTimes(1);
  });

  it("closes popover when Escape is pressed", () => {
    render(
      <WorkspaceToolsMenu
        onOpenSettings={vi.fn()}
        isDark={true}
        onToggleTheme={vi.fn()}
      />
    );

    const triggerBtn = screen.getByTestId("workspace-tools-menu-btn");
    fireEvent.click(triggerBtn);
    expect(screen.getByTestId("workspace-tools-popover")).toBeInTheDocument();

    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByTestId("workspace-tools-popover")).not.toBeInTheDocument();
  });
});
