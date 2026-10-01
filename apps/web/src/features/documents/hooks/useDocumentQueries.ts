import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  documentsApi,
  type ListDocumentsParams,
  type ListChunksParams,
} from "../api/documentsApi";

export const DOCUMENT_QUERY_KEYS = {
  all: ["documents"] as const,
  lists: () => [...DOCUMENT_QUERY_KEYS.all, "list"] as const,
  list: (params: ListDocumentsParams = {}) => [...DOCUMENT_QUERY_KEYS.lists(), params] as const,
  details: () => [...DOCUMENT_QUERY_KEYS.all, "detail"] as const,
  detail: (id: string) => [...DOCUMENT_QUERY_KEYS.details(), id] as const,
  status: (id: string) => [...DOCUMENT_QUERY_KEYS.detail(id), "status"] as const,
  structure: (id: string) => [...DOCUMENT_QUERY_KEYS.detail(id), "structure"] as const,
  summary: (id: string) => [...DOCUMENT_QUERY_KEYS.detail(id), "summary"] as const,
  chunks: (id: string, params: ListChunksParams = {}) =>
    [...DOCUMENT_QUERY_KEYS.detail(id), "chunks", params] as const,
  chunkDetail: (id: string, chunkId: string) =>
    [...DOCUMENT_QUERY_KEYS.detail(id), "chunk", chunkId] as const,
  references: (id: string) => [...DOCUMENT_QUERY_KEYS.detail(id), "references"] as const,
};

export function useDocumentsList(params: ListDocumentsParams = {}) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.list(params),
    queryFn: () => documentsApi.listDocuments(params),
    staleTime: 1000 * 30,
  });
}

export function useDocumentDetail(documentId: string | null | undefined) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.detail(documentId ?? ""),
    queryFn: () => documentsApi.getDocumentDetail(documentId!),
    enabled: Boolean(documentId),
    staleTime: 1000 * 60 * 10, // 10 minutes cache
  });
}

export function useDocumentStatusQuery(documentId: string | null | undefined, enabled = true) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.status(documentId ?? ""),
    queryFn: () => documentsApi.getStatus(documentId!),
    enabled: Boolean(documentId) && enabled,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return 1500;
      if (data.status === "completed" || data.status === "failed") {
        return false;
      }
      return 1500;
    },
  });
}

export function useDocumentStructure(documentId: string | null | undefined) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.structure(documentId ?? ""),
    queryFn: () => documentsApi.getStructure(documentId!),
    enabled: Boolean(documentId),
    staleTime: Infinity,
  });
}

export function useDocumentSummary(documentId: string | null | undefined) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.summary(documentId ?? ""),
    queryFn: () => documentsApi.getSummary(documentId!),
    enabled: Boolean(documentId),
    staleTime: 1000 * 60 * 5, // 5 min
  });
}

export function useDocumentChunks(
  documentId: string | null | undefined,
  params: ListChunksParams = {}
) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.chunks(documentId ?? "", params),
    queryFn: () => documentsApi.getChunks(documentId!, params),
    enabled: Boolean(documentId),
    staleTime: 1000 * 60,
  });
}

export function useDocumentReferences(documentId: string | null | undefined) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.references(documentId ?? ""),
    queryFn: () => documentsApi.extractReferences(documentId!),
    enabled: Boolean(documentId),
    staleTime: Infinity,
  });
}

export function useChunkDetail(
  documentId: string | null | undefined,
  chunkId: string | null | undefined
) {
  return useQuery({
    queryKey: DOCUMENT_QUERY_KEYS.chunkDetail(documentId ?? "", chunkId ?? ""),
    queryFn: () => documentsApi.getChunkDetail(documentId!, chunkId!),
    enabled: Boolean(documentId && chunkId),
  });
}

export function useStarDocumentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, folderId }: { documentId: string; folderId?: string | null }) =>
      documentsApi.starDocument(documentId, folderId),
    onSuccess: (_data, { documentId }) => {
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.detail(documentId) });
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.lists() });
    },
  });
}

export function useDeleteDocumentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) => documentsApi.deleteDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.lists() });
    },
  });
}

export function useGenerateSummaryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentId, force }: { documentId: string; force?: boolean }) =>
      documentsApi.generateSummary(documentId, force),
    onSuccess: (_data, { documentId }) => {
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.summary(documentId) });
    },
  });
}

