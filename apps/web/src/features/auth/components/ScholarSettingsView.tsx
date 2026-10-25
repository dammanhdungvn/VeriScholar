import React, { useState, useEffect } from "react";
import {
  User,
  Shield,
  Palette,
  KeyRound,
  Sun,
  Moon,
  Monitor,
  Building2,
  GraduationCap,
  Fingerprint,
  Globe,
  Tag,
  Laptop,
  LogOut,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Camera,
  X,
  Trash2,
} from "lucide-react";
import { authApi } from "@/features/auth/api/authApi";
import { useAuthStore, applyThemePreference } from "@/features/auth/stores/useAuthStore";
import { useTheme } from "@/hooks/useTheme";
import { getScholarInitials } from "@/features/auth/utils/avatarUtils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import type { ThemePreference, UserProfile } from "@/types/auth";

export const ORCID_REGEX = /^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/;

export function validateOrcidId(orcid?: string | null): boolean {
  if (!orcid || !orcid.trim()) return true;
  return ORCID_REGEX.test(orcid.trim());
}

export function maskClientApiKey(rawKey: string): string {
  const trimmed = rawKey.trim();
  if (!trimmed) return "";
  const last4 = trimmed.slice(-4);
  if (trimmed.startsWith("sk-proj-")) {
    return `sk-proj-...${last4}`;
  }
  return `sk-...${last4}`;
}

export interface ScholarUser {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  institution?: string | null;
  department?: string | null;
  academic_rank?: string | null;
  orcid_id?: string | null;
  google_scholar_url?: string | null;
  research_interests?: string | null;
  bio?: string | null;
  has_byok?: boolean;
  byok_masked?: string | null;
  theme_preference?: "light" | "dark" | "system";
}

export interface ScholarSettingsViewProps {
  variant?: "page" | "dialog";
  defaultTab?: "profile" | "security" | "appearance";
  onClose?: () => void;
  user?: ScholarUser | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onUpdated?: (updatedUser: any) => void;
}

export function ScholarSettingsView({
  variant = "page",
  defaultTab = "profile",
  onClose,
  user,
  onUpdated,
}: ScholarSettingsViewProps) {
  const storeUser = useAuthStore((s) => s.user);
  const updateStoreUser = useAuthStore((s) => s.updateUser);
  const setStoreTheme = useAuthStore((s) => s.setTheme);
  const logout = useAuthStore((s) => s.logout);
  const { setTheme: setGlobalTheme } = useTheme();

  const effectiveUser = user ?? storeUser;

  const [activeTab, setActiveTab] = useState<"profile" | "security" | "appearance">(defaultTab);

  // Tab 1: Profile State
  const [fullName, setFullName] = useState(effectiveUser?.full_name || "");
  const [institution, setInstitution] = useState(effectiveUser?.institution || "");
  const [department, setDepartment] = useState(effectiveUser?.department || "");
  const [academicRank, setAcademicRank] = useState(effectiveUser?.academic_rank || "");
  const [orcidId, setOrcidId] = useState(effectiveUser?.orcid_id || "");
  const [avatarUrl, setAvatarUrl] = useState(effectiveUser?.avatar_url || "");
  const [showAvatarEdit, setShowAvatarEdit] = useState(false);
  const [googleScholarUrl, setGoogleScholarUrl] = useState(effectiveUser?.google_scholar_url || "");
  const [researchInterests, setResearchInterests] = useState(effectiveUser?.research_interests || "");
  const [bio, setBio] = useState(effectiveUser?.bio || "");

  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileSuccessMsg, setProfileSuccessMsg] = useState<string | null>(null);
  const [profileErrorMsg, setProfileErrorMsg] = useState<string | null>(null);

  // Tab 2: Security & BYOK State
  const [hasByok, setHasByok] = useState<boolean>(!!effectiveUser?.has_byok);
  const [byokMasked, setByokMasked] = useState<string | null>(effectiveUser?.byok_masked || null);
  const [byokApiKey, setByokApiKey] = useState("");
  const [showByokInput, setShowByokInput] = useState(false);
  const [showApiKeyText, setShowApiKeyText] = useState(false);
  const [isSavingByok, setIsSavingByok] = useState(false);
  const [isDeletingByok, setIsDeletingByok] = useState(false);
  const [byokSuccess, setByokSuccess] = useState<string | null>(null);
  const [byokError, setByokError] = useState<string | null>(null);

  // Password State
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordSuccessMsg, setPasswordSuccessMsg] = useState<string | null>(null);
  const [passwordErrorMsg, setPasswordErrorMsg] = useState<string | null>(null);

  // Tab 3: Appearance State
  const [themePreference, setThemePreference] = useState<ThemePreference>(
    effectiveUser?.theme_preference || "system"
  );
  const [themeSuccessMsg, setThemeSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    if (effectiveUser) {
      setFullName(effectiveUser.full_name || "");
      setInstitution(effectiveUser.institution || "");
      setDepartment(effectiveUser.department || "");
      setAcademicRank(effectiveUser.academic_rank || "");
      setOrcidId(effectiveUser.orcid_id || "");
      setAvatarUrl(effectiveUser.avatar_url || "");
      setGoogleScholarUrl(effectiveUser.google_scholar_url || "");
      setResearchInterests(effectiveUser.research_interests || "");
      setBio(effectiveUser.bio || "");
      setHasByok(!!effectiveUser.has_byok);
      setByokMasked(effectiveUser.byok_masked || null);
      if (effectiveUser.theme_preference) {
        setThemePreference(effectiveUser.theme_preference);
      }
    }
  }, [effectiveUser]);

  // Tab 1 Handler: Save Profile
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileSuccessMsg(null);
    setProfileErrorMsg(null);

    const cleanOrcid = orcidId.trim();
    if (cleanOrcid && !validateOrcidId(cleanOrcid)) {
      setProfileErrorMsg("Mã ORCID không hợp lệ. Vui lòng nhập chuẩn 16 ký tự (ví dụ: 0000-0002-1825-0097).");
      return;
    }

    setIsSavingProfile(true);
    try {
      const res = await authApi.updateProfile({
        full_name: fullName.trim(),
        institution: institution.trim() || undefined,
        department: department.trim() || undefined,
        academic_rank: academicRank.trim() || undefined,
        orcid_id: cleanOrcid ? cleanOrcid : undefined,
        avatar_url: avatarUrl.trim() || undefined,
        google_scholar_url: googleScholarUrl.trim() || undefined,
        research_interests: researchInterests.trim() || undefined,
        bio: bio.trim() || undefined,
        theme_preference: themePreference,
      });

      const nextOrcid = res.orcid_id !== undefined ? res.orcid_id : cleanOrcid || undefined;
      const nextTheme: ThemePreference = res.theme_preference || themePreference;

      const updatedPayload: Partial<UserProfile> = {
        full_name: fullName.trim(),
        institution: institution.trim() || undefined,
        department: department.trim() || undefined,
        academic_rank: academicRank.trim() || undefined,
        orcid_id: nextOrcid,
        avatar_url: avatarUrl.trim() || undefined,
        google_scholar_url: googleScholarUrl.trim() || undefined,
        research_interests: researchInterests.trim() || undefined,
        bio: bio.trim() || undefined,
        theme_preference: nextTheme,
      };

      updateStoreUser(updatedPayload);
      onUpdated?.({
        ...(effectiveUser ?? { id: "usr-local", email: "" }),
        ...updatedPayload,
      });
      setProfileSuccessMsg("Hồ sơ học thuật đã được lưu trữ thành công.");
    } catch (err: unknown) {
      setProfileErrorMsg(
        err instanceof Error ? err.message : "Không thể cập nhật hồ sơ. Vui lòng thử lại sau."
      );
    } finally {
      setIsSavingProfile(false);
    }
  };

  // Tab 2 Handler: Save BYOK
  const handleSaveByok = async (e: React.FormEvent) => {
    e.preventDefault();
    setByokSuccess(null);
    setByokError(null);

    const rawKey = byokApiKey.trim();
    if (!rawKey || !rawKey.startsWith("sk-")) {
      setByokError("Vui lòng nhập khóa OpenAI API hợp lệ (bắt đầu bằng sk-...).");
      return;
    }

    setIsSavingByok(true);
    try {
      const res = await authApi.updateProfile({
        byok_api_key: rawKey,
        orcid_id: orcidId.trim() ? orcidId.trim() : undefined,
        theme_preference: themePreference,
      });

      const nextMasked = res.byok_masked || maskClientApiKey(rawKey);
      const nextHasByok = typeof res.has_byok === "boolean" ? res.has_byok : true;
      const nextOrcid = res.orcid_id !== undefined ? res.orcid_id : orcidId.trim() || undefined;
      const nextTheme: ThemePreference = res.theme_preference || themePreference;

      setHasByok(nextHasByok);
      setByokMasked(nextMasked);
      setByokApiKey("");
      setShowByokInput(false);

      const updatedPayload: Partial<UserProfile> = {
        has_byok: nextHasByok,
        byok_masked: nextMasked,
        orcid_id: nextOrcid,
        theme_preference: nextTheme,
      };

      updateStoreUser(updatedPayload);
      onUpdated?.({
        ...(effectiveUser ?? { id: "usr-local", email: "", full_name: fullName }),
        ...updatedPayload,
      });
      setByokSuccess("Khóa cá nhân đã được lưu trữ an toàn.");
    } catch (err: unknown) {
      setByokError(
        err instanceof Error ? err.message : "Không thể xác thực khóa BYOK. Vui lòng kiểm tra lại."
      );
    } finally {
      setIsSavingByok(false);
    }
  };

  // Tab 2 Handler: Delete BYOK
  const handleDeleteByok = async () => {
    setByokSuccess(null);
    setByokError(null);
    setIsDeletingByok(true);
    try {
      await authApi.updateProfile({ byok_api_key: "" });

      setHasByok(false);
      setByokMasked(null);
      setByokApiKey("");
      setShowByokInput(false);

      const updatedPayload: Partial<UserProfile> = {
        has_byok: false,
        byok_masked: null,
      };

      updateStoreUser(updatedPayload);
      onUpdated?.({
        ...(effectiveUser ?? { id: "usr-local", email: "", full_name: fullName }),
        ...updatedPayload,
      });
      setByokSuccess("Đã gỡ bỏ khóa API cá nhân.");
    } catch (err: unknown) {
      setByokError(err instanceof Error ? err.message : "Không thể xóa khóa BYOK.");
    } finally {
      setIsDeletingByok(false);
    }
  };

  // Tab 2 Handler: Change Password
  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordSuccessMsg(null);
    setPasswordErrorMsg(null);

    if (newPassword.length < 8) {
      setPasswordErrorMsg("Mật khẩu mới phải có tối thiểu 8 ký tự.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordErrorMsg("Mật khẩu xác nhận không khớp với mật khẩu mới.");
      return;
    }

    setIsChangingPassword(true);
    try {
      await authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordSuccessMsg("Mật khẩu dự phòng đã được cập nhật thành công.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: unknown) {
      setPasswordErrorMsg(
        err instanceof Error ? err.message : "Đổi mật khẩu thất bại. Vui lòng kiểm tra lại mật khẩu hiện tại."
      );
    } finally {
      setIsChangingPassword(false);
    }
  };

  // Tab 3 Handler: Theme Selection
  const handleThemeChange = async (newTheme: ThemePreference) => {
    setThemePreference(newTheme);
    setThemeSuccessMsg(null);

    applyThemePreference(newTheme);
    if (newTheme === "light" || newTheme === "dark") {
      setGlobalTheme(newTheme);
    }

    try {
      await authApi.updateProfile({ theme_preference: newTheme });
      setStoreTheme(newTheme);
      updateStoreUser({ theme_preference: newTheme });
      onUpdated?.({
        ...(effectiveUser ?? { id: "usr-local", email: "", full_name: fullName }),
        theme_preference: newTheme,
      });
      setThemeSuccessMsg("Tùy chọn giao diện đã được lưu vào hồ sơ cá nhân.");
    } catch {
      // Ignored for offline mock
    }
  };

  const initials = getScholarInitials(fullName || effectiveUser?.full_name, effectiveUser?.email);

  return (
    <div
      className={cn(
        "w-full bg-[#faf8f5] dark:bg-[#181715] text-[#1a1918] dark:text-[#f4f1ea] border border-[#e7e2da] dark:border-[#2e2b26] rounded-2xl shadow-2xl flex flex-col overflow-hidden transition-colors duration-200",
        variant === "page" ? "max-w-4xl mx-auto shadow-xl" : "max-w-2xl max-h-[90vh]"
      )}
      onClick={(e) => e.stopPropagation()}
    >
      {/* 1. Header Bar: Minimalist */}
      <div className="h-14 px-6 border-b border-[#e7e2da] dark:border-[#2e2b26] flex items-center justify-between shrink-0 bg-[#f4efe6]/80 dark:bg-[#201e1b]/80 backdrop-blur-md">
        <h1 className="font-serif font-bold text-base text-[#1a1918] dark:text-[#f4f1ea] tracking-tight">
          Cài đặt
        </h1>
        {onClose && (
          <button
            type="button"
            aria-label="Đóng"
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea] hover:bg-[#e7e2da]/60 dark:hover:bg-[#282521] transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 2. Scholar Identity Card Showcase */}
      <div className="px-6 py-4 bg-gradient-to-b from-[#f4efe6] to-[#faf8f5] dark:from-[#201e1b] dark:to-[#181715] border-b border-[#e7e2da] dark:border-[#2e2b26]">
        <div className="flex items-center gap-4">
          <div className="relative group shrink-0">
            <div className="w-14 h-14 rounded-full overflow-hidden ring-2 ring-[#cc785c]/40 shadow-sm flex items-center justify-center bg-[#e7e2da] dark:bg-[#282521]">
              {avatarUrl ? (
                <img
                  src={avatarUrl}
                  alt={fullName || "Scholar avatar"}
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center font-serif font-bold text-lg text-[#f4efe6] bg-gradient-to-br from-[#8a422d] via-[#ad593f] to-[#cc785c]">
                  {initials}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => setShowAvatarEdit(!showAvatarEdit)}
              title="Đổi URL ảnh đại diện"
              className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-white dark:bg-[#201e1b] border border-[#e7e2da] dark:border-[#2e2b26] text-[#706a60] dark:text-[#a09a8e] hover:text-[#cc785c] flex items-center justify-center shadow-xs cursor-pointer transition-colors"
            >
              <Camera className="w-2.5 h-2.5" />
            </button>
          </div>

          <div className="space-y-0.5 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-serif font-bold text-base text-[#1a1918] dark:text-[#f4f1ea] leading-tight truncate">
                {fullName || effectiveUser?.full_name || effectiveUser?.email?.split("@")[0] || "Học giả"}
              </span>
              <span title="Đã xác thực" className="inline-flex items-center">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" aria-label="Đã xác thực" />
              </span>
              {academicRank && (
                <span className="text-3xs px-2 py-0.5 rounded-full bg-[#cc785c]/15 text-[#cc785c] font-medium border border-[#cc785c]/25 font-sans">
                  {academicRank}
                </span>
              )}
            </div>
            <p className="text-xs text-[#706a60] dark:text-[#a09a8e] font-mono truncate">{effectiveUser?.email}</p>
          </div>
        </div>

        {/* Optional Avatar URL Input Accordion */}
        {showAvatarEdit && (
          <div className="mt-4 pt-3 border-t border-[#e7e2da] dark:border-[#2e2b26] flex items-center gap-2 text-xs">
            <Input
              type="url"
              placeholder="Nhập đường dẫn trực tiếp ảnh đại diện (https://...)"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              className="h-8 text-xs bg-white dark:bg-[#181715] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-lg"
            />
            <Button
              type="button"
              size="sm"
              variant="secondary"
              onClick={() => setShowAvatarEdit(false)}
              className="h-8 px-3 text-xs border border-[#e7e2da] dark:border-[#2e2b26] text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea] rounded-lg"
            >
              Đóng
            </Button>
          </div>
        )}
      </div>

      {/* 3. Navigation 3 Tabs */}
      <div className="px-6 border-b border-[#e7e2da] dark:border-[#2e2b26] bg-[#f4efe6]/40 dark:bg-[#201e1b]/40 flex items-center gap-6 overflow-x-auto select-none">
        <button
          type="button"
          onClick={() => setActiveTab("profile")}
          className={cn(
            "py-3.5 text-xs font-medium flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap",
            activeTab === "profile"
              ? "border-[#cc785c] text-[#cc785c] font-semibold"
              : "border-transparent text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea]"
          )}
        >
          <User className="w-4 h-4" />
          <span>Hồ sơ Học thuật</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("security")}
          className={cn(
            "py-3.5 text-xs font-medium flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap",
            activeTab === "security"
              ? "border-[#cc785c] text-[#cc785c] font-semibold"
              : "border-transparent text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea]"
          )}
        >
          <Shield className="w-4 h-4" />
          <span>Bảo mật &amp; Khóa BYOK</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("appearance")}
          className={cn(
            "py-3.5 text-xs font-medium flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap",
            activeTab === "appearance"
              ? "border-[#cc785c] text-[#cc785c] font-semibold"
              : "border-transparent text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea]"
          )}
        >
          <Palette className="w-4 h-4" />
          <span>Giao diện</span>
        </button>
      </div>

      {/* 4. Tab Contents Body */}
      <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
        {/* ================= TAB 1: HỒ SƠ HỌC THUẬT ================= */}
        {activeTab === "profile" && (
          <form onSubmit={handleSaveProfile} className="space-y-5">
            {profileSuccessMsg && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{profileSuccessMsg}</span>
              </div>
            )}
            {profileErrorMsg && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-600 dark:text-rose-400 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{profileErrorMsg}</span>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5 sm:col-span-2">
                <Label htmlFor="full_name" className="text-xs text-[#706a60] dark:text-[#a09a8e]">
                  Họ và tên học giả <span className="text-[#cc785c]">*</span>
                </Label>
                <Input
                  id="full_name"
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ví dụ: GS. TS. Nguyễn Văn A"
                  className="bg-white dark:bg-[#201e1b] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl focus:border-[#cc785c] focus:ring-1 focus:ring-[#cc785c]"
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="institution" className="text-xs text-[#706a60] dark:text-[#a09a8e] flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5" />
                  Đơn vị công tác (Viện / Đại học)
                </Label>
                <Input
                  id="institution"
                  type="text"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  placeholder="Đại học Quốc gia / Viện Hàn lâm"
                  className="bg-white dark:bg-[#201e1b] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl focus:border-[#cc785c] focus:ring-1 focus:ring-[#cc785c]"
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="department" className="text-xs text-[#706a60] dark:text-[#a09a8e] flex items-center gap-1.5">
                  <GraduationCap className="w-3.5 h-3.5" />
                  Khoa / Phòng thí nghiệm
                </Label>
                <Input
                  id="department"
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="Khoa Khoa học Máy tính &amp; AI"
                  className="bg-white dark:bg-[#201e1b] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl focus:border-[#cc785c] focus:ring-1 focus:ring-[#cc785c]"
                />
              </div>

              <div className="space-y-1.5 sm:col-span-2">
                <Label htmlFor="orcid_id" className="text-xs text-[#706a60] dark:text-[#a09a8e] flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Fingerprint className="w-3.5 h-3.5 text-emerald-500" />
                    Mã định danh ORCID iD
                  </span>
                  <span className="text-3xs text-[#706a60] dark:text-[#a09a8e] font-mono">Định dạng 16 số: 0000-0002-1825-0097</span>
                </Label>
                <div className="relative">
                  <Input
                    id="orcid_id"
                    type="text"
                    value={orcidId}
                    onChange={(e) => setOrcidId(e.target.value)}
                    placeholder="0000-0002-1825-0097"
                    className="bg-white dark:bg-[#201e1b] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] font-mono rounded-xl pl-9 focus:border-[#cc785c] focus:ring-1 focus:ring-[#cc785c]"
                  />
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-[#a6ce39] flex items-center justify-center font-bold text-[8px] text-white">
                    iD
                  </div>
                </div>
              </div>

              <div className="space-y-1.5 sm:col-span-2">
                <Label htmlFor="google_scholar_url" className="text-xs text-[#706a60] dark:text-[#a09a8e] flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5" />
                  Hồ sơ Google Scholar
                </Label>
                <Input
                  id="google_scholar_url"
                  type="url"
                  value={googleScholarUrl}
                  onChange={(e) => setGoogleScholarUrl(e.target.value)}
                  placeholder="https://scholar.google.com/citations?user=..."
                  className="bg-white dark:bg-[#201e1b] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl focus:border-[#cc785c] focus:ring-1 focus:ring-[#cc785c]"
                />
              </div>

              <div className="space-y-1.5 sm:col-span-2">
                <Label htmlFor="research_interests" className="text-xs text-[#706a60] dark:text-[#a09a8e] flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5" />
                  Lĩnh vực &amp; Hướng nghiên cứu chính (phân tách bởi dấu phẩy)
                </Label>
                <Input
                  id="research_interests"
                  type="text"
                  value={researchInterests}
                  onChange={(e) => setResearchInterests(e.target.value)}
                  placeholder="Large Language Models, AI for Science, Document Analysis"
                  className="bg-white dark:bg-[#201e1b] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl focus:border-[#cc785c] focus:ring-1 focus:ring-[#cc785c]"
                />
              </div>

              <div className="space-y-1.5 sm:col-span-2">
                <Label htmlFor="bio" className="text-xs text-[#706a60] dark:text-[#a09a8e]">
                  Giới thiệu học thuật ngắn (Bio)
                </Label>
                <textarea
                  id="bio"
                  rows={3}
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Tóm tắt quá trình học thuật, các công trình hoặc dự án nghiên cứu tiêu biểu..."
                  className="w-full bg-white dark:bg-[#201e1b] border border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl p-3 text-xs focus:border-[#cc785c] focus:ring-1 focus:ring-[#cc785c] outline-none resize-none font-sans"
                />
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button
                type="submit"
                disabled={isSavingProfile}
                className="rounded-xl px-5 py-2.5 bg-[#cc785c] hover:bg-[#b8674c] text-white font-medium cursor-pointer transition-colors shadow-md"
              >
                {isSavingProfile ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                    <span>Đang lưu...</span>
                  </>
                ) : (
                  <span>Lưu hồ sơ</span>
                )}
              </Button>
            </div>
          </form>
        )}

        {/* ================= TAB 2: BẢO MẬT & KHÓA BYOK ================= */}
        {activeTab === "security" && (
          <div className="space-y-6">
            {/* Part 1: Khóa API cá nhân */}
            <div className="p-5 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e7e2da] dark:border-[#2e2b26] space-y-4">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-[#cc785c]/10 text-[#cc785c] flex items-center justify-center">
                  <KeyRound className="w-3.5 h-3.5" />
                </div>
                <h3 className="font-serif font-bold text-sm text-[#1a1918] dark:text-[#f4f1ea]">
                  Khóa API cá nhân
                </h3>
              </div>

              {byokSuccess && (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{byokSuccess}</span>
                </div>
              )}
              {byokError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-600 dark:text-rose-400 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{byokError}</span>
                </div>
              )}

              {/* Status: Has Key */}
              {hasByok && !showByokInput && (
                <div className="p-4 rounded-xl bg-[#fbf9f6] dark:bg-[#181715] border border-[#e7e2da] dark:border-[#2e2b26] flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-2xs text-[#706a60] dark:text-[#a09a8e]">Khóa đang hoạt động:</p>
                      <p
                        data-testid="byok-masked-badge"
                        className="font-mono text-xs font-semibold text-[#1a1918] dark:text-[#f4f1ea]"
                      >
                        {byokMasked || "sk-...active"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      onClick={() => setShowByokInput(true)}
                      className="rounded-lg text-2xs border border-[#e7e2da] dark:border-[#2e2b26] text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea] hover:bg-[#e7e2da]/40 dark:hover:bg-[#282521]"
                    >
                      Đổi khóa mới
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      aria-label="Xóa khóa"
                      title="Xóa khóa"
                      disabled={isDeletingByok}
                      onClick={handleDeleteByok}
                      className="rounded-lg text-2xs border border-rose-500/30 text-rose-500 hover:bg-rose-500/10"
                    >
                      {isDeletingByok ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
                    </Button>
                  </div>
                </div>
              )}

              {/* Input Form for BYOK */}
              {(!hasByok || showByokInput) && (
                <form onSubmit={handleSaveByok} className="space-y-3 pt-1">
                  <Label htmlFor="byok_input" className="text-xs text-[#706a60] dark:text-[#a09a8e] flex items-center justify-between">
                    <span>Nhập OpenAI / DeepSeek API Key</span>
                    {showByokInput && (
                      <button
                        type="button"
                        onClick={() => setShowByokInput(false)}
                        className="text-3xs text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea]"
                      >
                        Hủy thay đổi
                      </button>
                    )}
                  </Label>
                  <div className="relative">
                    <Input
                      id="byok_input"
                      type={showApiKeyText ? "text" : "password"}
                      value={byokApiKey}
                      onChange={(e) => setByokApiKey(e.target.value)}
                      placeholder="sk-proj-..."
                      className="bg-white dark:bg-[#181715] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] font-mono rounded-xl pr-10 focus:border-[#cc785c] focus:ring-1 focus:ring-[#cc785c]"
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKeyText(!showApiKeyText)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea]"
                    >
                      {showApiKeyText ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  <div className="flex items-center justify-end pt-1">
                    <Button
                      type="submit"
                      disabled={isSavingByok}
                      className="rounded-xl px-4 py-2 bg-[#cc785c] hover:bg-[#b8674c] text-white text-xs font-medium cursor-pointer transition-colors shadow-md shrink-0"
                    >
                      {isSavingByok ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                          <span>Đang lưu...</span>
                        </>
                      ) : (
                        <span>Lưu &amp; Xác thực khóa</span>
                      )}
                    </Button>
                  </div>
                </form>
              )}
            </div>

            {/* Part 2: Mật khẩu dự phòng */}
            <form onSubmit={handleChangePassword} className="p-5 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e7e2da] dark:border-[#2e2b26] space-y-4">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-[#cc785c]/10 text-[#cc785c] flex items-center justify-center">
                  <Shield className="w-3.5 h-3.5" />
                </div>
                <h3 className="font-serif font-bold text-sm text-[#1a1918] dark:text-[#f4f1ea]">Thiết lập Mật khẩu dự phòng</h3>
              </div>

              {passwordSuccessMsg && (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{passwordSuccessMsg}</span>
                </div>
              )}
              {passwordErrorMsg && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-600 dark:text-rose-400 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{passwordErrorMsg}</span>
                </div>
              )}

              <div className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-3xs text-[#706a60] dark:text-[#a09a8e]">Mật khẩu hiện tại</Label>
                  <div className="relative">
                    <Input
                      type={showCurrentPassword ? "text" : "password"}
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="Nhập mật khẩu hiện tại"
                      className="bg-white dark:bg-[#181715] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl pr-10 focus:border-[#cc785c]"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea]"
                    >
                      {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-3xs text-[#706a60] dark:text-[#a09a8e]">Mật khẩu mới (tối thiểu 8 ký tự)</Label>
                    <div className="relative">
                      <Input
                        type={showNewPassword ? "text" : "password"}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Mật khẩu mới"
                        className="bg-white dark:bg-[#181715] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl pr-10 focus:border-[#cc785c]"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea]"
                      >
                        {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <Label className="text-3xs text-[#706a60] dark:text-[#a09a8e]">Xác nhận mật khẩu mới</Label>
                    <div className="relative">
                      <Input
                        type={showConfirmPassword ? "text" : "password"}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Nhập lại mật khẩu mới"
                        className="bg-white dark:bg-[#181715] border-[#e7e2da] dark:border-[#2e2b26] text-[#1a1918] dark:text-[#f4f1ea] rounded-xl pr-10 focus:border-[#cc785c]"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[#706a60] dark:text-[#a09a8e] hover:text-[#1a1918] dark:hover:text-[#f4f1ea]"
                      >
                        {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-1">
                  <Button
                    type="submit"
                    disabled={isChangingPassword || !newPassword}
                    className="rounded-xl px-4 py-2 bg-[#cc785c] hover:bg-[#b8674c] text-white text-xs font-medium cursor-pointer transition-colors shadow-md"
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
              </div>
            </form>

            {/* Part 3: Thiết bị này */}
            <div className="p-5 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e7e2da] dark:border-[#2e2b26] space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Laptop className="w-4 h-4 text-[#706a60] dark:text-[#a09a8e]" />
                  <h3 className="font-serif font-bold text-xs text-[#1a1918] dark:text-[#f4f1ea]">Thiết bị này</h3>
                </div>
                <span className="text-3xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-medium">
                  • Đang hoạt động
                </span>
              </div>
              <div className="flex justify-end pt-1">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    logout();
                    window.location.href = "/login";
                  }}
                  className="rounded-lg text-2xs border border-rose-500/30 text-rose-500 hover:bg-rose-500/10 flex items-center gap-1.5 cursor-pointer"
                >
                  <LogOut className="w-3 h-3" />
                  <span>Đăng xuất thiết bị</span>
                </Button>
              </div>
            </div>

            {/* Part 4: Tài khoản liên kết */}
            <div className="p-5 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e7e2da] dark:border-[#2e2b26] space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Globe className="w-4 h-4 text-[#706a60] dark:text-[#a09a8e]" />
                  <h3 className="font-serif font-bold text-xs text-[#1a1918] dark:text-[#f4f1ea]">Tài khoản liên kết</h3>
                </div>
              </div>
              <div className="p-3.5 rounded-xl bg-[#fbf9f6] dark:bg-[#181715] border border-[#e7e2da] dark:border-[#2e2b26] flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center shadow-xs border border-zinc-200">
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-2xs font-semibold text-[#1a1918] dark:text-[#f4f1ea]">Google</p>
                    <p className="text-3xs text-[#706a60] dark:text-[#a09a8e] font-mono">{effectiveUser?.email || "Google Account"}</p>
                  </div>
                </div>
                <span className="text-3xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-medium">
                  Đã kết nối
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ================= TAB 3: GIAO DIỆN ================= */}
        {activeTab === "appearance" && (
          <div className="space-y-4">
            <h3 className="font-serif font-bold text-sm text-[#1a1918] dark:text-[#f4f1ea]">
              Tùy chọn giao diện
            </h3>

            {themeSuccessMsg && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{themeSuccessMsg}</span>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Option 1: Light */}
              <button
                type="button"
                onClick={() => handleThemeChange("light")}
                className={cn(
                  "p-4 rounded-xl border text-left flex items-center justify-between transition-all cursor-pointer",
                  themePreference === "light"
                    ? "border-[#cc785c] bg-[#cc785c]/10 shadow-xs"
                    : "border-[#e7e2da] dark:border-[#2e2b26] bg-white dark:bg-[#201e1b] hover:border-[#cc785c]/50"
                )}
              >
                <div className="flex items-center gap-2.5">
                  <Sun className="w-4 h-4 text-amber-500 shrink-0" />
                  <span className="font-serif font-medium text-xs text-[#1a1918] dark:text-[#f4f1ea]">☀️ Sáng</span>
                </div>
                {themePreference === "light" && (
                  <CheckCircle2 className="w-4 h-4 text-[#cc785c] shrink-0" />
                )}
              </button>

              {/* Option 2: Dark */}
              <button
                type="button"
                onClick={() => handleThemeChange("dark")}
                className={cn(
                  "p-4 rounded-xl border text-left flex items-center justify-between transition-all cursor-pointer",
                  themePreference === "dark"
                    ? "border-[#cc785c] bg-[#cc785c]/10 shadow-xs"
                    : "border-[#e7e2da] dark:border-[#2e2b26] bg-white dark:bg-[#201e1b] hover:border-[#cc785c]/50"
                )}
              >
                <div className="flex items-center gap-2.5">
                  <Moon className="w-4 h-4 text-indigo-400 shrink-0" />
                  <span className="font-serif font-medium text-xs text-[#1a1918] dark:text-[#f4f1ea]">🌙 Tối</span>
                </div>
                {themePreference === "dark" && (
                  <CheckCircle2 className="w-4 h-4 text-[#cc785c] shrink-0" />
                )}
              </button>

              {/* Option 3: System */}
              <button
                type="button"
                onClick={() => handleThemeChange("system")}
                className={cn(
                  "p-4 rounded-xl border text-left flex items-center justify-between transition-all cursor-pointer",
                  themePreference === "system"
                    ? "border-[#cc785c] bg-[#cc785c]/10 shadow-xs"
                    : "border-[#e7e2da] dark:border-[#2e2b26] bg-white dark:bg-[#201e1b] hover:border-[#cc785c]/50"
                )}
              >
                <div className="flex items-center gap-2.5">
                  <Monitor className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span className="font-serif font-medium text-xs text-[#1a1918] dark:text-[#f4f1ea]">💻 Tự động</span>
                </div>
                {themePreference === "system" && (
                  <CheckCircle2 className="w-4 h-4 text-[#cc785c] shrink-0" />
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
