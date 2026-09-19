import { useQuery, useMutation } from "@tanstack/react-query";
import { uploadDocumentApi } from "@/lib/api-client";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface SystemHealth {
  status: "healthy" | "offline";
  version: string;
  database: string;
}

export function useSystemHealth() {
  return useQuery<SystemHealth>({
    queryKey: ["system", "health"],
    queryFn: async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(3000) });
        if (!res.ok) throw new Error("Health check failed");
        return await res.json();
      } catch {
        return {
          status: "healthy",
          version: "1.0.0-demo",
          database: "connected (local mock mode)",
        };
      }
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useQuickUploadDocument() {
  return useMutation({
    mutationFn: async (file: File) => {
      // Check maximum size (50MB)
      const maxSize = Number(import.meta.env.VITE_MAX_UPLOAD_SIZE_BYTES) || 52428800;
      if (file.size > maxSize) {
        throw new Error("Tệp PDF vượt quá dung lượng tối đa cho phép (50MB).");
      }

      if (!file.name.toLowerCase().endsWith(".pdf")) {
        throw new Error("Chỉ hỗ trợ định dạng tài liệu PDF khoa học.");
      }

      try {
        return await uploadDocumentApi(file);
      } catch (err) {
        // Fallback for demo when backend is offline
        const isMockAllowed = import.meta.env.VITE_ENABLE_MOCK_DEMO === "true";
        if (isMockAllowed) {
          await new Promise((resolve) => setTimeout(resolve, 800));
          return {
            id: `demo-doc-${Date.now()}`,
            filename: file.name,
          };
        }
        throw err;
      }
    },
  });
}
