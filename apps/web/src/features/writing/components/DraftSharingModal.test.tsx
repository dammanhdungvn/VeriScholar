import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { DraftSharingModal } from "./DraftSharingModal";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import type { DraftShareResponse } from "../types";

vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    getShareSettings: vi.fn(),
    shareDraft: vi.fn(),
  },
}));

describe("DraftSharingModal", () => {
  const mockShareSettings: DraftShareResponse = {
    draft_id: "draft-200",
    share_token: "tok_abc123",
    share_url: "http://localhost:5173/drafts/share/tok_abc123",
    permission: "editor",
    allow_public_link: false,
    collaborators: [
      {
        user_id: "u-1",
        email: "coauthor@mit.edu",
        permission: "editor",
        granted_at: "2026-10-15T07:00:00Z",
      },
      {
        user_id: "u-2",
        email: "reviewer@stanford.edu",
        permission: "viewer",
        granted_at: "2026-10-15T07:30:00Z",
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    useWritingStore.getState().reset();
    useWritingStore.getState().setDraft({
      id: "draft-200",
      user_id: "user-1",
      title: "Draft 200",
      content: "Content",
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });
    vi.mocked(draftsApi.getShareSettings).mockResolvedValue(mockShareSettings);
  });

  it("does not render when isOpen is false", () => {
    render(<DraftSharingModal isOpen={false} />);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("renders modal, displays strict permission warning, and lists collaborators", async () => {
    render(<DraftSharingModal isOpen={true} draftId="draft-200" />);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(
      screen.getByText(/Chia Sẻ Bản Thảo & Phân Quyền Cộng Tác/i)
    ).toBeInTheDocument();

    // Check Strict Permission Warning
    expect(
      screen.getByTestId("permission-strict-warning")
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Cảnh Báo Phân Quyền Nghiêm Ngặt/i)
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(draftsApi.getShareSettings).toHaveBeenCalledWith("draft-200");
    });

    // Check Collaborators
    expect(screen.getByText("coauthor@mit.edu")).toBeInTheDocument();
    expect(screen.getByText("reviewer@stanford.edu")).toBeInTheDocument();
    expect(screen.getByText("EDITOR")).toBeInTheDocument();
    expect(screen.getByText("VIEWER")).toBeInTheDocument();
  });

  it("invites a new collaborator with chosen role", async () => {
    const updatedSettings: DraftShareResponse = {
      ...mockShareSettings,
      collaborators: [
        ...mockShareSettings.collaborators,
        {
          user_id: "u-3",
          email: "newmember@harvard.edu",
          permission: "commenter",
          granted_at: "2026-10-15T08:00:00Z",
        },
      ],
    };

    vi.mocked(draftsApi.shareDraft).mockResolvedValue(updatedSettings);

    render(<DraftSharingModal isOpen={true} draftId="draft-200" />);

    await waitFor(() => {
      expect(draftsApi.getShareSettings).toHaveBeenCalled();
    });

    const emailInput = screen.getByTestId("invite-email-input");
    const roleSelect = screen.getByTestId("invite-role-select");
    const sendBtn = screen.getByTestId("send-invite-btn");

    fireEvent.change(emailInput, { target: { value: "newmember@harvard.edu" } });
    fireEvent.change(roleSelect, { target: { value: "commenter" } });
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(draftsApi.shareDraft).toHaveBeenCalledWith(
        "draft-200",
        expect.objectContaining({
          target_email: "newmember@harvard.edu",
          permission: "commenter",
        })
      );
    });

    expect(screen.getByText("newmember@harvard.edu")).toBeInTheDocument();
    expect(screen.getByText("COMMENTER")).toBeInTheDocument();
  });

  it("toggles public sharing link and allows copying link", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
      },
    });

    const publicSettings: DraftShareResponse = {
      ...mockShareSettings,
      allow_public_link: true,
      share_url: "http://localhost:5173/drafts/share/tok_abc123",
    };

    vi.mocked(draftsApi.shareDraft).mockResolvedValue(publicSettings);

    render(<DraftSharingModal isOpen={true} draftId="draft-200" />);

    await waitFor(() => {
      expect(draftsApi.getShareSettings).toHaveBeenCalled();
    });

    const toggle = screen.getByTestId("public-link-toggle");
    fireEvent.click(toggle);

    await waitFor(() => {
      expect(draftsApi.shareDraft).toHaveBeenCalledWith("draft-200", {
        allow_public_link: true,
        permission: "viewer",
      });
    });

    const copyBtn = screen.getByTestId("copy-link-btn");
    fireEvent.click(copyBtn);

    expect(writeTextMock).toHaveBeenCalledWith(
      "http://localhost:5173/drafts/share/tok_abc123"
    );
    expect(screen.getByText("Đã sao chép")).toBeInTheDocument();
  });
});
