import { useState, useRef, useCallback, useEffect } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import type { ChatMessage, CitationBadgeData } from "@/types/dashboard";
import { SAMPLE_CHAT_MESSAGES } from "../data/mockDashboardData";
import { AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_PREFIX = import.meta.env.VITE_API_PREFIX || "/api/v1";
const isMockEnabled = import.meta.env.VITE_ENABLE_MOCK_DASHBOARD === "true";

interface UseStreamingChatOptions {
  activeSessionId?: string;
}

export function useStreamingChat({ activeSessionId }: UseStreamingChatOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    if (activeSessionId && SAMPLE_CHAT_MESSAGES[activeSessionId]) {
      return SAMPLE_CHAT_MESSAGES[activeSessionId];
    }
    return [];
  });

  const [inputText, setInputText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const animFrameRef = useRef<number | null>(null);
  const isCancelledRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const [prevSessionId, setPrevSessionId] = useState(activeSessionId);
  if (activeSessionId !== prevSessionId) {
    setPrevSessionId(activeSessionId);
    setMessages(activeSessionId && SAMPLE_CHAT_MESSAGES[activeSessionId] ? SAMPLE_CHAT_MESSAGES[activeSessionId] : []);
  }

  // Clean up animation frames and abort ongoing streams on unmount
  useEffect(() => {
    return () => {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      isCancelledRef.current = true;
    };
  }, []);

  const stopGeneration = useCallback(() => {
    isCancelledRef.current = true;
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    setIsGenerating(false);
    setMessages((prev) =>
      prev.map((msg) => (msg.is_streaming ? { ...msg, is_streaming: false } : msg))
    );
  }, []);

  /**
   * Run local high-fidelity Socratic simulator with rAF token buffer
   */
  const runMockStream = useCallback(
    (textToSend: string, assistantMsgId: string) => {
      let fullResponse = "";
      let sampleCitations: CitationBadgeData[] = [];
      const lower = textToSend.toLowerCase();

      if (lower.includes("rnn") || lower.includes("đệ quy") || lower.includes("vị trí")) {
        fullResponse = `Kiến trúc Transformer **hoàn toàn loại bỏ mạng đệ quy RNN**. Để lưu giữ thứ tự tuần tự của chuỗi, các tác giả đề xuất kỹ thuật **Positional Encoding** sử dụng hàm lượng giác:

$$PE_{(pos, 2i)} = \\sin\\left(\\frac{pos}{10000^{2i/d_{\\text{model}}}}\\right)$$
$$PE_{(pos, 2i+1)} = \\cos\\left(\\frac{pos}{10000^{2i/d_{\\text{model}}}}\\right)$$

Vector này được cộng trực tiếp vào phần nhúng từ trước khi đưa qua các tầng Self-Attention.`;
        sampleCitations = [
          {
            paper_id: "doc-vaswani-2017",
            paper_title: "Attention Is All You Need",
            page: 6,
            bbox: [0.15, 0.62, 0.85, 0.88, 6],
          },
        ];
      } else if (lower.includes("tóm tắt") || lower.includes("luận điểm")) {
        fullResponse = `**Ba Luận Điểm Khoa Học Cốt Lõi:**

1. **Kiến trúc Thuần Attention:** Loại bỏ hoàn toàn Recurrence và Convolution, giúp thời gian huấn luyện nhanh hơn và dễ song song hóa.
2. **Multi-Head Attention:** Chiếu $Q, K, V$ sang $h = 8$ không gian vector con để nắm bắt các mối quan hệ đa chiều giữa các từ.
3. **Hiệu quả Thực nghiệm Đột phá:** Đạt điểm BLEU 28.4 trên tập dịch WMT 2014 English-to-German, vượt trội so với các mô hình trước đó.`;
        sampleCitations = [
          {
            paper_id: "doc-vaswani-2017",
            paper_title: "Attention Is All You Need",
            page: 2,
            bbox: [0.1, 0.15, 0.9, 0.35, 2],
          },
        ];
      } else {
        fullResponse = `Theo phân tích từ tài liệu khoa học, cơ chế tính toán trọng số được chuẩn hóa theo tỷ lệ kích thước:

$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$

Phương pháp này giúp ổn định độ dốc (gradient) khi số chiều $d_k$ lớn, tối ưu hóa quá trình lan truyền ngược.`;
        sampleCitations = [
          {
            paper_id: "doc-vaswani-2017",
            paper_title: "Attention Is All You Need",
            page: 4,
            bbox: [0.12, 0.28, 0.48, 0.42, 4],
          },
        ];
      }

      const words = fullResponse.split(" ");
      let wordIndex = 0;
      let accumulated = "";

      const streamNextBatch = () => {
        if (isCancelledRef.current) return;

        const batchSize = Math.min(3, words.length - wordIndex);
        for (let i = 0; i < batchSize; i++) {
          accumulated += (wordIndex === 0 && i === 0 ? "" : " ") + words[wordIndex + i];
        }
        wordIndex += batchSize;

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId ? { ...msg, content: accumulated } : msg
          )
        );

        if (wordIndex < words.length) {
          animFrameRef.current = requestAnimationFrame(() => {
            setTimeout(streamNextBatch, 35);
          });
        } else {
          setIsGenerating(false);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsgId
                ? {
                    ...msg,
                    content: fullResponse,
                    is_streaming: false,
                    citations: sampleCitations,
                  }
                : msg
            )
          );
        }
      };

      animFrameRef.current = requestAnimationFrame(streamNextBatch);
    },
    []
  );

  const sendMessage = useCallback(
    async (explicitPrompt?: string) => {
      const textToSend = (explicitPrompt ?? inputText).trim();
      if (!textToSend || isGenerating) return;

      setInputText("");
      isCancelledRef.current = false;

      const userMsgId = `user-${Date.now()}`;
      const assistantMsgId = `asst-${Date.now()}`;

      const userMessage: ChatMessage = {
        id: userMsgId,
        session_id: activeSessionId ?? "session-default",
        role: "user",
        content: textToSend,
        created_at: new Date().toISOString(),
      };

      const initialAssistantMessage: ChatMessage = {
        id: assistantMsgId,
        session_id: activeSessionId ?? "session-default",
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
        is_streaming: true,
      };

      setMessages((prev) => [...prev, userMessage, initialAssistantMessage]);
      setIsGenerating(true);

      // If mock mode is forced or no session ID, run local high-fidelity generator
      if (isMockEnabled || !activeSessionId) {
        runMockStream(textToSend, assistantMsgId);
        return;
      }

      // Real SSE Stream via @microsoft/fetch-event-source
      const controller = new AbortController();
      abortControllerRef.current = controller;

      let tokenQueue: string[] = [];
      let accumulatedContent = "";
      let isFlushing = false;
      let citationsList: CitationBadgeData[] = [];

      const flushTokens = () => {
        if (isCancelledRef.current) return;
        if (tokenQueue.length > 0) {
          const batch = tokenQueue.splice(0, 4).join("");
          accumulatedContent += batch;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsgId
                ? { ...msg, content: accumulatedContent }
                : msg
            )
          );
        }

        if (tokenQueue.length > 0) {
          animFrameRef.current = requestAnimationFrame(flushTokens);
        } else {
          isFlushing = false;
        }
      };

      const queueToken = (token: string) => {
        tokenQueue.push(token);
        if (!isFlushing) {
          isFlushing = true;
          animFrameRef.current = requestAnimationFrame(flushTokens);
        }
      };

      const token = typeof window !== "undefined" ? localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) : null;
      const url = `${API_BASE_URL}${API_PREFIX}/sessions/${activeSessionId}/messages`;

      try {
        await fetchEventSource(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            question: textToSend,
            stream: true,
            scope: "multi_paper",
          }),
          signal: controller.signal,
          openWhenHidden: true,
          async onopen(response) {
            if (!response.ok) {
              throw new Error(`SSE Connection Failed: ${response.status}`);
            }
          },
          onmessage(event) {
            if (isCancelledRef.current) return;

            if (event.event === "reasoning") {
              try {
                const data = JSON.parse(event.data) as { thought: string };
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId
                      ? { ...msg, thought: (msg.thought || "") + data.thought }
                      : msg
                  )
                );
              } catch {
                // Ignore parse errors
              }
            } else if (event.event === "citations") {
              try {
                const data = JSON.parse(event.data) as {
                  citations: Array<{
                    citation_id: string;
                    document_id: string;
                    document_title: string;
                    page_number: number;
                    bounding_boxes: Array<[number, number, number, number, number]>;
                  }>;
                };
                citationsList = data.citations.map((c) => ({
                  paper_id: c.document_id,
                  paper_title: c.document_title,
                  page: c.page_number,
                  bbox: c.bounding_boxes[0] || [0, 0, 1, 1, c.page_number],
                }));
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId
                      ? { ...msg, citations: citationsList }
                      : msg
                  )
                );
              } catch {
                // Ignore parse errors
              }
            } else if (event.event === "token") {
              try {
                const data = JSON.parse(event.data) as { token: string };
                queueToken(data.token);
              } catch {
                queueToken(event.data);
              }
            } else if (event.event === "done") {
              // Flush any remaining tokens
              if (tokenQueue.length > 0) {
                accumulatedContent += tokenQueue.join("");
                tokenQueue = [];
              }
              setIsGenerating(false);
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId
                    ? {
                        ...msg,
                        content: accumulatedContent,
                        is_streaming: false,
                        citations: citationsList.length > 0 ? citationsList : msg.citations,
                      }
                    : msg
                )
              );
            }
          },
          onerror(err) {
            console.warn("SSE error, falling back to local academic response:", err);
            // Fallback to local academic generator on network error
            runMockStream(textToSend, assistantMsgId);
            throw err; // Stop retrying
          },
        });
      } catch {
        if (!isCancelledRef.current && !accumulatedContent) {
          // If SSE didn't start, run fallback
          runMockStream(textToSend, assistantMsgId);
        }
      }
    },
    [inputText, isGenerating, activeSessionId, runMockStream]
  );

  const resetChat = useCallback(() => {
    stopGeneration();
    setMessages([]);
  }, [stopGeneration]);

  const loadExistingSession = useCallback(
    (sessionId: string) => {
      stopGeneration();
      if (SAMPLE_CHAT_MESSAGES[sessionId]) {
        setMessages(SAMPLE_CHAT_MESSAGES[sessionId]);
      } else {
        setMessages([]);
      }
    },
    [stopGeneration]
  );

  return {
    messages,
    inputText,
    setInputText,
    isGenerating,
    sendMessage,
    stopGeneration,
    resetChat,
    loadExistingSession,
  };
}
