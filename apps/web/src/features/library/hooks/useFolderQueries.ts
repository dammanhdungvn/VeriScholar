import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { foldersApi } from "../api/foldersApi";
import { synthesisApi } from "../api/synthesisApi";
import type {
  FolderItem,
  FolderTreeItem,
  FolderCreatePayload,
  FolderUpdatePayload,
  FolderDocumentAssignPayload,
  ComparisonMatrixRequest,
  ComparisonMatrixResponse,
  HierarchicalRagRequest,
  HierarchicalRagResponse,
} from "../types";

export const FOLDER_QUERY_KEYS = {
  all: ["folders", "list"] as const,
  tree: ["folders", "tree"] as const,
  detail: (id: string) => ["folders", "detail", id] as const,
};

/**
 * Hook to fetch flat list of all user folders
 */
export function useFoldersListQuery() {
  return useQuery<FolderItem[]>({
    queryKey: FOLDER_QUERY_KEYS.all,
    queryFn: () => foldersApi.listFolders(),
    staleTime: 30 * 1000,
  });
}

/**
 * Hook to fetch hierarchical nested folder tree
 */
export function useFolderTreeQuery() {
  return useQuery<FolderTreeItem[]>({
    queryKey: FOLDER_QUERY_KEYS.tree,
    queryFn: () => foldersApi.getFolderTree(),
    staleTime: 30 * 1000,
  });
}

/**
 * Hook to fetch details for a single folder
 */
export function useFolderDetailQuery(folderId?: string | null) {
  return useQuery<FolderItem | null>({
    queryKey: folderId ? FOLDER_QUERY_KEYS.detail(folderId) : ["folders", "detail", "none"],
    queryFn: async () => {
      if (!folderId) return null;
      return foldersApi.getFolder(folderId);
    },
    enabled: Boolean(folderId),
  });
}

/**
 * Hook to create a new folder
 */
export function useCreateFolderMutation() {
  const queryClient = useQueryClient();

  return useMutation<FolderItem, Error, FolderCreatePayload>({
    mutationFn: (payload) => foldersApi.createFolder(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.tree });
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.all });
    },
  });
}

/**
 * Hook to update folder
 */
export function useUpdateFolderMutation() {
  const queryClient = useQueryClient();

  return useMutation<FolderItem, Error, { id: string; payload: FolderUpdatePayload }>({
    mutationFn: ({ id, payload }) => foldersApi.updateFolder(id, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.tree });
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.detail(variables.id) });
    },
  });
}

/**
 * Hook to delete folder safely
 */
export function useDeleteFolderMutation() {
  const queryClient = useQueryClient();

  return useMutation<{ message?: string }, Error, string>({
    mutationFn: (id) => foldersApi.deleteFolder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.tree });
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

/**
 * Hook to assign documents to a folder
 */
export function useAssignDocumentsToFolderMutation() {
  const queryClient = useQueryClient();

  return useMutation<
    { assigned_count?: number },
    Error,
    { folderId: string; payload: FolderDocumentAssignPayload }
  >({
    mutationFn: ({ folderId, payload }) => foldersApi.assignDocuments(folderId, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.tree });
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.detail(variables.folderId) });
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

/**
 * Hook to generate Literature Comparison Matrix
 */
export function useComparisonMatrixMutation() {
  return useMutation<ComparisonMatrixResponse, Error, ComparisonMatrixRequest>({
    mutationFn: (payload) => foldersApi.generateComparisonMatrix(payload),
  });
}

/**
 * Hook to execute 2-tier Hierarchical RAG synthesis query
 */
export function useHierarchicalRagMutation() {
  return useMutation<HierarchicalRagResponse, Error, HierarchicalRagRequest>({
    mutationFn: (payload) => synthesisApi.hierarchicalRagQuery(payload),
  });
}
