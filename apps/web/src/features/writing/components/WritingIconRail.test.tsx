import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { WritingIconRail } from "./WritingIconRail";

describe("WritingIconRail", () => {
  it("renders brand logo, toggle file tree button, and quick navigation links", () => {
    const handleToggle = vi.fn();
    const handleSettings = vi.fn();

    render(
      <BrowserRouter>
        <WritingIconRail
          isFileTreeOpen={true}
          onToggleFileTree={handleToggle}
          onOpenSettings={handleSettings}
        />
      </BrowserRouter>
    );

    // Brand logo
    const logoLink = screen.getByTestId("rail-logo-btn");
    expect(logoLink).toBeInTheDocument();
    expect(logoLink).toHaveAttribute("href", "/dashboard");

    // Toggle file tree button
    const toggleBtn = screen.getByTestId("toggle-file-tree-btn");
    expect(toggleBtn).toBeInTheDocument();
    fireEvent.click(toggleBtn);
    expect(handleToggle).toHaveBeenCalledTimes(1);

    // Quick navigation links
    expect(screen.getByTestId("rail-nav-chat")).toHaveAttribute("href", "/dashboard");
    expect(screen.getByTestId("rail-nav-project")).toHaveAttribute("href", "/dashboard");
    expect(screen.getByTestId("rail-nav-library")).toHaveAttribute("href", "/dashboard");

    // Settings button
    const settingsBtn = screen.getByTestId("rail-settings-btn");
    fireEvent.click(settingsBtn);
    expect(handleSettings).toHaveBeenCalledTimes(1);
  });
});
