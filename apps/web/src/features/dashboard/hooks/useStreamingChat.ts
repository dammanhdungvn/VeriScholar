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
    setMessages([]);
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
    async (explicitPrompt?: string, customRequestId?: string) => {
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

      let effectiveSessionId = activeSessionId;
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
            if (isCancelledRef.current) return;

            try {
              if (ev.data === "[DONE]") {
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
                setIsGenerating(false);
                return;
              }

              const parsed = JSON.parse(ev.data);

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
                const newCites: CitationBadgeData[] = Array.isArray(parsed.citations)
                  ? parsed.citations
                  : parsed.citation
                  ? [parsed.citation]
                  : [];
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
              if (ev.data && ev.data !== "[DONE]") {
                queueToken(ev.data);
              }
            }
          },
          onerror(err) {
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
        if (!isCancelledRef.current && !accumulatedContent) {
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
              citations: turn.citations?.map((c) => ({
                paper_id: c.document_id,
                paper_title: c.document_title,
                page: c.page_number,
                bbox: c.bounding_boxes[0] || [0, 0, 1, 1, c.page_number],
              })),
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
