import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordStrengthMeter } from "./PasswordStrengthMeter";
import { evaluatePasswordStrength } from "../hooks/usePasswordValidation";
import { cn } from "@/lib/utils";
import {
  Mail,
  ShieldCheck,
  RotateCw,
  Loader2,
  AlertCircle,
  Eye,
  EyeOff,
  CheckCircle2,
} from "lucide-react";

export interface OtpVerificationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  email: string;
  mode: "registration" | "forgot_password";
  onVerify: (otp: string, newPassword?: string) => Promise<void> | void;
  onResendOtp?: () => Promise<void> | void;
}

export function OtpVerificationModal({
  open,
  onOpenChange,
  email,
  mode,
  onVerify,
  onResendOtp,
}: OtpVerificationModalProps) {
  const [otpDigits, setOtpDigits] = React.useState<string[]>(["", "", "", "", "", ""]);
  const [newPassword, setNewPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [showPassword, setShowPassword] = React.useState(false);
  const [countdown, setCountdown] = React.useState(60);
  const [canResend, setCanResend] = React.useState(false);
  const [isVerifying, setIsVerifying] = React.useState(false);
  const [isResending, setIsResending] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [successNotice, setSuccessNotice] = React.useState<string | null>(null);

  const inputsRef = React.useRef<(HTMLInputElement | null)[]>([]);

  // Timer interval for countdown
  React.useEffect(() => {
    if (!open) {
      setCountdown(60);
      setCanResend(false);
      return;
    }

    if (canResend) return;

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          setCanResend(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [open, canResend]);

  // Focus first input on open
  React.useEffect(() => {
    if (open) {
      const focusTimer = setTimeout(() => {
        inputsRef.current[0]?.focus();
      }, 80);
      return () => clearTimeout(focusTimer);
    }
  }, [open]);

  const handleDigitChange = (index: number, val: string) => {
    // Only accept numeric
    const cleanVal = val.replace(/\D/g, "");
    if (!cleanVal) {
      const next = [...otpDigits];
      next[index] = "";
      setOtpDigits(next);
      return;
    }

    // Handle single digit input
    const char = cleanVal.slice(-1);
    const next = [...otpDigits];
    next[index] = char;
    setOtpDigits(next);

    // Auto focus next input
    if (index < 5) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otpDigits[index] && index > 0) {
      inputsRef.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (!pastedData) return;

    const next = [...otpDigits];
    for (let i = 0; i < 6; i++) {
      next[i] = pastedData[i] || "";
    }
    setOtpDigits(next);

    const focusIdx = Math.min(pastedData.length, 5);
    inputsRef.current[focusIdx]?.focus();
  };

  const fullOtp = otpDigits.join("");
  const isOtpComplete = fullOtp.length === 6;

  const handleResend = async () => {
    if (!canResend || isResending) return;
    setIsResending(true);
    setErrorMessage(null);
    setSuccessNotice(null);
    try {
      await onResendOtp?.();
      setSuccessNotice("Mã OTP mới đã được gửi tới email của bạn.");
      setCountdown(60);
      setCanResend(false);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Gửi lại mã OTP thất bại.");
    } finally {
      setIsResending(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!isOtpComplete) {
      setErrorMessage("Vui lòng nhập đầy đủ 6 chữ số mã xác thực.");
      return;
    }

    if (mode === "forgot_password") {
      const strength = evaluatePasswordStrength(newPassword);
      if (!strength.isAcceptable) {
        setErrorMessage("Mật khẩu mới cần tối thiểu 8 ký tự, gồm chữ hoa, số hoặc ký tự đặc biệt.");
        return;
      }
      if (newPassword !== confirmPassword) {
        setErrorMessage("Mật khẩu xác nhận không khớp.");
        return;
      }
    }

    setIsVerifying(true);
    try {
      await onVerify(fullOtp, mode === "forgot_password" ? newPassword : undefined);
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error
          ? err.message
          : "Mã OTP không chính xác hoặc đã hết hiệu lực. Vui lòng thử lại."
      );
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-canvas dark:bg-[#1a1917] border border-amber-900/10 dark:border-amber-500/20 shadow-2xl p-6 sm:p-7 rounded-2xl font-sans">
        {/* Academic Luxury Header */}
        <DialogHeader className="space-y-2 text-left">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500/20 via-amber-600/25 to-amber-700/30 border border-amber-500/30 flex items-center justify-center text-amber-600 dark:text-amber-400 shadow-sm mb-1">
            {mode === "registration" ? (
              <ShieldCheck className="w-6 h-6" />
            ) : (
              <Mail className="w-6 h-6" />
            )}
          </div>
          <DialogTitle className="text-xl sm:text-2xl font-serif font-bold text-ink dark:text-[#f7f5f0] tracking-tight">
            {mode === "registration"
              ? "Xác thực Email học thuật"
              : "Khôi phục mật khẩu tài khoản"}
          </DialogTitle>
          <DialogDescription className="text-xs sm:text-sm text-muted dark:text-[#a8a49a] leading-relaxed">
            Chúng tôi đã gửi mã xác thực 6 chữ số tới địa chỉ email:
          </DialogDescription>
          <div className="p-3.5 rounded-xl bg-amber-500/8 dark:bg-amber-400/8 border border-amber-500/20 dark:border-amber-400/20 flex items-center gap-2.5">
            <Mail className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
            <span className="font-mono font-semibold text-xs sm:text-sm text-ink dark:text-white break-all select-all">
              {email}
            </span>
          </div>
        </DialogHeader>

        {errorMessage && (
          <div
            role="alert"
            className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-700 dark:text-rose-300 text-xs flex items-start gap-2.5 shadow-xs animate-in fade-in"
          >
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
            <span className="leading-relaxed font-medium">{errorMessage}</span>
          </div>
        )}

        {successNotice && (
          <div
            role="status"
            className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-800 dark:text-emerald-300 text-xs flex items-start gap-2.5 shadow-xs animate-in fade-in"
          >
            <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-600 dark:text-emerald-400" />
            <span className="leading-relaxed font-medium">{successNotice}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          {/* OTP 6-Digit Grid with High Contrast & Focus Ring */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-xs font-semibold text-ink/90 dark:text-zinc-200 uppercase tracking-wide">
                Nhập mã xác thực (OTP)
              </Label>
              <span className="text-3xs text-muted dark:text-zinc-400 font-mono">
                {isOtpComplete ? "6/6 chữ số" : `${fullOtp.length}/6 chữ số`}
              </span>
            </div>

            <div className="flex items-center justify-between gap-1.5 sm:gap-2">
              {otpDigits.map((digit, idx) => (
                <input
                  key={idx}
                  ref={(el) => {
                    inputsRef.current[idx] = el;
                  }}
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleDigitChange(idx, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(idx, e)}
                  onPaste={handlePaste}
                  disabled={isVerifying}
                  data-testid={`otp-input-${idx}`}
                  aria-label={`Chữ số OTP thứ ${idx + 1}`}
                  className={cn(
                    "w-11 sm:w-12 h-13 sm:h-14 text-center text-xl sm:text-2xl font-mono font-bold rounded-xl border-2 transition-all duration-150",
                    "focus:outline-none focus:scale-105",
                    digit
                      ? "border-amber-500 dark:border-amber-400 bg-amber-50/40 dark:bg-amber-950/30 text-amber-900 dark:text-amber-100 focus:border-amber-600 focus:ring-4 focus:ring-amber-500/25"
                      : "border-zinc-300 dark:border-zinc-600 bg-white dark:bg-[#1f1d1a] text-ink dark:text-white shadow-xs focus:border-amber-600 dark:focus:border-amber-400 focus:ring-4 focus:ring-amber-500/25"
                  )}
                />
              ))}
            </div>
          </div>

          {/* New Password fields if mode === "forgot_password" */}
          {mode === "forgot_password" && (
            <div className="space-y-3 pt-2 border-t border-hairline dark:border-[#38332c]">
              <div className="space-y-1.5">
                <Label htmlFor="otp-new-password" required className="text-xs font-semibold">
                  Mật khẩu mới
                </Label>
                <Input
                  id="otp-new-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Tối thiểu 8 ký tự"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  disabled={isVerifying}
                  endIcon={
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="cursor-pointer hover:text-ink dark:hover:text-white transition-colors focus:outline-none"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  }
                  required
                />
                <PasswordStrengthMeter password={newPassword} />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="otp-confirm-password" required className="text-xs font-semibold">
                  Xác nhận mật khẩu mới
                </Label>
                <Input
                  id="otp-confirm-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Nhập lại mật khẩu mới"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={isVerifying}
                  required
                />
              </div>
            </div>
          )}

          {/* Resend OTP Link & Countdown */}
          <div className="flex items-center justify-between text-xs text-muted dark:text-zinc-400 pt-1">
            <span>Không nhận được mã?</span>
            {canResend ? (
              <button
                type="button"
                onClick={handleResend}
                disabled={isResending}
                className="text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 font-semibold underline underline-offset-4 flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {isResending ? (
                  <RotateCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <RotateCw className="w-3.5 h-3.5" />
                )}
                <span>Gửi lại mã</span>
              </button>
            ) : (
              <span className="font-mono text-muted/80">Gửi lại sau {countdown}s</span>
            )}
          </div>

          {/* Action Buttons with Prominent Amber-600 CTA */}
          <div className="flex items-center justify-end gap-3 pt-3">
            <button
              type="button"
              onClick={() => onOpenChange(false)}
              disabled={isVerifying}
              className="h-11 px-4 text-xs sm:text-sm font-medium text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-white rounded-xl hover:bg-surface-soft dark:hover:bg-zinc-800 transition-colors cursor-pointer disabled:opacity-50"
            >
              Hủy bỏ
            </button>
            <button
              type="submit"
              disabled={isVerifying || !isOtpComplete}
              className="w-full sm:w-auto h-11 px-6 rounded-xl font-sans text-xs sm:text-sm font-semibold text-white bg-amber-600 hover:bg-amber-700 active:bg-amber-800 shadow-lg shadow-amber-600/30 hover:shadow-xl hover:shadow-amber-600/40 transition-all duration-150 cursor-pointer disabled:bg-amber-600/50 disabled:text-white/60 disabled:shadow-none disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isVerifying ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Đang xác thực...</span>
                </>
              ) : (
                <span>
                  {mode === "registration" ? "Xác nhận & Kích hoạt" : "Đặt lại mật khẩu"}
                </span>
              )}
            </button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
