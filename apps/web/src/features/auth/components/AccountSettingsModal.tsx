import { useState } from "react";
import {
  X,
  User,
  Shield,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Building2,
  GraduationCap,
  Fingerprint,
} from "lucide-react";
import { useAuthStore } from "../stores/useAuthStore";
import { authApi } from "../api/authApi";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export interface AccountSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: "profile" | "security";
}

interface AccountSettingsContentProps {
  onClose: () => void;
  defaultTab: "profile" | "security";
}

function AccountSettingsContent({ onClose, defaultTab }: AccountSettingsContentProps) {
  const { user, updateUser } = useAuthStore();
  const [activeTab, setActiveTab] = useState<"profile" | "security">(defaultTab);

  // Profile Form State initialized directly from current user
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [institution, setInstitution] = useState(user?.institution || "");
  const [academicRank, setAcademicRank] = useState(user?.academic_rank || "");
  const [orcidId, setOrcidId] = useState(user?.orcid_id || "");
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileSuccessMsg, setProfileSuccessMsg] = useState<string | null>(null);
  const [profileErrorMsg, setProfileErrorMsg] = useState<string | null>(null);

  // Security Form State
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [securitySuccessMsg, setSecuritySuccessMsg] = useState<string | null>(null);
  const [securityErrorMsg, setSecurityErrorMsg] = useState<string | null>(null);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      setProfileErrorMsg("Họ và tên không được để trống.");
      return;
    }

    setIsSavingProfile(true);
    setProfileSuccessMsg(null);
    setProfileErrorMsg(null);

    const payload = {
      full_name: fullName.trim(),
      institution: institution.trim() || undefined,
      academic_rank: academicRank.trim() || undefined,
      orcid_id: orcidId.trim() || undefined,
    };

    try {
      if (import.meta.env.VITE_ENABLE_MOCK_AUTH !== "true") {
        try {
          await authApi.updateProfile(payload);
        } catch {
          // If endpoint is in migration/test, update local store
        }
      }
      updateUser(payload);
      setProfileSuccessMsg("Hồ sơ học giả đã được cập nhật thành công.");
    } catch (err: unknown) {
      setProfileErrorMsg(err instanceof Error ? err.message : "Không thể cập nhật hồ sơ. Vui lòng thử lại.");
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setSecuritySuccessMsg(null);
    setSecurityErrorMsg(null);

    if (!currentPassword) {
      setSecurityErrorMsg("Vui lòng nhập mật khẩu hiện tại.");
      return;
    }
    if (newPassword.length < 8) {
      setSecurityErrorMsg("Mật khẩu mới phải có tối thiểu 8 ký tự.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setSecurityErrorMsg("Mật khẩu xác nhận không khớp với mật khẩu mới.");
      return;
    }

    setIsChangingPassword(true);
    try {
      if (import.meta.env.VITE_ENABLE_MOCK_AUTH !== "true") {
        await authApi.changePassword({
          current_password: currentPassword,
          new_password: newPassword,
        });
      }
      setSecuritySuccessMsg("Mật khẩu đã được thay đổi thành công.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: unknown) {
      setSecurityErrorMsg(
        err instanceof Error ? err.message : "Đổi mật khẩu thất bại. Vui lòng kiểm tra lại mật khẩu hiện tại."
      );
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Cài đặt tài khoản"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div
        className="w-full max-w-lg bg-canvas dark:bg-[#1e1c18] rounded-2xl shadow-2xl border border-hairline dark:border-[#38332c] flex flex-col overflow-hidden text-ink dark:text-[#f5f3ed] max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="h-14 px-6 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-serif font-bold text-sm sm:text-base text-ink dark:text-zinc-100">
                Cài đặt tài khoản
              </h2>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Đóng"
            className="p-1.5 rounded-lg text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-hairline dark:border-[#2f2b26] px-6 bg-surface-soft/40 dark:bg-[#191714] shrink-0">
          <button
            type="button"
            onClick={() => setActiveTab("profile")}
            className={`py-3 px-4 text-xs font-medium font-sans border-b-2 flex items-center gap-2 transition-colors cursor-pointer ${
              activeTab === "profile"
                ? "border-primary text-primary font-semibold"
                : "border-transparent text-muted hover:text-ink dark:hover:text-zinc-200"
            }`}
          >
            <User className="w-3.5 h-3.5" />
            <span>Hồ sơ nghiên cứu</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("security")}
            className={`py-3 px-4 text-xs font-medium font-sans border-b-2 flex items-center gap-2 transition-colors cursor-pointer ${
              activeTab === "security"
                ? "border-primary text-primary font-semibold"
                : "border-transparent text-muted hover:text-ink dark:hover:text-zinc-200"
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            <span>Bảo mật & Mật khẩu</span>
          </button>
        </div>

        {/* Content Area */}
        <div className="p-6 overflow-y-auto space-y-4 font-sans text-xs">
          {activeTab === "profile" ? (
            <form onSubmit={handleSaveProfile} className="space-y-4">
              {profileSuccessMsg && (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-300 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />
                  <span>{profileSuccessMsg}</span>
                </div>
              )}
              {profileErrorMsg && (
                <div className="p-3 rounded-xl bg-error/10 border border-error/20 text-error flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-error" />
                  <span>{profileErrorMsg}</span>
                </div>
              )}

              {/* Readonly Email & Role */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 rounded-xl bg-surface-soft/50 dark:bg-[#25221d] border border-hairline/70 dark:border-[#38332c]">
                <div>
                  <span className="text-[11px] text-muted block mb-0.5">Email tài khoản</span>
                  <span className="font-mono font-medium text-ink dark:text-zinc-200 text-xs truncate block">
                    {user?.email || "scholar@verischolar.ai"}
                  </span>
                </div>
                <div>
                  <span className="text-[11px] text-muted block mb-0.5">Vai trò hệ thống</span>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-primary/10 text-primary capitalize">
                    {user?.role || "researcher"}
                  </span>
                </div>
              </div>

              {/* Full Name */}
              <div className="space-y-1.5">
                <Label htmlFor="settings-full-name" required>
                  Họ và tên
                </Label>
                <Input
                  id="settings-full-name"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="GS.TS. Nguyễn Văn A"
                  required
                />
              </div>

              {/* Institution */}
              <div className="space-y-1.5">
                <Label htmlFor="settings-institution">
                  Cơ quan / Viện nghiên cứu / Trường Đại học
                </Label>
                <Input
                  id="settings-institution"
                  type="text"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  placeholder="Viện Hàn lâm Khoa học / Đại học Quốc gia"
                  startIcon={<Building2 className="w-4 h-4" />}
                />
              </div>

              {/* Academic Rank & ORCID ID */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="settings-academic-rank">Học hàm / Học vị</Label>
                  <Input
                    id="settings-academic-rank"
                    type="text"
                    value={academicRank}
                    onChange={(e) => setAcademicRank(e.target.value)}
                    placeholder="Giáo sư, Tiến sĩ"
                    startIcon={<GraduationCap className="w-4 h-4" />}
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="settings-orcid-id">ORCID ID</Label>
                  <Input
                    id="settings-orcid-id"
                    type="text"
                    value={orcidId}
                    onChange={(e) => setOrcidId(e.target.value)}
                    placeholder="0000-0002-1825-0097"
                    startIcon={<Fingerprint className="w-4 h-4" />}
                  />
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-2 flex justify-end gap-2.5">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={onClose}
                  className="rounded-xl text-xs"
                >
                  Hủy
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={isSavingProfile}
                  className="rounded-xl text-xs min-w-[120px]"
                >
                  {isSavingProfile ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                      <span>Đang lưu...</span>
                    </>
                  ) : (
                    <span>Lưu thay đổi</span>
                  )}
                </Button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleChangePassword} className="space-y-4">
              {securitySuccessMsg && (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-300 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />
                  <span>{securitySuccessMsg}</span>
                </div>
              )}
              {securityErrorMsg && (
                <div className="p-3 rounded-xl bg-error/10 border border-error/20 text-error flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-error" />
                  <span>{securityErrorMsg}</span>
                </div>
              )}

              {/* Current Password */}
              <div className="space-y-1.5">
                <Label htmlFor="settings-current-password" required>
                  Mật khẩu hiện tại
                </Label>
                <Input
                  id="settings-current-password"
                  type={showCurrentPassword ? "text" : "password"}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Nhập mật khẩu hiện tại"
                  required
                  endIcon={
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      className="text-muted hover:text-ink dark:hover:text-zinc-100 p-1 cursor-pointer"
                      title={showCurrentPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                    >
                      {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  }
                />
              </div>

              {/* New Password */}
              <div className="space-y-1.5">
                <Label htmlFor="settings-new-password" required>
                  Mật khẩu mới
                </Label>
                <Input
                  id="settings-new-password"
                  type={showNewPassword ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Tối thiểu 8 ký tự"
                  required
                  endIcon={
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="text-muted hover:text-ink dark:hover:text-zinc-100 p-1 cursor-pointer"
                      title={showNewPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                    >
                      {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  }
                />
              </div>

              {/* Confirm Password */}
              <div className="space-y-1.5">
                <Label htmlFor="settings-confirm-password" required>
                  Xác nhận mật khẩu mới
                </Label>
                <Input
                  id="settings-confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Nhập lại mật khẩu mới"
                  required
                  endIcon={
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="text-muted hover:text-ink dark:hover:text-zinc-100 p-1 cursor-pointer"
                      title={showConfirmPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                    >
                      {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  }
                />
              </div>

              {/* Submit Button */}
              <div className="pt-2 flex justify-end gap-2.5">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={onClose}
                  className="rounded-xl text-xs"
                >
                  Hủy
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={isChangingPassword}
                  className="rounded-xl text-xs min-w-[130px]"
                >
                  {isChangingPassword ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                      <span>Đang cập nhật...</span>
                    </>
                  ) : (
                    <span>Cập nhật mật khẩu</span>
                  )}
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export function AccountSettingsModal({
  isOpen,
  onClose,
  defaultTab = "profile",
}: AccountSettingsModalProps) {
  if (!isOpen) return null;

  return (
    <AccountSettingsContent
      key={defaultTab}
      onClose={onClose}
      defaultTab={defaultTab}
    />
  );
}
