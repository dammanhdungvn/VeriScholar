import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notesApi, type ListNotesParams } from "../api/notesApi";
import type {
  CreateNoteRequest,
  UpdateNoteRequest,
  NoteResponse,
  SynthesizeNotesRequest,
} from "@/types/note";
import type { ApiResponseWithHeaders } from "@/lib/api-client";

export const NOTE_QUERY_KEYS = {
  all: ["notes"] as const,
  lists: () => [...NOTE_QUERY_KEYS.all, "list"] as const,
  list: (params: ListNotesParams = {}) => [...NOTE_QUERY_KEYS.lists(), params] as const,
  details: () => [...NOTE_QUERY_KEYS.all, "detail"] as const,
  detail: (id: string) => [...NOTE_QUERY_KEYS.details(), id] as const,
};

export function useNotesList(params: ListNotesParams = {}) {
  return useQuery({
    queryKey: NOTE_QUERY_KEYS.list(params),
    queryFn: () => notesApi.listNotes(params),
    staleTime: 1000 * 30, // 30s
  });
}

export function useNoteDetail(noteId: string | null | undefined) {
  return useQuery({
    queryKey: NOTE_QUERY_KEYS.detail(noteId ?? ""),
    queryFn: () => notesApi.getNoteDetail(noteId!),
    enabled: Boolean(noteId),
  });
}

export function useCreateNoteMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateNoteRequest) => notesApi.createNote(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTE_QUERY_KEYS.lists() });
    },
  });
}

export function useUpdateNoteMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      noteId,
      data,
      etag,
    }: {
      noteId: string;
      data: UpdateNoteRequest;
      etag: string;
    }) => notesApi.updateNote(noteId, data, etag),
    onMutate: async ({ noteId, data }) => {
      // Cancel queries
      await queryClient.cancelQueries({ queryKey: NOTE_QUERY_KEYS.detail(noteId) });

      // Snapshot previous value for rollback
      const previousNote = queryClient.getQueryData<ApiResponseWithHeaders<NoteResponse>>(
        NOTE_QUERY_KEYS.detail(noteId)
      );

      // Optimistically update
      if (previousNote) {
        queryClient.setQueryData<ApiResponseWithHeaders<NoteResponse>>(
          NOTE_QUERY_KEYS.detail(noteId),
          {
            ...previousNote,
            data: {
              ...previousNote.data,
              user_note: data.user_note !== undefined ? data.user_note : previousNote.data.user_note,
              tags: data.tags !== undefined && data.tags !== null ? data.tags : previousNote.data.tags,
              version: previousNote.data.version + 1,
            },
          }
        );
      }

      return { previousNote };
    },
    onError: (_err, { noteId }, context) => {
      // Rollback on OCC conflict (412) or other failure
      if (context?.previousNote) {
        queryClient.setQueryData(NOTE_QUERY_KEYS.detail(noteId), context.previousNote);
      }
    },
    onSettled: (_data, _err, { noteId }) => {
      queryClient.invalidateQueries({ queryKey: NOTE_QUERY_KEYS.detail(noteId) });
      queryClient.invalidateQueries({ queryKey: NOTE_QUERY_KEYS.lists() });
    },
  });
}

export function useDeleteNoteMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (noteId: string) => notesApi.deleteNote(noteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTE_QUERY_KEYS.lists() });
    },
  });
}

export function useSynthesizeNotesMutation() {
  return useMutation({
    mutationFn: (data: SynthesizeNotesRequest) => notesApi.synthesizeNotes(data),
  });
}
