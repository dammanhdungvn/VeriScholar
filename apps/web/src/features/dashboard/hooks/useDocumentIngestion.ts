import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { dashboardApi } from "../api/dashboardApi";
import { ApiError } from "@/lib/api-client";

interface UseDocumentIngestionOptions {
  pollingIntervalMs?: number;
  maxPollAttempts?: number;
}

export function useDocumentIngestion(options: UseDocumentIngestionOptions = {}) {
  const { pollingIntervalMs = 1000, maxPollAttempts = 120 } = options;
  const setStatus = useWorkspaceStore((s) => s.setStatus);
  const setSession = useWorkspaceStore((s) => s.setSession);
  const setDocument = useWorkspaceStore((s) => s.setDocument);
  const setError = useWorkspaceStore((s) => s.setError);

  const ingest = async (file: File) => {
    // 1. Client Pre-validation
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      const err = new Error("Chỉ chấp nhận tệp định dạng PDF (.pdf).");
      setError(err.message);
      throw err;
    }

    if (file.size > 50 * 1024 * 1024) {
      const err = new Error("Dung lượng tệp vượt quá giới hạn 50MB.");
      setError(err.message);
      throw err;
    }

    try {
      // 2. Upload Document (Temporary storage CAS blob)
      setStatus("uploading", 15, "Đang tải tệp lên máy chủ an toàn...");
      const doc = await documentsApi.uploadDocument(file);
      const cleanTitle = doc.title || file.name.replace(/\.pdf$/i, "");
      setDocument(doc.id, cleanTitle);

      // 3. Lazy Session Creation (Zero DB Junk Invariant)
      setStatus("validating", 35, "Đang thẩm định cấu trúc học thuật & khởi tạo phiên...");
      const session = await dashboardApi.createSession({
        title: cleanTitle,
        initial_document_ids: [doc.id],
      });
      setSession(session.id);

      // 4. Trigger Parse & Embedding Pipeline
      setStatus(
        "parsing",
        50,
        "Đang phân tích layout 2 cột, bóc tách công thức LaTeX & chia chunks..."
      );
      await documentsApi.parseDocument(doc.id);

      // 5. Polling Status until completed
      let attempts = 0;
      while (attempts < maxPollAttempts) {
        attempts++;
        const statusRes = await documentsApi.getStatus(doc.id);

        if (statusRes.status === "completed") {
          break;
        }

        if (statusRes.status === "failed") {
          throw new Error(
            statusRes.error_message || "Xử lý bóc tách tài liệu thất bại."
          );
        }

        // Map progress 50% -> 95%
        const computedProgress = Math.min(
          95,
          50 + Math.round((statusRes.progress || 0) * 0.45)
        );
        setStatus("parsing", computedProgress, "Đang hoàn tất lập chỉ mục vector không gian...");

        await new Promise((resolve) => setTimeout(resolve, pollingIntervalMs));
      }

      // 6. Complete
      setStatus("completed", 100, "Xử lý bài báo thành công.");
      return { documentId: doc.id, sessionId: session.id };
    } catch (err: unknown) {
      let message = "Không thể xử lý tệp PDF. Vui lòng thử lại.";
      if (err instanceof ApiError) {
        message = err.message;
      } else if (err instanceof Error) {
        message = err.message;
      }
      setError(message);
      throw err;
    }
  };

  return { ingest };
}
