import * as React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLogin } from "../hooks/useLogin";
import { mockSocialAuth } from "../data/mock-auth";
import { useAuthStore } from "../stores/useAuthStore";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { SocialAuthButtons } from "./SocialAuthButtons";
import { ForgotPasswordModal } from "./ForgotPasswordModal";
import {
  Sparkles,
  Eye,
  EyeOff,
  AlertCircle,
  Loader2,
} from "lucide-react";

export function LoginForm() {
  const navigate = useNavigate();
  const loginMutation = useLogin();
  const loginStore = useAuthStore((s) => s.login);

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [rememberMe, setRememberMe] = React.useState(true);
  const [showPassword, setShowPassword] = React.useState(false);
  const [isSocialLoading, setIsSocialLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [forgotModalOpen, setForgotModalOpen] = React.useState(false);

  const handleQuickFillDemo = () => {
    const demoEmail = "scholar@verischolar.ai";
    const demoPassword = "VeriScholar2026!";
    setEmail(demoEmail);
    setPassword(demoPassword);
    setErrorMessage(null);

    loginMutation.mutate(
      { email: demoEmail, password: demoPassword, remember_me: true },
      {
        onSuccess: () => {
          navigate("/dashboard");
        },
        onError: (err) => {
          setErrorMessage(err.message || "Đăng nhập thất bại. Vui lòng thử lại.");
        },
      }
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim() || !password) {
      setErrorMessage("Vui lòng nhập đầy đủ Email và Mật khẩu.");
      return;
    }

    loginMutation.mutate(
      { email, password, remember_me: rememberMe },
      {
        onSuccess: () => {
          navigate("/dashboard");
        },
        onError: (err) => {
          setErrorMessage(err.message || "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.");
        },
      }
    );
  };

  const handleSocialAuth = async (provider: "google" | "orcid") => {
    setIsSocialLoading(true);
    setErrorMessage(null);
    try {
      const res = await mockSocialAuth(provider);
      loginStore(res, true);
      navigate("/dashboard");
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Đăng nhập qua dịch vụ liên kết thất bại.");
    } finally {
      setIsSocialLoading(false);
    }
  };

  return (
    <div className="w-full space-y-5 font-sans text-left">
      {/* 1. Clean Form Header without redundant subtitle */}
      <div>
        <h1 className="text-2xl sm:text-[26px] font-semibold tracking-tight text-ink dark:text-[#f5f3ed]">
          Đăng nhập
        </h1>
      </div>

      {/* 2. Icon-Only Social SSO at Top */}
      <SocialAuthButtons
        onSocialAuth={handleSocialAuth}
        isLoading={isSocialLoading}
        disabled={loginMutation.isPending}
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

      {/* 5. Main Form Fields */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Field */}
        <div className="space-y-1.5">
          <Label htmlFor="login-email" required>
            Email
          </Label>
          <Input
            id="login-email"
            type="email"
            autoComplete="email"
            placeholder="name@university.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loginMutation.isPending || isSocialLoading}
            error={Boolean(errorMessage && !email)}
            required
          />
        </div>

        {/* Password Field */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="login-password" required>
              Mật khẩu
            </Label>
            <button
              type="button"
              onClick={() => setForgotModalOpen(true)}
              className="text-xs text-primary hover:text-primary-active font-medium cursor-pointer"
            >
              Quên mật khẩu?
            </button>
          </div>
          <Input
            id="login-password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            placeholder="••••••••"
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
            disabled={loginMutation.isPending || isSocialLoading}
            error={Boolean(errorMessage && !password)}
            required
          />
        </div>

        {/* Remember Me Checkbox */}
        <div className="flex items-center gap-2 pt-0.5">
          <Checkbox
            id="remember-me"
            checked={rememberMe}
            onCheckedChange={setRememberMe}
            disabled={loginMutation.isPending || isSocialLoading}
          />
          <label
            htmlFor="remember-me"
            className="text-xs text-body dark:text-[#c4c0b6] cursor-pointer select-none"
          >
            Ghi nhớ đăng nhập
          </label>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          variant="primary"
          disabled={loginMutation.isPending || isSocialLoading}
          className="w-full h-10.5 text-sm font-medium shadow-xs mt-1"
        >
          {loginMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-on-primary" />
              <span>Đang xác thực...</span>
            </>
          ) : (
            <span>Đăng nhập</span>
          )}
        </Button>
      </form>

      {/* 6. Demo Quick Access: 1-click Auto-login with Demo account */}
      <Button
        type="button"
        variant="secondary"
        onClick={handleQuickFillDemo}
        disabled={loginMutation.isPending || isSocialLoading}
        data-testid="quick-fill-demo-btn"
        className="w-full h-9.5 text-xs font-medium border-dashed border-hairline dark:border-[#38332c] hover:border-primary/50 text-body dark:text-zinc-300 hover:text-ink dark:hover:text-white transition-colors gap-1.5"
      >
        <Sparkles className="w-3.5 h-3.5 text-primary shrink-0" />
        <span>Tài khoản Demo</span>
      </Button>

      {/* 7. Footer Switcher Link: Minimal direct text */}
      <div className="pt-1 text-center text-xs">
        <Link
          to="/register"
          className="text-primary hover:text-primary-active font-medium underline underline-offset-2"
        >
          Đăng ký tài khoản
        </Link>
      </div>

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        open={forgotModalOpen}
        onOpenChange={setForgotModalOpen}
        defaultEmail={email}
      />
    </div>
  );
}
