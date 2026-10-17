import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  sessionsApi,
  type ListSessionsParams,
  type ListSessionMessagesParams,
} from "../api/sessionsApi";
import type {
  SessionCreateRequest,
  SessionResponseData,
  SessionUpdateViewportRequest,
  SessionAddDocumentRequest,
} from "@/types/session";
import type { ApiResponseWithHeaders } from "@/lib/api-client";

export const SESSION_QUERY_KEYS = {
  all: ["sessions"] as const,
  lists: () => [...SESSION_QUERY_KEYS.all, "list"] as const,
  list: (params: ListSessionsParams = {}) => [...SESSION_QUERY_KEYS.lists(), params] as const,
  details: () => [...SESSION_QUERY_KEYS.all, "detail"] as const,
  detail: (id: string) => [...SESSION_QUERY_KEYS.details(), id] as const,
  messages: (id: string) => [...SESSION_QUERY_KEYS.detail(id), "messages"] as const,
  messagesList: (id: string, params: ListSessionMessagesParams = {}) =>
    [...SESSION_QUERY_KEYS.messages(id), params] as const,
};

export function useSessionsList(params: ListSessionsParams = {}) {
  return useQuery({
    queryKey: SESSION_QUERY_KEYS.list(params),
    queryFn: () => sessionsApi.listSessions(params),
    staleTime: 1000 * 60, // 1 min
  });
}

export function useSessionDetail(sessionId: string | null | undefined) {
  return useQuery({
    queryKey: SESSION_QUERY_KEYS.detail(sessionId ?? ""),
    queryFn: () => sessionsApi.getSessionDetail(sessionId!),
    enabled: Boolean(sessionId),
    staleTime: 1000 * 60 * 5, // 5 minutes fresh cache to prevent refresh waterfall
  });
}

export function useSessionMessages(
  sessionId: string | null | undefined,
  params: ListSessionMessagesParams = {}
) {
  return useQuery({
    queryKey: SESSION_QUERY_KEYS.messagesList(sessionId ?? "", params),
    queryFn: () => sessionsApi.listSessionMessages(sessionId!, params),
    enabled: Boolean(sessionId),
  });
}

export function useCreateSessionMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SessionCreateRequest) => sessionsApi.createSession(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.lists() });
    },
  });
}

export function useUpdateSessionMetadataMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      sessionId,
      title,
      etag,
    }: {
      sessionId: string;
      title: string;
      etag: string;
    }) => {
      try {
        return await sessionsApi.updateSessionMetadata(sessionId, title, etag);
      } catch (err: unknown) {
        if (
          typeof err === "object" &&
          err !== null &&
          "status" in err &&
          (err as { status: number }).status === 412
        ) {
          const fresh = await sessionsApi.getSessionDetail(sessionId);
          const freshEtag = fresh.headers?.get("etag") || fresh.headers?.get("ETag") || `v${fresh.data.version}`;
          return await sessionsApi.updateSessionMetadata(sessionId, title, freshEtag);
        }
        throw err;
      }
    },
    onMutate: async ({ sessionId, title }) => {
      await queryClient.cancelQueries({ queryKey: SESSION_QUERY_KEYS.detail(sessionId) });

      const previousSession = queryClient.getQueryData<ApiResponseWithHeaders<SessionResponseData>>(
        SESSION_QUERY_KEYS.detail(sessionId)
      );

      if (previousSession) {
        queryClient.setQueryData<ApiResponseWithHeaders<SessionResponseData>>(
          SESSION_QUERY_KEYS.detail(sessionId),
          {
            ...previousSession,
            data: {
              ...previousSession.data,
              title,
              version: previousSession.data.version + 1,
            },
          }
        );
      }

      return { previousSession };
    },
    onError: (_err, { sessionId }, context) => {
      if (context?.previousSession) {
        queryClient.setQueryData(SESSION_QUERY_KEYS.detail(sessionId), context.previousSession);
      }
    },
    onSettled: (_data, _err, { sessionId }) => {
      queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.detail(sessionId) });
      queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.lists() });
    },
  });
}

export function useUpdateSessionViewportMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      data,
      etag,
    }: {
      sessionId: string;
      data: SessionUpdateViewportRequest;
      etag: string;
    }) => sessionsApi.updateSessionViewport(sessionId, data, etag),
    onError: (err: unknown, { sessionId }) => {
      // If 412 Precondition Failed, quietly refresh session details to synchronize ETag
      const errorObj = err as { status?: number; response?: { status?: number } };
      if (errorObj?.status === 412 || errorObj?.response?.status === 412) {
        queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.detail(sessionId) });
      }
    },
    // Viewport persistence is background sync; do not invalidate query to avoid scroll re-fetch cascades
  });
}

export function useDeleteSessionMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => sessionsApi.deleteSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.lists() });
    },
  });
}

export function useAddSessionDocumentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sessionId,
      data,
    }: {
      sessionId: string;
      data: SessionAddDocumentRequest;
    }) => sessionsApi.addDocumentToSession(sessionId, data),
    onSuccess: (_data, { sessionId }) => {
      queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.detail(sessionId) });
    },
  });
}

export function useClearSessionMessagesMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => sessionsApi.clearSessionMessages(sessionId),
    onSuccess: (_data, sessionId) => {
      queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.messages(sessionId) });
    },
  });
}

export function useRestoreArchivedSessionMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ sessionId, file }: { sessionId: string; file: File }) =>
      sessionsApi.restoreArchivedSession(sessionId, file),
    onSuccess: (_data, { sessionId }) => {
      queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.detail(sessionId) });
      queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.lists() });
    },
  });
}

export function useExportSessionBundleMutation() {
  return useMutation({
    mutationFn: (sessionId: string) => sessionsApi.exportSessionBundle(sessionId),
  });
}
