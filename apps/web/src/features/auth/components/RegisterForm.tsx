import * as React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useRegister } from "../hooks/useRegister";
import { evaluatePasswordStrength } from "../hooks/usePasswordValidation";
import { mockSocialAuth } from "../data/mock-auth";
import { useAuthStore } from "../stores/useAuthStore";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { PasswordStrengthMeter } from "./PasswordStrengthMeter";
import { SocialAuthButtons } from "./SocialAuthButtons";
import {
  Eye,
  EyeOff,
  AlertCircle,
  Loader2,
} from "lucide-react";

export function RegisterForm() {
  const navigate = useNavigate();
  const registerMutation = useRegister();
  const loginStore = useAuthStore((s) => s.login);

  const [fullName, setFullName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [acceptTerms, setAcceptTerms] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);
  const [isSocialLoading, setIsSocialLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const passwordStrength = React.useMemo(() => evaluatePasswordStrength(password), [password]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!fullName.trim()) {
      setErrorMessage("Vui lòng nhập họ và tên của bạn.");
      return;
    }

    if (!email.trim()) {
      setErrorMessage("Vui lòng nhập địa chỉ email hợp lệ.");
      return;
    }

    if (!passwordStrength.isAcceptable) {
      setErrorMessage("Mật khẩu cần tối thiểu 8 ký tự, gồm chữ hoa, số hoặc ký tự đặc biệt.");
      return;
    }

    if (!acceptTerms) {
      setErrorMessage("Vui lòng đồng ý với Điều khoản Sử dụng để tiếp tục.");
      return;
    }

    try {
      registerMutation.mutate(
        {
          full_name: fullName.trim(),
          email: email.trim(),
          password,
          accept_terms: acceptTerms,
        },
        {
          onSuccess: () => {
            navigate("/dashboard");
          },
          onError: (err) => {
            setErrorMessage(err.message || "Đăng ký tài khoản thất bại.");
          },
        }
      );
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Đăng ký tài khoản thất bại. Vui lòng thử lại sau.");
    }
  };

  const handleSocialAuth = async (provider: "google" | "orcid") => {
    setIsSocialLoading(true);
    setErrorMessage(null);
    try {
      const res = await mockSocialAuth(provider);
      loginStore(res, true);
      navigate("/dashboard");
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Đăng ký qua dịch vụ liên kết thất bại.");
    } finally {
      setIsSocialLoading(false);
    }
  };

  return (
    <div className="w-full space-y-5 font-sans text-left">
      {/* 1. Header without redundant subtitle */}
      <div>
        <h1 className="text-2xl sm:text-[26px] font-semibold tracking-tight text-ink dark:text-[#f5f3ed]">
          Đăng ký
        </h1>
      </div>

      {/* 2. Icon-Only Social SSO at Top */}
      <SocialAuthButtons
        onSocialAuth={handleSocialAuth}
        isLoading={isSocialLoading}
        disabled={registerMutation.isPending}
      />

      {/* 3. Subtle Hairline Divider */}
      <Separator label="hoặc email" />

      {/* 4. Error Message Alert */}
      {errorMessage && (
        <div
          role="alert"
          className="p-3 rounded-xl bg-error/10 border border-error/20 text-error text-xs flex items-start gap-2.5 animate-in fade-in slide-in-from-top-1"
        >
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span className="leading-relaxed">{errorMessage}</span>
        </div>
      )}

      {/* 5. Streamlined 3 Core Fields Form */}
      <form onSubmit={handleSubmit} className="space-y-3.5">
        {/* Full Name */}
        <div className="space-y-1.5">
          <Label htmlFor="reg-fullname" required>
            Họ và tên
          </Label>
          <Input
            id="reg-fullname"
            type="text"
            autoComplete="name"
            placeholder="Nguyễn Văn A"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            disabled={registerMutation.isPending || isSocialLoading}
            required
          />
        </div>

        {/* Email */}
        <div className="space-y-1.5">
          <Label htmlFor="reg-email" required>
            Email
          </Label>
          <Input
            id="reg-email"
            type="email"
            autoComplete="email"
            placeholder="name@university.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={registerMutation.isPending || isSocialLoading}
            required
          />
        </div>

        {/* Password */}
        <div className="space-y-1.5">
          <Label htmlFor="reg-password" required>
            Mật khẩu
          </Label>
          <Input
            id="reg-password"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Tối thiểu 8 ký tự"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
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
            disabled={registerMutation.isPending || isSocialLoading}
            required
          />
          <PasswordStrengthMeter password={password} />
        </div>

        {/* Terms Agreement Checkbox */}
        <div className="flex items-start gap-2 pt-1">
          <Checkbox
            id="accept-terms"
            checked={acceptTerms}
            onCheckedChange={setAcceptTerms}
            disabled={registerMutation.isPending || isSocialLoading}
            className="mt-0.5"
          />
          <label
            htmlFor="accept-terms"
            className="text-2xs text-muted dark:text-[#9c988f] leading-snug cursor-pointer select-none"
          >
            Đồng ý với{" "}
            <span className="text-primary hover:underline font-medium">Điều khoản</span> &{" "}
            <span className="text-primary hover:underline font-medium">Bảo mật</span> của VeriScholar.
          </label>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          variant="primary"
          disabled={
            registerMutation.isPending ||
            isSocialLoading ||
            !acceptTerms ||
            !passwordStrength.isAcceptable
          }
          className="w-full h-10.5 text-sm font-medium shadow-xs mt-1"
        >
          {registerMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-on-primary" />
              <span>Đang khởi tạo...</span>
            </>
          ) : (
            <span>Đăng ký</span>
          )}
        </Button>
      </form>

      {/* 6. Footer Switcher: Minimal direct text */}
      <div className="pt-1 text-center text-xs">
        <Link
          to="/login"
          className="text-primary hover:text-primary-active font-medium underline underline-offset-2"
        >
          Đăng nhập
        </Link>
      </div>
    </div>
  );
}
