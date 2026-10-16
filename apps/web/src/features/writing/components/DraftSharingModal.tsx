import { useState, useEffect } from "react";
import {
  Share2,
  Users,
  ShieldAlert,
  Copy,
  Check,
  X,
  Loader2,
  UserPlus,
  Lock,
  Globe,
  Mail,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import type {
  DraftShareResponse,
  DraftCollaborator,
  SharePermission,
} from "../types";
import { cn } from "@/lib/utils";

export interface DraftSharingModalProps {
  isOpen?: boolean;
  onClose?: () => void;
  draftId?: string;
}

export function DraftSharingModal({
  isOpen,
  onClose,
  draftId: propDraftId,
}: DraftSharingModalProps) {
  const storeIsOpen = useWritingStore((s) => s.isShareModalOpen);
  const storeClose = useWritingStore((s) => s.closeShareModal);
  const activeDraftId = useWritingStore((s) => s.activeDraftId);

  const effectiveIsOpen = isOpen !== undefined ? isOpen : storeIsOpen;
  const effectiveClose = onClose || storeClose;
  const effectiveDraftId = propDraftId || activeDraftId;

  const [shareData, setShareData] = useState<DraftShareResponse | null>(null);
  const [collaborators, setCollaborators] = useState<DraftCollaborator[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  // Invite form state
  const [inviteEmail, setInviteEmail] = useState("");
  const [selectedRole, setSelectedRole] = useState<SharePermission>("editor");
  const [allowPublicLink, setAllowPublicLink] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  useEffect(() => {
    let ignore = false;
    if (effectiveIsOpen && effectiveDraftId) {
      draftsApi
        .getShareSettings(effectiveDraftId)
        .then((res) => {
          if (!ignore) {
            setShareData(res);
            setCollaborators(res.collaborators || []);
            setAllowPublicLink(res.allow_public_link);
            setIsLoading(false);
          }
        })
        .catch((err) => {
          if (!ignore) {
            console.error("Failed to load share settings:", err);
            setStatusMessage({
              type: "error",
              text: "Không thể tải cài đặt chia sẻ. Vui lòng thử lại sau.",
            });
            setIsLoading(false);
          }
        });
    }
    return () => {
      ignore = true;
    };
  }, [effectiveIsOpen, effectiveDraftId]);

  // Keyboard shortcut: ESC to close
  useEffect(() => {
    if (!effectiveIsOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") effectiveClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [effectiveIsOpen, effectiveClose]);

  // Invite collaborator
  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!effectiveDraftId || !inviteEmail.trim()) return;

    try {
      setIsSubmitting(true);
      setStatusMessage(null);

      const res = await draftsApi.shareDraft(effectiveDraftId, {
        target_email: inviteEmail.trim(),
        permission: selectedRole,
        allow_public_link: allowPublicLink,
      });

      setShareData(res);
      setCollaborators(res.collaborators || []);
      setInviteEmail("");
      setStatusMessage({
        type: "success",
        text: `Đã cấp quyền ${selectedRole.toUpperCase()} cho ${inviteEmail.trim()} thành công.`,
      });
    } catch (err) {
      console.error("Failed to invite collaborator:", err);
      setStatusMessage({
        type: "error",
        text: "Không thể thêm cộng tác viên. Vui lòng kiểm tra lại email.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Toggle public link
  const handleTogglePublicLink = async (checked: boolean) => {
    if (!effectiveDraftId) return;
    try {
      setIsSubmitting(true);
      const res = await draftsApi.shareDraft(effectiveDraftId, {
        allow_public_link: checked,
        permission: "viewer",
      });
      setAllowPublicLink(checked);
      setShareData(res);
      setStatusMessage({
        type: "success",
        text: checked
          ? "Đã kích hoạt liên kết chia sẻ công khai."
          : "Đã hủy kích hoạt liên kết chia sẻ công khai.",
      });
    } catch (err) {
      console.error("Failed to toggle public link:", err);
      setStatusMessage({
        type: "error",
        text: "Cập nhật liên kết công khai thất bại.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Copy share URL
  const handleCopyLink = () => {
    const url =
      shareData?.share_url ||
      `${window.location.origin}/drafts/share/${shareData?.share_token || effectiveDraftId}`;
    navigator.clipboard.writeText(url);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  if (!effectiveIsOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Chia sẻ bản thảo và phân quyền cộng tác"
      data-testid="draft-sharing-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isSubmitting) effectiveClose();
      }}
    >
      <div className="w-full max-w-2xl max-h-[85vh] bg-white dark:bg-[#181715] rounded-xl shadow-2xl border border-[#e2dcd2] dark:border-[#2e2b26] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-12 px-5 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center justify-between shrink-0 bg-[#fbf9f5] dark:bg-[#1f1d1a]">
          <div className="flex items-center gap-2">
            <Share2 className="w-4 h-4 text-coral-600 dark:text-coral-400" />
            <span className="font-semibold text-sm text-ink dark:text-zinc-100 font-anthropic-serif">
              Chia Sẻ Bản Thảo & Phân Quyền Cộng Tác
            </span>
          </div>

          <button
            type="button"
            onClick={effectiveClose}
            disabled={isSubmitting}
            aria-label="Đóng"
            className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 cursor-pointer disabled:opacity-50"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {/* Status Alert Banner */}
          {statusMessage && (
            <div
              className={cn(
                "p-3 rounded-lg text-xs flex items-center justify-between border",
                statusMessage.type === "success"
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:text-emerald-300"
                  : "bg-rose-500/10 border-rose-500/30 text-rose-800 dark:text-rose-300"
              )}
            >
              <span>{statusMessage.text}</span>
              <button
                type="button"
                onClick={() => setStatusMessage(null)}
                className="text-muted hover:text-ink ml-2"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Strict Permission Warning (Cảnh báo phân quyền nghiêm ngặt) */}
          <div
            data-testid="permission-strict-warning"
            className="p-3.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-900 dark:text-amber-200 space-y-1"
          >
            <div className="flex items-center gap-2 font-semibold text-xs text-amber-800 dark:text-amber-300">
              <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
              <span>Cảnh Báo Phân Quyền Nghiêm Ngặt</span>
            </div>
            <p className="text-[11px] leading-relaxed text-amber-800/90 dark:text-amber-300/90">
              Quyền <strong>Editor (Chỉnh sửa)</strong> cho phép người dùng thay đổi trực tiếp văn bản nghiên cứu, biên dịch lại tệp PDF và thao tác toàn bộ assets. Hãy chắc chắn bạn tin cậy địa chỉ email cộng tác viên trước khi cấp quyền.
            </p>
          </div>

          {/* Invite Form */}
          <form
            onSubmit={handleInvite}
            data-testid="invite-collaborator-form"
            className="p-3.5 rounded-lg bg-[#faf8f5] dark:bg-[#1f1d1a] border border-[#e2dcd2] dark:border-[#2e2b26] space-y-3"
          >
            <div className="flex items-center gap-1.5 font-semibold text-xs text-ink dark:text-zinc-200">
              <UserPlus className="w-4 h-4 text-coral-500" />
              <span>Mời cộng tác viên mới</span>
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
              <div className="flex-1 flex items-center gap-2 bg-white dark:bg-[#252320] px-3 py-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#2e2b26]">
                <Mail className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                <input
                  type="email"
                  required
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="nhap.email.dong.tac.gia@daihoc.edu.vn"
                  className="flex-1 text-xs bg-transparent text-ink dark:text-zinc-100 outline-none placeholder:text-zinc-400"
                  data-testid="invite-email-input"
                />
              </div>

              <select
                value={selectedRole}
                onChange={(e) =>
                  setSelectedRole(e.target.value as SharePermission)
                }
                data-testid="invite-role-select"
                className="px-3 py-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#2e2b26] bg-white dark:bg-[#252320] text-ink dark:text-zinc-100 text-xs outline-none cursor-pointer"
              >
                <option value="editor">Editor (Toàn quyền sửa)</option>
                <option value="commenter">Commenter (Nhận xét)</option>
                <option value="viewer">Viewer (Chỉ xem)</option>
              </select>

              <button
                type="submit"
                disabled={isSubmitting || !inviteEmail.trim()}
                data-testid="send-invite-btn"
                className="px-4 py-1.5 rounded-lg bg-coral-500 hover:bg-coral-600 text-white font-medium text-xs shadow-xs transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer shrink-0"
              >
                {isSubmitting ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <span>Gửi lời mời</span>
                )}
              </button>
            </div>

            {/* Role Descriptions */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[10px] text-zinc-500 dark:text-zinc-400 pt-1">
              <div
                className={cn(
                  "p-2 rounded border",
                  selectedRole === "viewer"
                    ? "border-coral-500/50 bg-coral-500/5 text-ink dark:text-zinc-200"
                    : "border-transparent"
                )}
              >
                <span className="font-semibold block text-zinc-700 dark:text-zinc-300">
                  Viewer (Chỉ xem)
                </span>
                Xem bài viết và file PDF preview đã dựng.
              </div>
              <div
                className={cn(
                  "p-2 rounded border",
                  selectedRole === "commenter"
                    ? "border-coral-500/50 bg-coral-500/5 text-ink dark:text-zinc-200"
                    : "border-transparent"
                )}
              >
                <span className="font-semibold block text-zinc-700 dark:text-zinc-300">
                  Commenter (Nhận xét)
                </span>
                Xem và bổ sung các ghi chú/yêu cầu kiểm chứng.
              </div>
              <div
                className={cn(
                  "p-2 rounded border",
                  selectedRole === "editor"
                    ? "border-coral-500/50 bg-coral-500/5 text-ink dark:text-zinc-200"
                    : "border-transparent"
                )}
              >
                <span className="font-semibold block text-zinc-700 dark:text-zinc-300">
                  Editor (Toàn quyền)
                </span>
                Sửa trực tiếp mã nguồn LaTeX & biên dịch.
              </div>
            </div>
          </form>

          {/* Public Link Sharing Toggle */}
          <div
            data-testid="public-share-section"
            className="p-3.5 rounded-lg bg-[#faf8f5] dark:bg-[#1f1d1a] border border-[#e2dcd2] dark:border-[#2e2b26] space-y-2.5"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <div>
                  <div className="font-semibold text-xs text-ink dark:text-zinc-200">
                    Chia sẻ qua liên kết công khai
                  </div>
                  <div className="text-[11px] text-muted dark:text-zinc-400">
                    Bất kỳ ai có đường link đều có thể xem bài viết mà không cần đăng nhập
                  </div>
                </div>
              </div>

              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowPublicLink}
                  onChange={(e) => handleTogglePublicLink(e.target.checked)}
                  data-testid="public-link-toggle"
                  className="sr-only peer"
                />
                <div className="w-9 h-5 bg-zinc-300 peer-focus:outline-none rounded-full peer dark:bg-zinc-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-zinc-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-coral-500"></div>
              </label>
            </div>

            {allowPublicLink && (
              <div className="flex items-center gap-2 pt-1 animate-in fade-in">
                <input
                  type="text"
                  readOnly
                  value={
                    shareData?.share_url ||
                    `${window.location.origin}/drafts/share/${shareData?.share_token || effectiveDraftId}`
                  }
                  data-testid="public-link-input"
                  className="flex-1 text-xs px-2.5 py-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#2e2b26] bg-white dark:bg-[#252320] text-zinc-700 dark:text-zinc-300 font-mono outline-none"
                />
                <button
                  type="button"
                  onClick={handleCopyLink}
                  data-testid="copy-link-btn"
                  className={cn(
                    "px-3 py-1.5 rounded-lg border text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer shrink-0",
                    isCopied
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-400"
                      : "bg-white dark:bg-[#252320] border-[#e2dcd2] dark:border-[#2e2b26] text-ink dark:text-zinc-200 hover:bg-[#ece8df] dark:hover:bg-[#2d2a26]"
                  )}
                >
                  {isCopied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Đã sao chép</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Sao chép link</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Collaborator List */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-ink dark:text-zinc-200">
              <div className="flex items-center gap-1.5">
                <Users className="w-4 h-4 text-coral-500" />
                <span>Danh sách cộng tác viên ({collaborators.length})</span>
              </div>
            </div>

            {isLoading ? (
              <div className="py-8 flex flex-col items-center justify-center text-zinc-400 space-y-2">
                <Loader2 className="w-5 h-5 animate-spin text-coral-500" />
                <span>Đang tải thông tin cộng tác viên...</span>
              </div>
            ) : collaborators.length > 0 ? (
              <div
                className="space-y-1.5 divide-y divide-[#ece8df] dark:divide-[#2a2824] border border-[#e2dcd2] dark:border-[#2e2b26] rounded-lg overflow-hidden bg-white dark:bg-[#1a1917]"
                data-testid="collaborators-list"
              >
                {collaborators.map((c, idx) => {
                  const isEditor = c.permission === "editor" || c.permission === "edit";
                  const isCommenter = c.permission === "commenter" || c.permission === "comment";

                  return (
                    <div
                      key={idx}
                      data-testid="collaborator-item"
                      className="px-3.5 py-2.5 flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className="w-7 h-7 rounded-full bg-zinc-200 dark:bg-zinc-800 flex items-center justify-center text-[11px] font-semibold text-zinc-700 dark:text-zinc-300 uppercase shrink-0">
                          {c.email.charAt(0)}
                        </div>
                        <div className="min-w-0">
                          <div className="font-medium text-ink dark:text-zinc-100 truncate">
                            {c.email}
                          </div>
                          {c.granted_at && (
                            <div className="text-[10px] text-zinc-400">
                              Cấp quyền lúc:{" "}
                              {new Date(c.granted_at).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            "px-2 py-0.5 rounded-full text-[10px] font-semibold",
                            isEditor &&
                              "bg-emerald-500/15 text-emerald-800 dark:text-emerald-300",
                            isCommenter &&
                              "bg-blue-500/15 text-blue-800 dark:text-blue-300",
                            !isEditor &&
                              !isCommenter &&
                              "bg-zinc-200/60 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400"
                          )}
                        >
                          {c.permission.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-6 rounded-lg border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] text-center text-xs text-muted dark:text-zinc-400">
                Chưa có cộng tác viên nào được mời. Nhập email ở trên để bắt đầu hợp tác.
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="h-12 px-5 border-t border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1f1d1a] flex items-center justify-between shrink-0 text-[11px] text-zinc-400">
          <div className="flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-zinc-400" />
            <span>Mã hóa bảo vệ phiên bản cộng tác thời gian thực</span>
          </div>

          <button
            type="button"
            onClick={effectiveClose}
            className="px-3 py-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#2e2b26] bg-white dark:bg-[#252320] text-ink dark:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5 font-medium cursor-pointer"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
}
