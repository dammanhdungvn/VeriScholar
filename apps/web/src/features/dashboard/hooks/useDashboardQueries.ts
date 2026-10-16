import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { dashboardApi } from "../api/dashboardApi";
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

/**
 * Hook to query sessions with TanStack Query
 */
export function useSessionsQuery(
  page = 1,
  perPage = 20,
  q?: string,
  includeArchived = false
) {
  return useQuery<SessionItem[]>({
    queryKey: [...DASHBOARD_QUERY_KEYS.allSessions, page, perPage, q, includeArchived],
    queryFn: () => dashboardApi.listSessions(page, perPage, q, includeArchived),
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
      return dashboardApi.getSession(sessionId);
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
    mutationFn: (req: CreateSessionRequest) => dashboardApi.createSession(req),
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
    mutationFn: ({ id, title, version }) => {
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
    mutationFn: (sessionId: string) => dashboardApi.deleteSession(sessionId),
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
    mutationFn: ({ sessionId, request }) => dashboardApi.addDocument(sessionId, request),
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
