import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import * as React from "react";
import {
  useSessionsQuery,
  useCreateSessionMutation,
  useUpdateSessionTitleMutation,
  useDeleteSessionMutation,
  DASHBOARD_QUERY_KEYS
} from "./useDashboardQueries";
import { dashboardApi } from "../api/dashboardApi";
import type { SessionItem, SessionDetail } from "@/types/dashboard";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe("Dashboard TanStack Query Hooks", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches recent sessions successfully", async () => {
    const mockSessions: SessionItem[] = [
      {
        id: "session-1",
        title: "Khảo sát Transformer",
        document_ids: ["doc-1"],
        created_at: "2026-01-01",
        updated_at: "2026-01-01",
        version: 1,
      },
    ];
    vi.spyOn(dashboardApi, "listSessions").mockResolvedValue(mockSessions);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useSessionsQuery(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.length).toBeGreaterThan(0);
    expect(result.current.data?.[0]?.title).toBeDefined();
  });

  it("creates a new session optimistically and returns session item", async () => {
    const createdSession: SessionDetail = {
      id: "session-new-123",
      title: "Khảo sát Transformer Mới",
      document_ids: [],
      created_at: "2026-01-01",
      updated_at: "2026-01-01",
      version: 1,
      viewport_state: { page: 1, zoom_ratio: 1.0, scroll_top: 0 },
      active_tab: "chat",
      is_archived: false,
    };
    vi.spyOn(dashboardApi, "createSession").mockResolvedValue(createdSession);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useCreateSessionMutation(), { wrapper });

    const newSession = await result.current.mutateAsync({
      title: "Khảo sát Transformer Mới",
    });

    expect(newSession.title).toBe("Khảo sát Transformer Mới");
    expect(newSession.id).toBe("session-new-123");
    expect(newSession.version).toBe(1);
  });

  it("updates session title with Optimistic Concurrency Control (OCC)", async () => {
    const updatedSession: SessionDetail = {
      id: "session-test-1",
      title: "Tiêu đề đã sửa đổi",
      document_ids: [],
      created_at: "2026-01-01",
      updated_at: "2026-01-01",
      version: 2,
      viewport_state: { page: 1, zoom_ratio: 1.0, scroll_top: 0 },
      active_tab: "chat",
      is_archived: false,
    };
    vi.spyOn(dashboardApi, "updateSessionTitle").mockResolvedValue(updatedSession);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useUpdateSessionTitleMutation(), { wrapper });

    const updated = await result.current.mutateAsync({
      id: "session-test-1",
      title: "Tiêu đề đã sửa đổi",
      version: 1,
    });

    expect(updated.title).toBe("Tiêu đề đã sửa đổi");
    expect(updated.version).toBe(2);
  });

  it("handles OCC concurrency conflict gracefully", async () => {
    vi.spyOn(dashboardApi, "updateSessionTitle").mockRejectedValue(
      new Error("412 Precondition Failed: CONCURRENCY_CONFLICT")
    );

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    const initialSessions: SessionItem[] = [
      {
        id: "session-occ",
        title: "Bản gốc",
        document_ids: [],
        created_at: "2026-01-01",
        updated_at: "2026-01-01",
        version: 1,
      },
    ];

    queryClient.setQueryData(DASHBOARD_QUERY_KEYS.allSessions, initialSessions);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(() => useUpdateSessionTitleMutation(), { wrapper });

    await expect(
      result.current.mutateAsync({
        id: "session-occ",
        title: "Tiêu đề gây xung đột",
        version: 1,
      })
    ).rejects.toThrow("CONCURRENCY_CONFLICT");

    // Verified rollback to initial state
    const cachedSessions = queryClient.getQueryData<SessionItem[]>(DASHBOARD_QUERY_KEYS.allSessions);
    expect(cachedSessions?.[0]?.title).toBe("Bản gốc");
  });

  it("deletes session optimistically", async () => {
    vi.spyOn(dashboardApi, "deleteSession").mockResolvedValue();

    const wrapper = createWrapper();
    const { result } = renderHook(() => useDeleteSessionMutation(), { wrapper });

    await expect(result.current.mutateAsync("session-to-delete")).resolves.toBeUndefined();
  });
});
