import { useCallback } from "react";
import type { SessionItem } from "@/types/dashboard";
import { useDashboardStore } from "../stores/useDashboardStore";
import {
  useSessionsQuery,
  useCreateSessionMutation,
  useDeleteSessionMutation,
  useUpdateSessionTitleMutation
} from "./useDashboardQueries";

export function useDashboardSessions() {
  const { data: sessions = [], isLoading, error } = useSessionsQuery(1, 50, undefined, true);
  const createMutation = useCreateSessionMutation();
  const deleteMutation = useDeleteSessionMutation();
  const updateTitleMutation = useUpdateSessionTitleMutation();

  const activeSessionId = useDashboardStore((s) => s.activeSessionId);
  const setActiveSessionId = useDashboardStore((s) => s.setActiveSessionId);

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  const createSession = useCallback(
    async (title: string = "Phiên nghiên cứu mới"): Promise<SessionItem> => {
      try {
        const created = await createMutation.mutateAsync({ title });
        setActiveSessionId(created.id);
        return created;
      } catch {
        // Fallback local session if mutation fails
        const fallbackSession: SessionItem = {
          id: `session-${Date.now()}`,
          title,
          document_ids: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          version: 1,
        };
        setActiveSessionId(fallbackSession.id);
        return fallbackSession;
      }
    },
    [createMutation, setActiveSessionId]
  );

  const deleteSession = useCallback(
    async (sessionId: string) => {
      try {
        await deleteMutation.mutateAsync(sessionId);
      } catch (err) {
        console.warn(`Failed to delete session ${sessionId}:`, err);
      } finally {
        if (activeSessionId === sessionId) {
          setActiveSessionId(undefined);
        }
      }
    },
    [activeSessionId, deleteMutation, setActiveSessionId]
  );

  const updateTitle = useCallback(
    async (sessionId: string, title: string, version = 1) => {
      await updateTitleMutation.mutateAsync({ id: sessionId, title, version });
    },
    [updateTitleMutation]
  );

  const selectSession = useCallback(
    (sessionId: string) => {
      setActiveSessionId(sessionId);
    },
    [setActiveSessionId]
  );

  return {
    sessions,
    activeSession,
    activeSessionId,
    isLoading,
    error,
    createSession,
    deleteSession,
    updateTitle,
    selectSession,
  };
}
