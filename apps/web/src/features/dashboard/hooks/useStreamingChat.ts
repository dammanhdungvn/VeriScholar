import { useState, useRef, useCallback, useEffect } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import type { ChatMessage, CitationBadgeData } from "@/types/dashboard";
import { AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { generateRequestId } from "@/lib/api-client";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const API_PREFIX = import.meta.env.VITE_API_PREFIX || "/api/v1";

interface UseStreamingChatOptions {
  activeSessionId?: string;
  onSessionCreated?: (sessionId: string) => void;
}

function normalizeCitation(raw: unknown): CitationBadgeData {
  const item = (typeof raw === "object" && raw !== null ? raw : {}) as Record<string, unknown>;
  const page = Number(item.page ?? item.page_number ?? 1);
  let bbox: [number, number, number, number, number] = [0, 0, 1, 1, page];

  if (Array.isArray(item.bbox) && item.bbox.length === 5) {
    bbox = item.bbox as [number, number, number, number, number];
  } else if (
    Array.isArray(item.bounding_boxes) &&
    item.bounding_boxes.length > 0 &&
    Array.isArray(item.bounding_boxes[0]) &&
    item.bounding_boxes[0].length === 5
  ) {
    bbox = item.bounding_boxes[0] as [number, number, number, number, number];
  }

  return {
    citation_id: typeof item.citation_id === "string" ? item.citation_id : undefined,
    paper_id: String(item.paper_id ?? item.document_id ?? ""),
    paper_title: String(item.paper_title ?? item.document_title ?? "Tài liệu trích dẫn"),
    page,
    bbox,
  };
}

export function useStreamingChat({
  activeSessionId,
  onSessionCreated,
}: UseStreamingChatOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const [inputText, setInputText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const animFrameRef = useRef<number | null>(null);
  const isCancelledRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const [prevSessionId, setPrevSessionId] = useState(activeSessionId);
  if (activeSessionId !== prevSessionId) {
    setPrevSessionId(activeSessionId);
    if (!isGenerating) {
      setMessages([]);
    }
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

  const sendMessage = useCallback(
    async (explicitPrompt?: string, customRequestId?: string, targetSessionId?: string) => {
      const textToSend = (explicitPrompt ?? inputText).trim();
      if (!textToSend || isGenerating) return;

      setInputText("");
      isCancelledRef.current = false;

      let effectiveSessionId = targetSessionId || activeSessionId;

      const userMsgId = `user-${Date.now()}`;
      const assistantMsgId = `asst-${Date.now()}`;

      const userMessage: ChatMessage = {
        id: userMsgId,
        session_id: effectiveSessionId ?? "session-default",
        role: "user",
        content: textToSend,
        created_at: new Date().toISOString(),
      };

      const initialAssistantMessage: ChatMessage = {
        id: assistantMsgId,
        session_id: effectiveSessionId ?? "session-default",
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
        is_streaming: true,
      };

      setMessages((prev) => [...prev, userMessage, initialAssistantMessage]);
      setIsGenerating(true);
      if (!effectiveSessionId) {
        try {
          const titleSnippet = textToSend.slice(0, 32);
          const createRes = await sessionsApi.createSession({
            title: `Nghiên cứu: ${titleSnippet}`,
          });
          if (createRes?.data?.id) {
            effectiveSessionId = createRes.data.id;
            onSessionCreated?.(effectiveSessionId);

            const openDocs = useReaderStore.getState().openDocumentIds;
            for (const docId of openDocs) {
              try {
                await sessionsApi.addDocumentToSession(effectiveSessionId, {
                  source_type: "document_id",
                  document_id: docId,
                });
              } catch {
                // Ignore if already added
              }
            }
          }
        } catch (err) {
          console.warn("Could not auto-create session for chat:", err);
        }
      }

      // If no session could be established, fail explicitly
      if (!effectiveSessionId) {
        setIsGenerating(false);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content:
                    "Không thể khởi tạo phiên nghiên cứu trên máy chủ backend. Vui lòng kiểm tra kết nối API.",
                  is_streaming: false,
                }
              : msg
          )
        );
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

      let streamFinished = false;

      const finishStream = () => {
        if (streamFinished) return;
        streamFinished = true;

        if (animFrameRef.current) {
          cancelAnimationFrame(animFrameRef.current);
          animFrameRef.current = null;
        }
        if (tokenQueue.length > 0) {
          accumulatedContent += tokenQueue.join("");
          tokenQueue = [];
        }
        isFlushing = false;

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: accumulatedContent || msg.content,
                  is_streaming: false,
                  citations: citationsList.length > 0 ? citationsList : msg.citations,
                }
              : msg.is_streaming
              ? { ...msg, is_streaming: false }
              : msg
          )
        );
        setIsGenerating(false);
      };

      const token = typeof window !== "undefined" ? localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) : null;
      const url = `${API_BASE_URL}${API_PREFIX}/sessions/${effectiveSessionId}/messages`;
      const finalRequestId = generateRequestId(customRequestId);

      try {
        await fetchEventSource(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            "X-Request-ID": finalRequestId,
          },
          body: JSON.stringify({
            message: textToSend,
          }),
          signal: controller.signal,
          openWhenHidden: true,
          async onopen(response) {
            if (response.ok) return;
            const errorText = await response.text().catch(() => "");
            throw new Error(`SSE stream connection failed (${response.status}): ${errorText}`);
          },
          onmessage(ev) {
            if (isCancelledRef.current || streamFinished) return;

            // Direct check for [DONE] token or done event
            if (
              ev.event === "done" ||
              ev.data === "[DONE]" ||
              ev.data === "DONE"
            ) {
              finishStream();
              controller.abort();
              return;
            }

            try {
              const parsed = JSON.parse(ev.data);

              if (
                parsed.type === "done" ||
                parsed.finish_reason ||
                parsed.status === "completed"
              ) {
                finishStream();
                controller.abort();
                return;
              }

              if (parsed.type === "thinking" || parsed.type === "thought") {
                const thoughtToken = parsed.token || parsed.thought || parsed.content || "";
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId
                      ? { ...msg, thought: (msg.thought || "") + thoughtToken }
                      : msg
                  )
                );
              } else if (parsed.type === "token" || parsed.type === "content") {
                const tokenText = parsed.token || parsed.text || parsed.content || "";
                queueToken(tokenText);
              } else if (parsed.type === "citation" || parsed.type === "citations") {
                const rawCites = Array.isArray(parsed.citations)
                  ? parsed.citations
                  : parsed.citation
                  ? [parsed.citation]
                  : [];
                const newCites: CitationBadgeData[] = rawCites.map(normalizeCitation);
                citationsList = [...citationsList, ...newCites];
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId
                      ? { ...msg, citations: citationsList }
                      : msg
                  )
                );
              } else if (parsed.type === "presupposition_alert") {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId
                      ? { ...msg, presupposition_alert: parsed.alert }
                      : msg
                  )
                );
              } else if (parsed.token || parsed.text) {
                queueToken(parsed.token || parsed.text);
              }
            } catch {
              if (ev.data && ev.data !== "[DONE]" && ev.data !== "DONE") {
                queueToken(ev.data);
              }
            }
          },
          async onclose() {
            // Server closed connection normally
            finishStream();
            controller.abort();
          },
          onerror(err) {
            if (controller.signal.aborted || streamFinished) {
              return;
            }
            console.error("SSE stream error:", err);
            if (!isCancelledRef.current) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId
                    ? {
                        ...msg,
                        content:
                          accumulatedContent ||
                          "Không thể kết nối đến máy chủ Socratic Copilot để hoàn tất suy luận. Vui lòng kiểm tra kết nối mạng và thử lại.",
                        is_streaming: false,
                      }
                    : msg
                )
              );
              setIsGenerating(false);
            }
            throw err;
          },
        });
      } catch {
        if (!controller.signal.aborted && !isCancelledRef.current && !accumulatedContent) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsgId
                ? {
                    ...msg,
                    content: "Lỗi kết nối khi gửi câu hỏi tới hệ thống.",
                    is_streaming: false,
                  }
                : msg
            )
          );
          setIsGenerating(false);
        }
      } finally {
        // Enforce state transition to idle regardless of what happened
        finishStream();
        if (animFrameRef.current) {
          cancelAnimationFrame(animFrameRef.current);
          animFrameRef.current = null;
        }
        tokenQueue = [];
        isFlushing = false;
        setIsGenerating(false);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: accumulatedContent || msg.content || (isCancelledRef.current ? "" : "Đã hoàn tất kết nối."),
                  is_streaming: false,
                  citations: citationsList.length > 0 ? citationsList : msg.citations,
                }
              : msg.is_streaming
              ? { ...msg, is_streaming: false }
              : msg
          )
        );
        abortControllerRef.current = null;
      }
    },
    [inputText, isGenerating, activeSessionId, onSessionCreated]
  );

  const resetChat = useCallback(async () => {
    stopGeneration();
    setMessages([]);
    if (activeSessionId) {
      try {
        await sessionsApi.clearSessionMessages(activeSessionId);
      } catch (err) {
        console.warn("Failed to clear messages on backend:", err);
      }
    }
  }, [stopGeneration, activeSessionId]);

  const loadExistingSession = useCallback(
    async (sessionId: string) => {
      if (isGenerating) return;
      stopGeneration();
      try {
        const response = await sessionsApi.listSessionMessages(sessionId);
        if (response.data && response.data.length > 0) {
          const mappedMessages: ChatMessage[] = [];
          for (const turn of response.data) {
            mappedMessages.push({
              id: `${turn.id}-q`,
              session_id: turn.session_id,
              role: "user",
              content: turn.question,
              created_at: turn.created_at,
            });
            mappedMessages.push({
              id: `${turn.id}-a`,
              session_id: turn.session_id,
              role: "assistant",
              content: turn.answer,
              citations: turn.citations?.map(normalizeCitation),
              created_at: turn.created_at,
            });
          }
          setMessages(mappedMessages);
          return;
        }
      } catch {
        // Fallback to empty if offline/not found
      }
      setMessages([]);
    },
    [stopGeneration, isGenerating]
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
