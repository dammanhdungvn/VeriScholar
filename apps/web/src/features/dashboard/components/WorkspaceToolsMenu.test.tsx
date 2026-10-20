import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { WorkspaceToolsMenu } from "./WorkspaceToolsMenu";

describe("WorkspaceToolsMenu Component", () => {
  it("renders closed by default", () => {
    render(
      <WorkspaceToolsMenu
        onExport={vi.fn()}
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
    const onExport = vi.fn();
    const onOpenSettings = vi.fn();
    const onToggleTheme = vi.fn();

    render(
      <WorkspaceToolsMenu
        onExport={onExport}
        onOpenSettings={onOpenSettings}
        isDark={false}
        onToggleTheme={onToggleTheme}
      />
    );

    const triggerBtn = screen.getByTestId("workspace-tools-menu-btn");
    fireEvent.click(triggerBtn);

    const popover = screen.getByTestId("workspace-tools-popover");
    expect(popover).toBeInTheDocument();

    // Export ZIP
    const exportBtn = screen.getByRole("menuitem", { name: /Xuất ZIP/i });
    fireEvent.click(exportBtn);
    expect(onExport).toHaveBeenCalledTimes(1);
    expect(screen.queryByTestId("workspace-tools-popover")).not.toBeInTheDocument();

    // Reopen and test Settings
    fireEvent.click(triggerBtn);
    const settingsBtn = screen.getByRole("menuitem", { name: /Cài đặt/i });
    fireEvent.click(settingsBtn);
    expect(onOpenSettings).toHaveBeenCalledTimes(1);

    // Reopen and test Theme toggle
    fireEvent.click(triggerBtn);
    const themeBtn = screen.getByRole("menuitem", { name: /Giao diện tối/i });
    fireEvent.click(themeBtn);
    expect(onToggleTheme).toHaveBeenCalledTimes(1);
  });

  it("closes popover when Escape is pressed", () => {
    render(
      <WorkspaceToolsMenu
        onExport={vi.fn()}
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
