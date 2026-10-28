import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardWorkspace } from "../DashboardWorkspace";

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Assistant Panel Header and Floating Bubble Unification", () => {
  it("does not render New Chat, Settings, Dark/light or Zen Chat in Assistant header", () => {
    renderWithClient(<DashboardWorkspace initialAssistantOpen={true} />);

    // Bỏ New Chat, Bỏ Setting, Bỏ Darklight, Bỏ Zen Chat, Bỏ chữ Assistant
    expect(screen.queryByTestId("new-chat-btn")).toBeNull();
    expect(screen.queryByText("New Chat")).toBeNull();
    expect(screen.queryByLabelText("Cài đặt phiên nghiên cứu")).toBeNull();
    expect(screen.queryByTestId("zen-chat-btn")).toBeNull();
    expect(screen.queryByTestId("workspace-tools-menu-btn")).toBeNull();
  });

  it("displays Socratic Assistant instead of Socratic Copilot", () => {
    renderWithClient(<DashboardWorkspace initialAssistantOpen={true} />);

    // Must display Socratic Assistant
    expect(screen.getAllByText(/Socratic Assistant/i).length).toBeGreaterThan(0);
    // Must NOT display Socratic Copilot
    expect(screen.queryByText(/Socratic Copilot/i)).toBeNull();
  });

  it("does not render top vertical edge dock and keeps only corner assistant FAB", () => {
    renderWithClient(<DashboardWorkspace initialAssistantOpen={false} />);

    // Top vertical edge dock must NOT be rendered
    expect(screen.queryByTestId("vertical-edge-dock")).toBeNull();
    expect(screen.queryByTestId("edge-dock-info-btn")).toBeNull();
    expect(screen.queryByTestId("edge-dock-notes-btn")).toBeNull();
    expect(screen.queryByTestId("edge-dock-assistant-btn")).toBeNull();

    // Corner FAB must exist when assistant is closed
    const cornerFab = screen.getByTestId("floating-assistant-fab");
    expect(cornerFab).toBeDefined();
    expect(cornerFab.className).toContain("fixed");
    expect(cornerFab.className).toContain("bottom-6");
    expect(cornerFab.className).toContain("right-6");
  });
});
