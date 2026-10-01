import { useWorkspaceStore, type IngestionDocumentStatus } from "../stores/useWorkspaceStore";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { dashboardApi } from "../api/dashboardApi";
import { ApiError } from "@/lib/api-client";

interface UseDocumentIngestionOptions {
  pollingIntervalMs?: number;
  maxPollAttempts?: number;
  minDurationMs?: number;
}

export function useDocumentIngestion(options: UseDocumentIngestionOptions = {}) {
  const {
    pollingIntervalMs = 1000,
    maxPollAttempts = 120,
    minDurationMs = options.minDurationMs ?? (options.pollingIntervalMs && options.pollingIntervalMs <= 50 ? 50 : 1200),
  } = options;

  const setStatus = useWorkspaceStore((s) => s.setStatus);
  const setSession = useWorkspaceStore((s) => s.setSession);
  const setDocument = useWorkspaceStore((s) => s.setDocument);
  const setError = useWorkspaceStore((s) => s.setError);

  const ingest = async (
    file: File,
    onSessionCreated?: (sessionId: string) => void,
    existingSessionId?: string
  ) => {
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

    const cleanTitle = file.name.replace(/\.pdf$/i, "");

    // Khởi tạo bộ điều khiển tiến trình mượt mà (Smooth Perceptual Progress Controller)
    // Đảm bảo thanh tiến trình chạy mượt từ 0% -> 100%, không bao giờ nhảy cóc lên 50% hay treo cứng.
    let currentProgress = 0;
    let targetProgress = 15;
    let currentStatus: IngestionDocumentStatus = "validating";
    let currentMessage = "Đang thẩm định mật độ học thuật & khởi tạo phiên...";
    let isBackendDone = false;
    let isAborted = false;
    let finishResolver: (() => void) | null = null;

    const tickIntervalMs = 25;
    const baseStep = Math.max(0.8, 100 / (minDurationMs / tickIntervalMs));

    // Đặt trạng thái ban đầu chính xác tại 0%
    setStatus("validating", 0, currentMessage);

    const progressTimer = setInterval(() => {
      if (isAborted) {
        clearInterval(progressTimer);
        return;
      }

      if (isBackendDone) {
        // Backend đã xử lý xong: Tăng tốc mượt mà lướt thẳng tới 100%
        const remaining = 100 - currentProgress;
        const step = Math.max(baseStep * 1.6, remaining * 0.22);
        currentProgress = Math.min(100, currentProgress + step);

        const rounded = Math.round(currentProgress);
        const stageMsg =
          rounded >= 100
            ? "Xử lý bài báo thành công."
            : rounded >= 90
            ? "Đang hoàn tất chỉ mục bằng chứng học thuật..."
            : currentMessage;

        setStatus(rounded >= 100 ? "completed" : "parsing", rounded, stageMsg);

        if (currentProgress >= 100) {
          clearInterval(progressTimer);
          if (finishResolver) {
            finishResolver();
          }
        }
        return;
      }

      // Backend đang xử lý: Tăng dần đều tới targetProgress, không bao giờ nhảy cóc
      if (currentProgress < targetProgress) {
        const remaining = targetProgress - currentProgress;
        const step = Math.max(0.4, Math.min(baseStep, remaining * 0.28));
        currentProgress = Math.min(targetProgress, currentProgress + step);
      } else if (currentProgress < 94) {
        // Giảm tốc tiệm cận (asymptotic crawl) để thanh tiến trình luôn chuyển động nhẹ, không bị đơ
        currentProgress = Math.min(94, currentProgress + 0.12);
      }

      setStatus(currentStatus, Math.round(currentProgress), currentMessage);
    }, tickIntervalMs);

    const updateStage = (
      status: IngestionDocumentStatus,
      target: number,
      message: string
    ) => {
      currentStatus = status;
      targetProgress = Math.max(targetProgress, target);
      currentMessage = message;
    };

    const waitForSmoothCompletion = async () => {
      isBackendDone = true;
      return new Promise<void>((resolve) => {
        finishResolver = () => {
          // Dừng nhẹ 180ms tại 100% để người dùng cảm nhận trạng thái hoàn tất
          setTimeout(resolve, minDurationMs <= 50 ? 5 : 180);
        };
      });
    };

    try {
      // 1. Chạy API tạo session chat (POST /api/v1/sessions)
      let targetSessionId = existingSessionId;
      if (!targetSessionId) {
        updateStage(
          "validating",
          25,
          "Đang khởi tạo không gian phiên nghiên cứu học thuật..."
        );
        const session = await dashboardApi.createSession({
          title: `Nghiên cứu: ${cleanTitle}`,
        });
        targetSessionId = session.id;
        setSession(session.id);
        if (onSessionCreated) {
          onSessionCreated(session.id);
        }
      }

      // 2. Chạy sang API về xử lý file:
      // 2.1. Tải lên PDF và liên kết vào session (POST /api/v1/documents)
      updateStage(
        "uploading",
        50,
        "Đang tải tệp PDF lên máy chủ an toàn CAS & liên kết phiên..."
      );
      const doc = await documentsApi.uploadDocument(file, targetSessionId);
      const displayTitle = doc.title || cleanTitle;
      setDocument(doc.id, displayTitle);

      // 2.2. Kích hoạt pipeline bóc tách & chia chunks (POST /api/v1/documents/{id}:parse)
      updateStage(
        "parsing",
        70,
        "Đang phân tích layout 2 cột, bóc tách công thức LaTeX & bảng biểu..."
      );
      await documentsApi.parseDocument(doc.id, {
        chunk_size: 512,
        chunk_overlap: 50,
        extract_tables: true,
      });

      // 2.3. Polling trạng thái xử lý file (GET /api/v1/documents/{id}/status)
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

        // Cập nhật message theo từng stage học thuật từ backend (Swagger)
        let stageMessage = "Đang hoàn tất lập chỉ mục vector không gian...";
        let stageTarget = 85;
        if (statusRes.stage === "validation") {
          stageMessage = "Đang thẩm định mật độ học thuật của bài báo...";
          stageTarget = 60;
        } else if (statusRes.stage === "layout_detection") {
          stageMessage = "Đang nhận diện bố cục 2 cột & phát hiện bảng biểu...";
          stageTarget = 70;
        } else if (statusRes.stage === "running_ocr" || statusRes.stage === "ocr") {
          stageMessage = "Đang bóc tách văn bản vi mô & công thức LaTeX...";
          stageTarget = 78;
        } else if (statusRes.stage === "chunking") {
          stageMessage = "Đang phân đoạn ngữ cảnh chunks theo đoạn văn...";
          stageTarget = 86;
        } else if (statusRes.stage === "embedding") {
          stageMessage = "Đang hoàn tất lập chỉ mục vector không gian...";
          stageTarget = 92;
        }

        if (statusRes.progress && statusRes.progress > 0) {
          stageTarget = Math.max(
            stageTarget,
            Math.min(94, 60 + Math.round(statusRes.progress * 0.34))
          );
        }

        updateStage("parsing", stageTarget, stageMessage);

        await new Promise((resolve) => setTimeout(resolve, pollingIntervalMs));
      }

      // 3. Backend đã xong -> Chờ thanh tiến trình hoàn tất hành trình 0% -> 100%
      await waitForSmoothCompletion();
      return { documentId: doc.id, sessionId: targetSessionId };
    } catch (err: unknown) {
      isAborted = true;
      clearInterval(progressTimer);
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
