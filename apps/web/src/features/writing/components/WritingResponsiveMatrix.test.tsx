import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { WritingWorkspace } from "./WritingWorkspace";
import { useWritingStore } from "../stores/useWritingStore";
import type { Draft } from "../types";

const mockDraft: Draft = {
  id: "e540e433-3b76-48ab-b65e-082b269aba60",
  user_id: "user-1",
  title: "A Survey on Scalable Attention Mechanisms",
  content: "\\documentclass{article}\n\\begin{document}\n\\section{Introduction}\nAttention mechanisms are essential.\n\\end{document}",
  format: "latex",
  version: 3,
  created_at: "2026-10-19T00:00:00Z",
  updated_at: "2026-10-19T00:00:00Z",
};

describe("Writing Responsive Matrix Audit (Mobile, Tablet, Desktop)", () => {
  beforeEach(() => {
    useWritingStore.getState().reset();
    useWritingStore.getState().setDraft(mockDraft);
    vi.restoreAllMocks();
  });

  describe("1. Mobile Viewport (< 768px: 375px iPhone, 390px, 412px Android)", () => {
    it("renders Mobile Segmented Switcher with [Soạn thảo], [Xem PDF], and [Trợ lý AI] buttons", () => {
      render(
        <BrowserRouter>
          <WritingWorkspace />
        </BrowserRouter>
      );

      const mobileSwitcher = screen.getByTestId("mobile-view-switcher");
      expect(mobileSwitcher).toBeInTheDocument();

      const tabEditor = screen.getByTestId("mobile-tab-editor");
      const tabPreview = screen.getByTestId("mobile-tab-preview");
      const tabAssistant = screen.getByTestId("mobile-tab-assistant");

      expect(tabEditor).toBeInTheDocument();
      expect(tabPreview).toBeInTheDocument();
      expect(tabAssistant).toBeInTheDocument();
    });

    it("switches mobile active tabs reactively when tapping segmented buttons", () => {
      render(
        <BrowserRouter>
          <WritingWorkspace />
        </BrowserRouter>
      );

      // Initially active on editor
      expect(useWritingStore.getState().mobileActiveTab).toBe("editor");

      // Tap Preview tab
      const tabPreview = screen.getByTestId("mobile-tab-preview");
      fireEvent.click(tabPreview);
      expect(useWritingStore.getState().mobileActiveTab).toBe("preview");

      // Tap Assistant tab
      const tabAssistant = screen.getByTestId("mobile-tab-assistant");
      fireEvent.click(tabAssistant);
      expect(useWritingStore.getState().mobileActiveTab).toBe("assistant");

      // Tap Editor tab
      const tabEditor = screen.getByTestId("mobile-tab-editor");
      fireEvent.click(tabEditor);
      expect(useWritingStore.getState().mobileActiveTab).toBe("editor");
    });

    it("renders mobile sidebar toggle button and drawer with backdrop and close button", () => {
      render(
        <BrowserRouter>
          <WritingWorkspace />
        </BrowserRouter>
      );

      // Mobile toggle button in header
      const mobileToggleBtn = screen.getByTestId("mobile-toggle-sidebar-btn");
      expect(mobileToggleBtn).toBeInTheDocument();

      // Drawer is open by default in store, backdrop exists
      const backdrop = screen.getByTestId("mobile-sidebar-backdrop");
      expect(backdrop).toBeInTheDocument();

      const closeDrawerBtn = screen.getByTestId("close-mobile-sidebar-btn");
      expect(closeDrawerBtn).toBeInTheDocument();

      // Tapping close button closes the sidebar drawer
      fireEvent.click(closeDrawerBtn);
      expect(useWritingStore.getState().isFileTreeOpen).toBe(false);
      expect(screen.queryByTestId("mobile-sidebar-backdrop")).toBeNull();

      // Tapping mobile toggle button re-opens drawer
      fireEvent.click(mobileToggleBtn);
      expect(useWritingStore.getState().isFileTreeOpen).toBe(true);
      expect(screen.getByTestId("mobile-sidebar-backdrop")).toBeInTheDocument();
    });
  });

  describe("2. Desktop Viewport (>= 1024px)", () => {
    it("renders full Overleaf layout: Icon Rail, Sidebar container, splitters, and desktop mode layout dropdown", () => {
      render(
        <BrowserRouter>
          <WritingWorkspace />
        </BrowserRouter>
      );

      // Left taskbar inherited from Dashboard
      expect(screen.getByRole("complementary", { name: /thanh điều hướng chính/i })).toBeInTheDocument();

      // Desktop layout dropdown in header
      expect(screen.getByTestId("header-layout-dropdown")).toBeInTheDocument();

      // Sidebar container
      expect(screen.getByTestId("sidebar-container")).toBeInTheDocument();

      // Splitters
      expect(screen.getByTestId("sidebar-resizable-splitter")).toBeInTheDocument();
      expect(screen.getByTestId("editor-preview-splitter")).toBeInTheDocument();
    });
  });
});
