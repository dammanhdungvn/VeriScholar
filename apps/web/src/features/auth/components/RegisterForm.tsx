import * as React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useRegister } from "../hooks/useRegister";
import { useGoogleAuth } from "../hooks/useGoogleAuth";
import { evaluatePasswordStrength } from "../hooks/usePasswordValidation";
import { authApi } from "../api/authApi";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { PasswordStrengthMeter } from "./PasswordStrengthMeter";
import { SocialAuthButtons } from "./SocialAuthButtons";
import { SocialConnectModal } from "./SocialConnectModal";
import { OtpVerificationModal } from "./OtpVerificationModal";
import { validateEmail, validateFullName } from "../utils/emailValidation";
import {
  Eye,
  EyeOff,
  AlertCircle,
  Loader2,
  GraduationCap,
} from "lucide-react";

export function RegisterForm() {
  const navigate = useNavigate();
  const registerMutation = useRegister();
  const { loginWithGoogleToken, isLoading: isGoogleLoading } = useGoogleAuth({
    onError: (err) => setErrorMessage(err.message),
  });

  const [fullName, setFullName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [acceptTerms, setAcceptTerms] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  // Field-specific validation states
  const [fullNameError, setFullNameError] = React.useState<string | null>(null);
  const [emailError, setEmailError] = React.useState<string | null>(null);

  // Modals state
  const [socialModalOpen, setSocialModalOpen] = React.useState(false);
  const [selectedSocialProvider, setSelectedSocialProvider] = React.useState<"google" | "orcid" | null>(null);
  const [otpModalOpen, setOtpModalOpen] = React.useState(false);

  const passwordStrength = React.useMemo(() => evaluatePasswordStrength(password), [password]);
  const emailValidation = React.useMemo(() => validateEmail(email), [email]);

  const handleFullNameBlur = () => {
    if (!fullName.trim()) return;
    const res = validateFullName(fullName);
    if (!res.isValid) {
      setFullNameError(res.error || "Họ và tên không hợp lệ.");
    } else {
      setFullNameError(null);
    }
  };

  const handleEmailBlur = () => {
    if (!email.trim()) return;
    if (!emailValidation.isValid) {
      setEmailError(emailValidation.error || "Địa chỉ email không hợp lệ.");
    } else {
      setEmailError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setFullNameError(null);
    setEmailError(null);

    // 1. Validate full name (minimum 2 words)
    const nameCheck = validateFullName(fullName);
    if (!nameCheck.isValid) {
      const err = nameCheck.error || "Vui lòng nhập đầy đủ cả Họ và Tên (tối thiểu 2 từ).";
      setFullNameError(err);
      setErrorMessage(err);
      return;
    }

    // 2. Validate email (strict whitelist: .edu, .edu.vn, .ac.*, gmail.com, etc.)
    if (!emailValidation.isValid) {
      const err = emailValidation.error || "Vui lòng nhập địa chỉ email hợp lệ.";
      setEmailError(err);
      setErrorMessage(err);
      return;
    }

    // 3. Validate password entropy / strength
    if (!passwordStrength.isAcceptable) {
      setErrorMessage("Mật khẩu cần tối thiểu 8 ký tự, gồm chữ hoa, số hoặc ký tự đặc biệt.");
      return;
    }

    if (!acceptTerms) {
      setErrorMessage("Vui lòng đồng ý với Điều khoản Sử dụng để tiếp tục.");
      return;
    }

    // 4. CRITICAL FLOW: Call backend register FIRST to create user, generate OTP and dispatch email
    try {
      await registerMutation.mutateAsync({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        accept_terms: acceptTerms,
      });
      // Registration call succeeded -> open OtpVerificationModal
      setOtpModalOpen(true);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.";
      setErrorMessage(msg);
    }
  };

  const handleVerifyOtp = async (otp: string) => {
    if (!otp || otp.length !== 6) {
      throw new Error("Mã OTP phải gồm 6 chữ số.");
    }

    await authApi.verifyEmail({
      email: email.trim(),
      code: otp,
    });

    setOtpModalOpen(false);
    navigate("/dashboard");
  };

  const handleResendOtp = async () => {
    await authApi.resendVerification({
      email: email.trim(),
    });
  };

  const handleSocialAuth = (provider: "google" | "orcid") => {
    setSelectedSocialProvider(provider);
    setSocialModalOpen(true);
  };

  return (
    <div className="w-full space-y-5 font-sans text-left">
      {/* 1. Academic Luxury Header */}
      <div>
        <h1 className="text-2xl sm:text-[28px] font-serif font-bold tracking-tight text-ink dark:text-[#f7f5f0]">
          Đăng ký
        </h1>
        <p className="text-xs sm:text-sm text-muted dark:text-[#9c988f] pt-0.5">
          Tạo tài khoản nhà nghiên cứu trên nền tảng VeriScholar
        </p>
      </div>

      {/* 2. Icon-Only Social SSO at Top */}
      <SocialAuthButtons
        onSocialAuth={handleSocialAuth}
        onGoogleSuccess={loginWithGoogleToken}
        isLoading={isGoogleLoading}
        disabled={registerMutation.isPending || isGoogleLoading}
      />

      {/* 3. Subtle Hairline Divider */}
      <Separator label="hoặc email" />

      {/* 4. Error Message Alert */}
      {errorMessage && (
        <div
          role="alert"
          className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-700 dark:text-rose-300 text-xs flex items-start gap-2.5 font-medium shadow-xs animate-in fade-in slide-in-from-top-1"
        >
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
          <span className="leading-relaxed">{errorMessage}</span>
        </div>
      )}

      {/* 5. Streamlined 3 Core Fields Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Full Name */}
        <div className="space-y-1.5">
          <Label htmlFor="reg-fullname" required className="text-xs font-semibold uppercase tracking-wide text-ink/90 dark:text-zinc-200">
            Họ và tên
          </Label>
          <Input
            id="reg-fullname"
            type="text"
            autoComplete="name"
            placeholder="Nguyễn Văn A (tối thiểu 2 từ)"
            value={fullName}
            onChange={(e) => {
              setFullName(e.target.value);
              if (fullNameError) setFullNameError(null);
              if (errorMessage) setErrorMessage(null);
            }}
            onBlur={handleFullNameBlur}
            disabled={registerMutation.isPending}
            error={Boolean(fullNameError)}
            className="h-11 rounded-xl border-zinc-300 dark:border-zinc-700 bg-white dark:bg-[#1f1d1a] text-ink dark:text-white text-sm focus:border-amber-600 focus:ring-4 focus:ring-amber-500/20"
            required
          />
          {fullNameError && (
            <p className="text-2xs text-rose-600 dark:text-rose-400 font-medium leading-tight">
              {fullNameError}
            </p>
          )}
        </div>

        {/* Email */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="reg-email" required className="text-xs font-semibold uppercase tracking-wide text-ink/90 dark:text-zinc-200">
              Email
            </Label>
            {email.trim() && emailValidation.isAcademic && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-3xs font-medium text-emerald-700 dark:text-emerald-300">
                <GraduationCap className="w-3.5 h-3.5" />
                Email học thuật được tin cậy
              </span>
            )}
          </div>
          <Input
            id="reg-email"
            type="email"
            autoComplete="email"
            placeholder="scholar@university.edu"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (emailError) setEmailError(null);
              if (errorMessage) setErrorMessage(null);
            }}
            onBlur={handleEmailBlur}
            disabled={registerMutation.isPending}
            error={Boolean(emailError)}
            className="h-11 rounded-xl border-zinc-300 dark:border-zinc-700 bg-white dark:bg-[#1f1d1a] text-ink dark:text-white text-sm focus:border-amber-600 focus:ring-4 focus:ring-amber-500/20"
            required
          />
          {emailError && (
            <p className="text-2xs text-rose-600 dark:text-rose-400 font-medium leading-tight">
              {emailError}
            </p>
          )}
        </div>

        {/* Password */}
        <div className="space-y-1.5">
          <Label htmlFor="reg-password" required className="text-xs font-semibold uppercase tracking-wide text-ink/90 dark:text-zinc-200">
            Mật khẩu
          </Label>
          <Input
            id="reg-password"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Tối thiểu 8 ký tự (chữ hoa, số, ký tự đặc biệt)"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (errorMessage) setErrorMessage(null);
            }}
            endIcon={
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="cursor-pointer hover:text-ink dark:hover:text-white transition-colors focus:outline-none"
                aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            }
            disabled={registerMutation.isPending}
            className="h-11 rounded-xl border-zinc-300 dark:border-zinc-700 bg-white dark:bg-[#1f1d1a] text-ink dark:text-white text-sm focus:border-amber-600 focus:ring-4 focus:ring-amber-500/20"
            required
          />
          <PasswordStrengthMeter password={password} />
        </div>

        {/* Terms Agreement Checkbox */}
        <div className="flex items-start gap-2.5 pt-1">
          <Checkbox
            id="accept-terms"
            checked={acceptTerms}
            onCheckedChange={setAcceptTerms}
            disabled={registerMutation.isPending}
            className="mt-0.5"
          />
          <label
            htmlFor="accept-terms"
            className="text-xs text-muted dark:text-[#a8a49a] leading-snug cursor-pointer select-none"
          >
            Đồng ý với{" "}
            <span className="text-amber-700 dark:text-amber-400 hover:underline font-medium">Điều khoản</span> &{" "}
            <span className="text-amber-700 dark:text-amber-400 hover:underline font-medium">Bảo mật</span> của VeriScholar.
          </label>
        </div>

        {/* Submit Button with Academic Luxury Amber-600 CTA */}
        <button
          type="submit"
          disabled={
            registerMutation.isPending ||
            !acceptTerms ||
            !passwordStrength.isAcceptable
          }
          className="w-full h-11 text-sm font-semibold rounded-xl text-white bg-amber-600 hover:bg-amber-700 active:bg-amber-800 shadow-lg shadow-amber-600/30 hover:shadow-xl hover:shadow-amber-600/40 transition-all duration-150 cursor-pointer disabled:bg-amber-600/50 disabled:text-white/60 disabled:shadow-none disabled:cursor-not-allowed mt-2 flex items-center justify-center gap-2"
        >
          {registerMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white mr-1.5" />
              <span>Đang xử lý đăng ký...</span>
            </>
          ) : (
            <span>Đăng ký</span>
          )}
        </button>
      </form>

      {/* 6. Footer Switcher */}
      <div className="pt-1 text-center text-xs">
        <span className="text-muted dark:text-[#a8a49a] mr-1">Đã có tài khoản?</span>
        <Link
          to="/login"
          className="text-amber-700 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-300 font-semibold underline underline-offset-2"
        >
          Đăng nhập
        </Link>
      </div>

      {/* Social Academic Connect Modal */}
      <SocialConnectModal
        open={socialModalOpen}
        onOpenChange={setSocialModalOpen}
        provider={selectedSocialProvider}
        onGoogleTokenSubmit={loginWithGoogleToken}
        isLoading={isGoogleLoading}
      />

      {/* Registration OTP Verification Modal */}
      <OtpVerificationModal
        open={otpModalOpen}
        onOpenChange={setOtpModalOpen}
        email={email}
        mode="registration"
        onVerify={handleVerifyOtp}
        onResendOtp={handleResendOtp}
      />
    </div>
  );
}
