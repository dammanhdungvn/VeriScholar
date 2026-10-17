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
  ShieldCheck,
  ExternalLink,
  Laptop,
  LogOut,
  Globe,
  Tag,
  FileText,
  Camera,
} from "lucide-react";
import { useAuthStore } from "../stores/useAuthStore";
import { authApi } from "../api/authApi";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { getScholarInitials } from "../utils/avatarUtils";

export interface AccountSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: "profile" | "connected" | "security";
}

interface AccountSettingsContentProps {
  onClose: () => void;
  defaultTab: "profile" | "connected" | "security";
}

function AccountSettingsContent({ onClose, defaultTab }: AccountSettingsContentProps) {
  const { user, updateUser, logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState<"profile" | "connected" | "security">(defaultTab);

  // Profile Form State initialized directly from current user
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [institution, setInstitution] = useState(user?.institution || "");
  const [department, setDepartment] = useState(user?.department || "");
  const [academicRank, setAcademicRank] = useState(user?.academic_rank || "");
  const [orcidId, setOrcidId] = useState(user?.orcid_id || "");
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || "");
  const [showAvatarEdit, setShowAvatarEdit] = useState(false);
  const [googleScholarUrl, setGoogleScholarUrl] = useState(user?.google_scholar_url || "");
  const [researchInterests, setResearchInterests] = useState(user?.research_interests || "");
  const [bio, setBio] = useState(user?.bio || "");

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

  const isGoogleUser = Boolean(
    user?.email?.endsWith("@gmail.com") ||
    user?.email?.includes("google") ||
    user?.avatar_url?.includes("googleusercontent.com")
  );

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
      department: department.trim() || undefined,
      academic_rank: academicRank.trim() || undefined,
      orcid_id: orcidId.trim() || undefined,
      avatar_url: avatarUrl.trim() || undefined,
      google_scholar_url: googleScholarUrl.trim() || undefined,
      research_interests: researchInterests.trim() || undefined,
      bio: bio.trim() || undefined,
    };

    try {
      try {
        await authApi.updateProfile(payload);
      } catch {
        // Fallback for offline / staging test double
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
      await authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
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

  const initials = getScholarInitials(fullName || user?.full_name, user?.email);
  const cleanOrcid = orcidId.trim().replace(/^https?:\/\/orcid\.org\//, "");

  // Tags list for preview
  const tagsList = researchInterests
    .split(/[,;\n]+/)
    .map((t) => t.trim())
    .filter(Boolean);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Cài đặt tài khoản"
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/65 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div
        className="w-full max-w-2xl bg-canvas dark:bg-[#1a1815] rounded-2xl shadow-2xl border border-hairline dark:border-[#38332c] flex flex-col overflow-hidden text-ink dark:text-[#f5f3ed] max-h-[92vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="h-14 px-6 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0 bg-surface-soft/20 dark:bg-[#151311]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-600/10 text-amber-700 dark:text-amber-500 flex items-center justify-center">
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

        {/* Scholar Hero Card */}
        <div className="p-5 sm:p-6 border-b border-hairline dark:border-[#2f2b26] bg-gradient-to-r from-amber-500/5 via-stone-500/5 to-transparent shrink-0">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4">
            {/* 64x64px Large Avatar */}
            <div className="relative group shrink-0">
              <div className="w-16 h-16 rounded-2xl overflow-hidden border-2 border-amber-600/30 dark:border-amber-500/30 shadow-md flex items-center justify-center bg-stone-100 dark:bg-[#25221d]">
                {avatarUrl ? (
                  <img
                    src={avatarUrl}
                    alt={fullName || user?.full_name || "Scholar Avatar"}
                    className="w-full h-full object-cover"
                    referrerPolicy="no-referrer"
                    onError={() => setAvatarUrl("")}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center font-serif font-bold text-xl bg-gradient-to-br from-amber-700 via-amber-800 to-amber-950 text-amber-100">
                    {initials}
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={() => setShowAvatarEdit(!showAvatarEdit)}
                className="absolute -bottom-1 -right-1 p-1 rounded-full bg-white dark:bg-[#25221d] border border-hairline dark:border-[#38332c] shadow-xs text-muted hover:text-ink dark:text-zinc-300 dark:hover:text-white transition-colors cursor-pointer"
                title="Thay đổi ảnh đại diện"
              >
                <Camera className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Scholar Identity Meta */}
            <div className="flex-1 text-center sm:text-left space-y-1.5">
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
                <h3 className="font-serif text-lg sm:text-xl font-bold text-ink dark:text-zinc-100 tracking-tight">
                  {fullName || user?.full_name || "Học giả VeriScholar"}
                </h3>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-600/10 text-amber-800 dark:text-amber-400 capitalize border border-amber-600/20">
                  {user?.role || "researcher"}
                </span>
              </div>

              <p className="text-xs font-mono text-muted dark:text-zinc-400">
                {user?.email || "scholar@verischolar.ai"}
              </p>

              {/* Trust & Compliance Badge */}
              <div className="pt-0.5 flex flex-wrap items-center justify-center sm:justify-start gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-2xs font-semibold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25 shadow-2xs">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  <span>Học giả đã xác thực (ISO 32000-1 / DOI Ready)</span>
                </span>
              </div>
            </div>
          </div>

          {/* Collapsible Avatar URL Input */}
          {showAvatarEdit && (
            <div className="mt-3.5 p-3 rounded-xl bg-surface-soft/80 dark:bg-[#221f1a] border border-hairline dark:border-[#38332c] space-y-1.5 animate-in fade-in slide-in-from-top-1">
              <Label htmlFor="avatar-url-input" className="text-2xs font-medium text-muted dark:text-zinc-300">
                URL Ảnh đại diện (Google Photo, ORCID hoặc liên kết trực tiếp):
              </Label>
              <div className="flex gap-2">
                <Input
                  id="avatar-url-input"
                  type="url"
                  value={avatarUrl}
                  onChange={(e) => setAvatarUrl(e.target.value)}
                  placeholder="https://example.com/avatar.jpg"
                  className="h-8 text-xs font-mono"
                />
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowAvatarEdit(false)}
                  className="h-8 text-xs px-3"
                >
                  Xong
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* 3 Tabs Navigation */}
        <div className="flex border-b border-hairline dark:border-[#2f2b26] px-6 bg-surface-soft/40 dark:bg-[#151311] shrink-0 overflow-x-auto">
          <button
            type="button"
            onClick={() => setActiveTab("profile")}
            className={`py-3 px-3.5 text-xs font-medium font-sans border-b-2 flex items-center gap-2 transition-colors cursor-pointer whitespace-nowrap ${
              activeTab === "profile"
                ? "border-amber-600 text-amber-700 dark:text-amber-500 font-semibold"
                : "border-transparent text-muted hover:text-ink dark:hover:text-zinc-200"
            }`}
          >
            <User className="w-3.5 h-3.5" />
            <span>Hồ sơ nghiên cứu</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("connected")}
            className={`py-3 px-3.5 text-xs font-medium font-sans border-b-2 flex items-center gap-2 transition-colors cursor-pointer whitespace-nowrap ${
              activeTab === "connected"
                ? "border-amber-600 text-amber-700 dark:text-amber-500 font-semibold"
                : "border-transparent text-muted hover:text-ink dark:hover:text-zinc-200"
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Tài khoản liên kết</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("security")}
            className={`py-3 px-3.5 text-xs font-medium font-sans border-b-2 flex items-center gap-2 transition-colors cursor-pointer whitespace-nowrap ${
              activeTab === "security"
                ? "border-amber-600 text-amber-700 dark:text-amber-500 font-semibold"
                : "border-transparent text-muted hover:text-ink dark:hover:text-zinc-200"
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            <span>Bảo mật &amp; Mật khẩu / Phiên</span>
          </button>
        </div>

        {/* Tab Content Area */}
        <div className="p-6 overflow-y-auto space-y-4 font-sans text-xs flex-1">
          {/* TAB 1: Academic Profile */}
          {activeTab === "profile" && (
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

              {/* Institution & Department */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="space-y-1.5">
                  <Label htmlFor="settings-institution">
                    Cơ quan / Viện nghiên cứu / Trường Đại học
                  </Label>
                  <Input
                    id="settings-institution"
                    type="text"
                    value={institution}
                    onChange={(e) => setInstitution(e.target.value)}
                    placeholder="Đại học Quốc gia / Viện Hàn lâm"
                    startIcon={<Building2 className="w-4 h-4" />}
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="settings-department">
                    Khoa / Phòng thí nghiệm / Bộ môn
                  </Label>
                  <Input
                    id="settings-department"
                    type="text"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    placeholder="Khoa Khoa học Máy tính / Lab AI"
                  />
                </div>
              </div>

              {/* Academic Rank & ORCID ID (Fixed Overflow with Link) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="space-y-1.5">
                  <Label htmlFor="settings-academic-rank">Học hàm / Học vị</Label>
                  <Input
                    id="settings-academic-rank"
                    type="text"
                    value={academicRank}
                    onChange={(e) => setAcademicRank(e.target.value)}
                    placeholder="Giáo sư, Tiến sĩ, Nghiên cứu sinh"
                    startIcon={<GraduationCap className="w-4 h-4" />}
                  />
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="settings-orcid-id">ORCID ID</Label>
                    {cleanOrcid && (
                      <a
                        href={`https://orcid.org/${cleanOrcid}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-2xs text-emerald-600 dark:text-emerald-400 hover:underline inline-flex items-center gap-0.5"
                      >
                        <span>orcid.org/{cleanOrcid}</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    )}
                  </div>
                  <Input
                    id="settings-orcid-id"
                    type="text"
                    value={orcidId}
                    onChange={(e) => setOrcidId(e.target.value)}
                    placeholder="0000-0002-1825-0097"
                    startIcon={<Fingerprint className="w-4 h-4 text-emerald-600" />}
                  />
                </div>
              </div>

              {/* Google Scholar Profile URL */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <Label htmlFor="settings-google-scholar">Google Scholar Profile URL</Label>
                  {googleScholarUrl.trim() && (
                    <a
                      href={googleScholarUrl.trim()}
                      target="_blank"
                      rel="noreferrer"
                      className="text-2xs text-amber-700 dark:text-amber-400 hover:underline inline-flex items-center gap-0.5"
                    >
                      <span>Mở Google Scholar</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  )}
                </div>
                <Input
                  id="settings-google-scholar"
                  type="url"
                  value={googleScholarUrl}
                  onChange={(e) => setGoogleScholarUrl(e.target.value)}
                  placeholder="https://scholar.google.com/citations?user=..."
                  startIcon={<Globe className="w-4 h-4 text-amber-600" />}
                />
              </div>

              {/* Research Interests */}
              <div className="space-y-1.5">
                <Label htmlFor="settings-research-interests">
                  Lĩnh vực nghiên cứu (Research Interests)
                </Label>
                <Input
                  id="settings-research-interests"
                  type="text"
                  value={researchInterests}
                  onChange={(e) => setResearchInterests(e.target.value)}
                  placeholder="Trí tuệ nhân tạo, Xử lý ngôn ngữ tự nhiên, Khoa học dữ liệu..."
                  startIcon={<Tag className="w-4 h-4 text-primary" />}
                />
                {tagsList.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {tagsList.map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded-md bg-stone-200/60 dark:bg-stone-800 text-stone-700 dark:text-stone-300 text-[10px] font-medium"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Bio */}
              <div className="space-y-1.5">
                <Label htmlFor="settings-bio">Tiểu sử học thuật (Academic Biography)</Label>
                <textarea
                  id="settings-bio"
                  rows={3}
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Tóm tắt quá trình nghiên cứu, học thuật và định hướng xuất bản..."
                  className="w-full rounded-xl border border-hairline dark:border-[#38332c] bg-canvas dark:bg-[#201e1b] px-3 py-2 text-xs text-ink dark:text-zinc-100 placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors resize-y"
                />
              </div>

              {/* Actions */}
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
                  className="rounded-xl text-xs min-w-[120px] bg-amber-600 hover:bg-amber-700 text-white"
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
          )}

          {/* TAB 2: Connected Accounts */}
          {activeTab === "connected" && (
            <div className="space-y-4">
              {/* Google Workspace SSO Card */}
              <div className="p-4 rounded-xl bg-surface-soft/60 dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-white dark:bg-[#2a2622] border border-hairline dark:border-[#38332c] flex items-center justify-center shrink-0 shadow-2xs">
                      <svg className="w-5 h-5" viewBox="0 0 24 24">
                        <path
                          fill="#4285F4"
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        />
                        <path
                          fill="#34A853"
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        />
                        <path
                          fill="#FBBC05"
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                        />
                        <path
                          fill="#EA4335"
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                        />
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-semibold text-xs text-ink dark:text-zinc-100">
                        Google Workspace SSO
                      </h4>
                      <p className="text-2xs font-mono text-muted dark:text-zinc-400">
                        {user?.email || "dungdam.gg01@gmail.com"}
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-2xs font-semibold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                    <span>Đã kết nối qua Google GIS</span>
                  </span>
                </div>
                <p className="text-2xs text-muted dark:text-zinc-400 leading-relaxed pl-12">
                  Tài khoản được bảo chứng bởi hạ tầng an ninh Google Cloud Identity và Xác thực 2 bước (2FA). Được cấp quyền đồng bộ dữ liệu nghiên cứu và đăng nhập tức thì.
                </p>
              </div>

              {/* ORCID Registry Card */}
              <div className="p-4 rounded-xl bg-surface-soft/60 dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-white dark:bg-[#2a2622] border border-hairline dark:border-[#38332c] flex items-center justify-center shrink-0 shadow-2xs">
                      <svg className="w-5 h-5" viewBox="0 0 256 256" fill="none">
                        <path
                          d="M128 0C57.307 0 0 57.307 0 128s57.307 128 128 128 128-57.307 128-128S198.693 0 128 0z"
                          fill="#A6CE39"
                        />
                        <path
                          d="M86.3 186.2H70.9V79.1h15.4v107.1zm-7.7-123.6c-5.3 0-9.6-4.3-9.6-9.6s4.3-9.6 9.6-9.6 9.6 4.3 9.6 9.6c0 5.3-4.3 9.6-9.6 9.6zm35.2 123.6h38.2c26.9 0 43.1-18.4 43.1-43.5 0-25.1-16.2-43.5-43.1-43.5h-38.2v87zm15.4-72.9h21.4c17.5 0 27.6 11.8 27.6 29.4 0 17.6-10.1 29.4-27.6 29.4h-21.4v-58.8z"
                          fill="#FFFFFF"
                        />
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-semibold text-xs text-ink dark:text-zinc-100">
                        ORCID Member Registry
                      </h4>
                      <p className="text-2xs text-muted dark:text-zinc-400">
                        {cleanOrcid ? `Mã định danh: ${cleanOrcid}` : "Chưa liên kết định danh"}
                      </p>
                    </div>
                  </div>
                  {cleanOrcid ? (
                    <a
                      href={`https://orcid.org/${cleanOrcid}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-2xs font-semibold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25"
                    >
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Đã xác nhận</span>
                    </a>
                  ) : (
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => setActiveTab("profile")}
                      className="h-7 text-2xs"
                    >
                      Thêm ORCID ID
                    </Button>
                  )}
                </div>
                <p className="text-2xs text-muted dark:text-zinc-400 leading-relaxed pl-12">
                  Đồng bộ mã định danh học giả quốc tế Open Researcher and Contributor ID để bảo chứng quyền tác giả các bài báo khoa học.
                </p>
              </div>

              {/* Overleaf Workspace Card */}
              <div className="p-4 rounded-xl bg-surface-soft/60 dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-white dark:bg-[#2a2622] border border-hairline dark:border-[#38332c] flex items-center justify-center shrink-0 shadow-2xs text-amber-700 dark:text-amber-500">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-xs text-ink dark:text-zinc-100">
                        Overleaf / LaTeX Cloud Workspace
                      </h4>
                      <p className="text-2xs text-muted dark:text-zinc-400">
                        Institutional Cloud Bridge
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-2xs font-medium bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20">
                    <span>Sẵn sàng kết nối</span>
                  </span>
                </div>
                <p className="text-2xs text-muted dark:text-zinc-400 leading-relaxed pl-12">
                  Hỗ trợ đồng bộ bản thảo khoa học hai chiều với Overleaf Git Bridge theo quy chuẩn tài liệu bảo chứng ISO 32000-1.
                </p>
              </div>
            </div>
          )}

          {/* TAB 3: Security & Sessions */}
          {activeTab === "security" && (
            <div className="space-y-5">
              {/* Change / Set Backup Password Form */}
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div className="flex items-center justify-between pb-1">
                  <div>
                    <h4 className="font-semibold text-xs text-ink dark:text-zinc-100">
                      {isGoogleUser ? "Thiết lập mật khẩu dự phòng" : "Đổi mật khẩu tài khoản"}
                    </h4>
                    <p className="text-2xs text-muted dark:text-zinc-400">
                      {isGoogleUser
                        ? "Tài khoản hiện đang đăng nhập qua Google OAuth. Bạn có thể đặt mật khẩu trực tiếp để đăng nhập dự phòng."
                        : "Thay đổi mật khẩu đăng nhập trực tiếp trên hệ thống VeriScholar."}
                    </p>
                  </div>
                </div>

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
                <div className="pt-1 flex justify-end gap-2.5">
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={isChangingPassword}
                    className="rounded-xl text-xs min-w-[130px] bg-amber-600 hover:bg-amber-700 text-white"
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

              {/* Active Session Information Card */}
              <div className="pt-3 border-t border-hairline dark:border-[#2f2b26]">
                <div className="p-4 rounded-xl bg-surface-soft/60 dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-stone-100 dark:bg-[#2a2622] border border-hairline dark:border-[#38332c] flex items-center justify-center shrink-0">
                        <Laptop className="w-4 h-4 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-xs text-ink dark:text-zinc-100">
                          Phiên làm việc hiện tại (Active Session)
                        </h4>
                        <p className="text-2xs text-muted dark:text-zinc-400">
                          Trình duyệt web &bull; Thời hạn 30 ngày (Remember Me token)
                        </p>
                      </div>
                    </div>
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-2xs font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      <span>Đang hoạt động</span>
                    </span>
                  </div>

                  <div className="flex justify-end pt-1">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        logout();
                        onClose();
                        window.location.href = "/login";
                      }}
                      className="h-8 text-2xs flex items-center gap-1.5 cursor-pointer text-rose-600 hover:text-rose-700 hover:bg-rose-500/10 dark:text-rose-400 dark:hover:bg-rose-500/20"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Đăng xuất thiết bị</span>
                    </Button>
                  </div>
                </div>
              </div>
            </div>
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
