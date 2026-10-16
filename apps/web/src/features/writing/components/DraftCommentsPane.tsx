import { useState, useCallback } from "react";
import {
  MessageSquare,
  CheckCircle2,
  Trash2,
  Reply,
  X,
  Send,
  PlusCircle,
  CornerDownRight,
  RotateCcw,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import type { DraftComment } from "../types";
import { cn } from "@/lib/utils";

interface DraftCommentsPaneProps {
  onClose?: () => void;
}

export function DraftCommentsPane({ onClose }: DraftCommentsPaneProps) {
  const {
    activeDraftId,
    comments,
    activeCommentId,
    setActiveCommentId,
    addComment,
    updateCommentInStore,
    removeCommentFromStore,
    setCommentsPaneOpen,
    selectionRange,
    editorContent,
  } = useWritingStore();

  const [activeTab, setActiveTab] = useState<"active" | "resolved">("active");
  const [replyTextMap, setReplyTextMap] = useState<Record<string, string>>({});
  const [activeReplyBoxId, setActiveReplyBoxId] = useState<string | null>(null);
  const [newCommentText, setNewCommentText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleClose = () => {
    if (onClose) {
      onClose();
    } else {
      setCommentsPaneOpen(false);
    }
  };

  // Filter top-level comments (or all comments where parent_id is null/undefined)
  const topLevelComments = comments.filter((c) => !c.parent_id);
  const filteredComments = topLevelComments.filter((c) =>
    activeTab === "active" ? !c.is_resolved : c.is_resolved
  );

  const unresolvedCount = topLevelComments.filter((c) => !c.is_resolved).length;
  const resolvedCount = topLevelComments.filter((c) => c.is_resolved).length;

  // Selected text from editor
  const selectedTextSnippet =
    selectionRange && selectionRange.start !== selectionRange.end
      ? editorContent.slice(selectionRange.start, selectionRange.end).trim()
      : "";

  // Create new top-level comment
  const handleCreateNewComment = useCallback(async () => {
    if (!activeDraftId || !newCommentText.trim()) return;

    try {
      setIsSubmitting(true);
      const start = selectionRange?.start ?? 0;
      const end = selectionRange?.end ?? 0;
      const snippet = selectedTextSnippet || "Toàn bộ bản thảo";

      const created = await draftsApi.createComment(activeDraftId, {
        start_offset: start,
        end_offset: end,
        selected_text: snippet,
        comment_text: newCommentText.trim(),
      });

      addComment(created);
      setNewCommentText("");
      setActiveCommentId(created.id);
    } catch (err) {
      console.error("Create comment failed:", err);
    } finally {
      setIsSubmitting(false);
    }
  }, [
    activeDraftId,
    newCommentText,
    selectionRange,
    selectedTextSnippet,
    addComment,
    setActiveCommentId,
  ]);

  // Toggle resolve status
  const handleToggleResolve = useCallback(
    async (comment: DraftComment) => {
      if (!activeDraftId) return;
      try {
        const nextResolved = !comment.is_resolved;
        const updated = await draftsApi.updateComment(activeDraftId, comment.id, {
          is_resolved: nextResolved,
        });
        updateCommentInStore(updated);
      } catch (err) {
        console.error("Toggle resolve comment failed:", err);
      }
    },
    [activeDraftId, updateCommentInStore]
  );

  // Delete comment
  const handleDeleteComment = useCallback(
    async (commentId: string) => {
      if (!activeDraftId) return;
      try {
        await draftsApi.deleteComment(activeDraftId, commentId);
        removeCommentFromStore(commentId);
      } catch (err) {
        console.error("Delete comment failed:", err);
      }
    },
    [activeDraftId, removeCommentFromStore]
  );

  // Send reply
  const handleSendReply = useCallback(
    async (parentComment: DraftComment) => {
      if (!activeDraftId) return;
      const text = replyTextMap[parentComment.id]?.trim();
      if (!text) return;

      try {
        setIsSubmitting(true);
        const reply = await draftsApi.createComment(activeDraftId, {
          start_offset: parentComment.start_offset,
          end_offset: parentComment.end_offset,
          selected_text: parentComment.selected_text,
          comment_text: text,
          parent_id: parentComment.id,
        });

        addComment(reply);
        setReplyTextMap((prev) => ({ ...prev, [parentComment.id]: "" }));
        setActiveReplyBoxId(null);
      } catch (err) {
        console.error("Send reply failed:", err);
      } finally {
        setIsSubmitting(false);
      }
    },
    [activeDraftId, replyTextMap, addComment]
  );

  return (
    <div
      data-testid="draft-comments-pane"
      className="w-80 md:w-96 flex flex-col h-full bg-[#fbf9f5] dark:bg-[#1a1917] border-l border-[#e8e4dc] dark:border-[#2e2b26] shrink-0 overflow-hidden text-ink dark:text-zinc-200 z-10 shadow-xs"
    >
      {/* 1. Header with title and close button */}
      <div className="h-12 px-4 border-b border-[#ece8df] dark:border-[#2a2824] bg-surface-cream dark:bg-[#1e1c19] flex items-center justify-between select-none shrink-0">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-coral-600 dark:text-coral-400" />
          <span className="font-semibold text-xs tracking-tight">Phản Biện & Nhận Xét</span>
        </div>
        <button
          type="button"
          data-testid="close-comments-pane-btn"
          onClick={handleClose}
          className="p-1 rounded-md text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#ece8df] dark:hover:bg-[#282623] transition-colors cursor-pointer"
          title="Đóng bảng nhận xét"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Filter Tabs: Active vs Resolved */}
      <div className="px-3 pt-2.5 pb-2 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1c1b18] shrink-0">
        <div className="grid grid-cols-2 p-0.5 bg-[#ece8df] dark:bg-[#252320] rounded-lg text-xs font-medium">
          <button
            type="button"
            data-testid="filter-active-comments-btn"
            onClick={() => setActiveTab("active")}
            className={cn(
              "py-1 rounded-md transition-colors text-center cursor-pointer flex items-center justify-center gap-1.5",
              activeTab === "active"
                ? "bg-white dark:bg-[#181715] text-coral-600 dark:text-coral-400 shadow-xs font-semibold"
                : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
            )}
          >
            <span>Chưa xử lý</span>
            <span className="text-[10px] px-1.5 py-0.2 bg-coral-500/10 text-coral-700 dark:text-coral-300 rounded-full font-mono">
              {unresolvedCount}
            </span>
          </button>
          <button
            type="button"
            data-testid="filter-resolved-comments-btn"
            onClick={() => setActiveTab("resolved")}
            className={cn(
              "py-1 rounded-md transition-colors text-center cursor-pointer flex items-center justify-center gap-1.5",
              activeTab === "resolved"
                ? "bg-white dark:bg-[#181715] text-emerald-600 dark:text-emerald-400 shadow-xs font-semibold"
                : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
            )}
          >
            <span>Đã giải quyết</span>
            <span className="text-[10px] px-1.5 py-0.2 bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 rounded-full font-mono">
              {resolvedCount}
            </span>
          </button>
        </div>
      </div>

      {/* 3. New Comment Composer (when selection exists or user wants to add note) */}
      <div className="p-3 border-b border-[#ece8df] dark:border-[#2a2824] bg-white/70 dark:bg-[#191816] shrink-0">
        <div className="text-[11px] font-medium text-muted dark:text-zinc-400 mb-1.5 flex items-center gap-1">
          <PlusCircle className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
          <span>Thêm nhận xét mới</span>
        </div>

        {selectedTextSnippet ? (
          <div className="p-2 mb-2 rounded bg-amber-500/10 border-l-2 border-amber-500 text-[11px] text-amber-900 dark:text-amber-200 italic line-clamp-2">
            "{selectedTextSnippet}"
          </div>
        ) : (
          <div className="text-[11px] text-zinc-400 dark:text-zinc-500 italic mb-1.5">
            Mẹo: Bôi đen đoạn văn bản trong editor để gắn nhận xét cụ thể.
          </div>
        )}

        <div className="flex gap-1.5">
          <textarea
            data-testid="new-comment-input"
            value={newCommentText}
            onChange={(e) => setNewCommentText(e.target.value)}
            placeholder="Nhập nội dung nhận xét / phản biện..."
            rows={2}
            className="flex-1 p-2 text-xs bg-surface-cream dark:bg-[#23211d] border border-[#d8d2c4] dark:border-[#33302b] rounded-md outline-none focus:border-coral-500 resize-none font-sans"
          />
          <button
            type="button"
            data-testid="submit-new-comment-btn"
            disabled={!newCommentText.trim() || isSubmitting}
            onClick={handleCreateNewComment}
            className="px-3 rounded-md bg-coral-500 hover:bg-coral-600 disabled:opacity-50 text-white text-xs font-medium flex items-center justify-center transition-colors cursor-pointer self-end py-2"
            title="Gửi nhận xét"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 4. Comments List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {filteredComments.length === 0 ? (
          <div className="h-44 flex flex-col items-center justify-center text-center p-4 text-muted dark:text-zinc-500">
            <MessageSquare className="w-8 h-8 stroke-1 text-zinc-300 dark:text-zinc-700 mb-2" />
            <p className="text-xs font-medium">
              {activeTab === "active"
                ? "Không có nhận xét nào chưa giải quyết."
                : "Chưa có nhận xét nào được đánh dấu đã giải quyết."}
            </p>
            <p className="text-[11px] mt-1 text-zinc-400 dark:text-zinc-600">
              {activeTab === "active"
                ? "Bôi đen một đoạn văn bản và gửi nhận xét để bắt đầu phản biện."
                : "Các nhận xét đã xử lý xong sẽ xuất hiện tại đây."}
            </p>
          </div>
        ) : (
          filteredComments.map((comment) => {
            const isSelected = activeCommentId === comment.id;
            const replies = comment.replies || [];

            return (
              <div
                key={comment.id}
                data-testid={`comment-card-${comment.id}`}
                onClick={() => setActiveCommentId(comment.id)}
                className={cn(
                  "p-3 rounded-lg border bg-white dark:bg-[#201e1a] transition-all text-xs select-text",
                  isSelected
                    ? "border-coral-500/60 ring-1 ring-coral-500/20 shadow-xs"
                    : "border-[#ece8df] dark:border-[#2e2b26] hover:border-zinc-300 dark:hover:border-zinc-700",
                  comment.is_resolved && "opacity-75 bg-[#faf8f4] dark:bg-[#1a1917]"
                )}
              >
                {/* Author and Date */}
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-ink dark:text-zinc-100">
                      {comment.author_name}
                    </span>
                    {comment.is_resolved && (
                      <span className="flex items-center gap-0.5 text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">
                        <CheckCircle2 className="w-3 h-3" /> Đã xong
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] text-muted dark:text-zinc-500 font-mono">
                    {new Date(comment.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>

                {/* Quoted selected text (soft yellow snippet) */}
                {comment.selected_text && (
                  <div className="p-2 mb-2 rounded bg-amber-500/10 dark:bg-amber-950/40 border-l-2 border-amber-500 text-[11px] text-amber-900 dark:text-amber-200 italic">
                    "{comment.selected_text}"
                  </div>
                )}

                {/* Main Comment Text */}
                <p className="text-zinc-800 dark:text-zinc-200 leading-relaxed mb-2 whitespace-pre-wrap">
                  {comment.comment_text}
                </p>

                {/* Action buttons: Resolve, Reply, Delete */}
                <div className="flex items-center justify-between pt-1.5 border-t border-[#f0eae1] dark:border-[#2a2824] text-[11px] text-muted dark:text-zinc-400">
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      data-testid={`resolve-comment-btn-${comment.id}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleResolve(comment);
                      }}
                      className={cn(
                        "flex items-center gap-1 hover:underline cursor-pointer font-medium",
                        comment.is_resolved
                          ? "text-zinc-500 hover:text-zinc-700"
                          : "text-emerald-600 dark:text-emerald-400 hover:text-emerald-700"
                      )}
                    >
                      {comment.is_resolved ? (
                        <>
                          <RotateCcw className="w-3 h-3" /> Mở lại
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-3 h-3" /> Giải quyết
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      data-testid={`reply-comment-btn-${comment.id}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveReplyBoxId(
                          activeReplyBoxId === comment.id ? null : comment.id
                        );
                      }}
                      className="flex items-center gap-1 hover:underline cursor-pointer text-coral-600 dark:text-coral-400"
                    >
                      <Reply className="w-3 h-3" /> Trả lời ({replies.length})
                    </button>
                  </div>

                  <button
                    type="button"
                    data-testid={`delete-comment-btn-${comment.id}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteComment(comment.id);
                    }}
                    className="p-1 rounded text-zinc-400 hover:text-rose-600 hover:bg-rose-500/10 transition-colors cursor-pointer"
                    title="Xóa nhận xét"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Threaded Replies List */}
                {replies.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-[#f0eae1] dark:border-[#2a2824] space-y-2">
                    {replies.map((reply) => (
                      <div
                        key={reply.id}
                        className="pl-3 border-l-2 border-coral-500/30 dark:border-coral-500/20 py-1"
                      >
                        <div className="flex items-center justify-between text-[11px] mb-0.5">
                          <span className="font-semibold text-ink dark:text-zinc-200">
                            {reply.author_name}
                          </span>
                          <span className="text-[10px] text-zinc-400 dark:text-zinc-500 font-mono">
                            {new Date(reply.created_at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </div>
                        <p className="text-[11px] text-zinc-700 dark:text-zinc-300">
                          {reply.comment_text}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Threaded Reply Input Form */}
                {activeReplyBoxId === comment.id && (
                  <div className="mt-2 pt-2 border-t border-[#ece8df] dark:border-[#2a2824] flex items-center gap-1.5 animate-in fade-in">
                    <CornerDownRight className="w-3.5 h-3.5 text-coral-500 shrink-0" />
                    <input
                      type="text"
                      data-testid={`reply-input-${comment.id}`}
                      value={replyTextMap[comment.id] || ""}
                      onChange={(e) =>
                        setReplyTextMap((prev) => ({
                          ...prev,
                          [comment.id]: e.target.value,
                        }))
                      }
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSendReply(comment);
                        }
                      }}
                      placeholder="Viết phản hồi trao đổi..."
                      className="flex-1 px-2 py-1 text-xs bg-surface-cream dark:bg-[#252320] border border-[#d8d2c4] dark:border-[#33302b] rounded outline-none focus:border-coral-500"
                    />
                    <button
                      type="button"
                      data-testid={`send-reply-btn-${comment.id}`}
                      disabled={!replyTextMap[comment.id]?.trim() || isSubmitting}
                      onClick={() => handleSendReply(comment)}
                      className="p-1.5 rounded bg-coral-500 hover:bg-coral-600 disabled:opacity-50 text-white cursor-pointer transition-colors"
                      title="Gửi phản hồi"
                    >
                      <Send className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
