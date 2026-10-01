import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { dashboardApi } from "../api/dashboardApi";
import { RECENT_SESSIONS } from "../data/mockDashboardData";
import type {
  SessionItem,
  SessionDetail,
  CreateSessionRequest,
  UpdateSessionTitleRequest,
  AddDocumentToSessionRequest,
  AddDocumentToSessionResponse
} from "@/types/dashboard";

export const DASHBOARD_QUERY_KEYS = {
  allSessions: ["dashboard", "sessions"] as const,
  sessionDetail: (id: string) => ["dashboard", "session", id] as const,
  sessionMessages: (id: string) => ["dashboard", "messages", id] as const,
};

const isMockEnabled = import.meta.env.VITE_ENABLE_MOCK_DASHBOARD === "true";

/**
 * Hook to query sessions with TanStack Query and fallback mock support
 */
export function useSessionsQuery(
  page = 1,
  perPage = 20,
  q?: string,
  includeArchived = false
) {
  return useQuery<SessionItem[]>({
    queryKey: [...DASHBOARD_QUERY_KEYS.allSessions, page, perPage, q, includeArchived],
    queryFn: async () => {
      if (isMockEnabled) {
        return RECENT_SESSIONS;
      }
      try {
        return await dashboardApi.listSessions(page, perPage, q, includeArchived);
      } catch (err) {
        if (isMockEnabled) {
          console.warn("Falling back to local sessions:", err);
          return RECENT_SESSIONS;
        }
        throw err;
      }
    },
    initialData: isMockEnabled ? RECENT_SESSIONS : undefined,
    staleTime: 30 * 1000,
  });
}

/**
 * Hook to fetch single session detail
 */
export function useSessionDetailQuery(sessionId?: string) {
  return useQuery<SessionDetail | null>({
    queryKey: sessionId ? DASHBOARD_QUERY_KEYS.sessionDetail(sessionId) : ["dashboard", "session", "none"],
    queryFn: async () => {
      if (!sessionId) return null;
      if (isMockEnabled) {
        const mock = RECENT_SESSIONS.find((s) => s.id === sessionId);
        if (!mock) return null;
        return {
          ...mock,
          active_document_id: mock.document_ids[0] ?? null,
          viewport_state: { page: 1, zoom_ratio: 1.0, scroll_top: 0 },
          active_tab: "chat",
          is_archived: false,
        };
      }
      try {
        return await dashboardApi.getSession(sessionId);
      } catch (err) {
        console.warn(`Failed to fetch session ${sessionId}:`, err);
        const mock = RECENT_SESSIONS.find((s) => s.id === sessionId);
        if (mock) {
          return {
            ...mock,
            active_document_id: mock.document_ids[0] ?? null,
            viewport_state: { page: 1, zoom_ratio: 1.0, scroll_top: 0 },
            active_tab: "chat",
            is_archived: false,
          };
        }
        throw err;
      }
    },
    enabled: Boolean(sessionId),
  });
}

/**
 * Hook to create a session with Optimistic Updates & Rollback
 */
export function useCreateSessionMutation() {
  const queryClient = useQueryClient();

  return useMutation<
    SessionDetail,
    Error,
    CreateSessionRequest,
    { previousSessions?: SessionItem[] }
  >({
    mutationFn: async (req: CreateSessionRequest) => {
      if (isMockEnabled) {
        const id = `session-${Date.now()}`;
        const newSession: SessionDetail = {
          id,
          title: req.title || "Phiên nghiên cứu mới",
          document_ids: req.initial_document_ids || [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          version: 1,
          viewport_state: { page: 1, zoom_ratio: 1.0, scroll_top: 0 },
          active_tab: "chat",
          is_archived: false,
        };
        return newSession;
      }
      return dashboardApi.createSession(req);
    },
    onMutate: async (newSessionReq) => {
      await queryClient.cancelQueries({ queryKey: DASHBOARD_QUERY_KEYS.allSessions });
      const previousSessions = queryClient.getQueryData<SessionItem[]>(
        DASHBOARD_QUERY_KEYS.allSessions
      );

      const optimisticSession: SessionItem = {
        id: `optimistic-${Date.now()}`,
        title: newSessionReq.title || "Phiên nghiên cứu mới",
        document_ids: newSessionReq.initial_document_ids || [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        version: 1,
      };

      queryClient.setQueryData<SessionItem[]>(
        DASHBOARD_QUERY_KEYS.allSessions,
        (old) => (old ? [optimisticSession, ...old] : [optimisticSession])
      );

      return { previousSessions };
    },
    onError: (_err, _variables, context) => {
      if (context?.previousSessions) {
        queryClient.setQueryData(
          DASHBOARD_QUERY_KEYS.allSessions,
          context.previousSessions
        );
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEYS.allSessions });
    },
  });
}

/**
 * Hook to update session title with Optimistic Concurrency Control (OCC)
 */
export function useUpdateSessionTitleMutation() {
  const queryClient = useQueryClient();

  return useMutation<
    SessionDetail,
    Error,
    { id: string; title: string; version: number },
    { previousSessions?: SessionItem[] }
  >({
    mutationFn: async ({ id, title, version }) => {
      if (isMockEnabled) {
        const updated: SessionDetail = {
          id,
          title,
          document_ids: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          version: version + 1,
          viewport_state: { page: 1, zoom_ratio: 1.0, scroll_top: 0 },
          active_tab: "chat",
          is_archived: false,
        };
        return updated;
      }
      const req: UpdateSessionTitleRequest = { title };
      return dashboardApi.updateSessionTitle(id, req, version);
    },
    onMutate: async ({ id, title }) => {
      await queryClient.cancelQueries({ queryKey: DASHBOARD_QUERY_KEYS.allSessions });
      const previousSessions = queryClient.getQueryData<SessionItem[]>(
        DASHBOARD_QUERY_KEYS.allSessions
      );

      queryClient.setQueryData<SessionItem[]>(
        DASHBOARD_QUERY_KEYS.allSessions,
        (old) =>
          old?.map((session) =>
            session.id === id ? { ...session, title } : session
          ) || []
      );

      return { previousSessions };
    },
    onError: (err, _variables, context) => {
      // If OCC conflict (412 Precondition Failed), re-fetch latest session state
      if (err.message.includes("412") || (err as { code?: string }).code === "CONCURRENCY_CONFLICT") {
        console.warn("Optimistic Concurrency Conflict: Fetching latest state.");
      }
      if (context?.previousSessions) {
        queryClient.setQueryData(
          DASHBOARD_QUERY_KEYS.allSessions,
          context.previousSessions
        );
      }
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEYS.allSessions });
      if (variables?.id) {
        queryClient.invalidateQueries({
          queryKey: DASHBOARD_QUERY_KEYS.sessionDetail(variables.id),
        });
      }
    },
  });
}

/**
 * Hook to delete session with optimistic removal
 */
export function useDeleteSessionMutation() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string, { previousSessions?: SessionItem[] }>({
    mutationFn: async (sessionId: string) => {
      if (isMockEnabled) return;
      return dashboardApi.deleteSession(sessionId);
    },
    onMutate: async (sessionId) => {
      await queryClient.cancelQueries({ queryKey: DASHBOARD_QUERY_KEYS.allSessions });
      const previousSessions = queryClient.getQueryData<SessionItem[]>(
        DASHBOARD_QUERY_KEYS.allSessions
      );

      queryClient.setQueryData<SessionItem[]>(
        DASHBOARD_QUERY_KEYS.allSessions,
        (old) => old?.filter((s) => s.id !== sessionId) || []
      );

      return { previousSessions };
    },
    onError: (_err, _variables, context) => {
      if (context?.previousSessions) {
        queryClient.setQueryData(
          DASHBOARD_QUERY_KEYS.allSessions,
          context.previousSessions
        );
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEYS.allSessions });
    },
  });
}

/**
 * Hook to add document to session
 */
export function useAddDocumentMutation() {
  const queryClient = useQueryClient();

  return useMutation<
    AddDocumentToSessionResponse,
    Error,
    { sessionId: string; request: AddDocumentToSessionRequest }
  >({
    mutationFn: async ({ sessionId, request }) => {
      if (isMockEnabled) {
        return {
          session_id: sessionId,
          document_id: request.document_id || "mock-doc-id",
          status: "associated",
          display_order: 1,
          message: "Tài liệu đã được thêm thành công.",
        };
      }
      return dashboardApi.addDocument(sessionId, request);
    },
    onSettled: (_data, _error, variables) => {
      if (variables?.sessionId) {
        queryClient.invalidateQueries({
          queryKey: DASHBOARD_QUERY_KEYS.sessionDetail(variables.sessionId),
        });
        queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEYS.allSessions });
      }
    },
  });
}
