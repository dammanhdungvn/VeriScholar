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
import { Button } from "@/components/ui/button";
import { Mail, Loader2, AlertCircle } from "lucide-react";
import { authApi } from "../api/authApi";
import { validateEmail } from "../utils/emailValidation";
import { OtpVerificationModal } from "./OtpVerificationModal";

export interface ForgotPasswordModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultEmail?: string;
}

export function ForgotPasswordModal({
  open,
  onOpenChange,
  defaultEmail = "",
}: ForgotPasswordModalProps) {
  const [email, setEmail] = React.useState(defaultEmail);
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [otpModalOpen, setOtpModalOpen] = React.useState(false);

  React.useEffect(() => {
    if (open) {
      queueMicrotask(() => {
        setEmail(defaultEmail);
        setErrorMessage(null);
      });
    }
  }, [open, defaultEmail]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const emailCheck = validateEmail(email);
    if (!emailCheck.isValid) {
      setErrorMessage(emailCheck.error || "Vui lòng nhập địa chỉ email hợp lệ.");
      return;
    }

    setIsLoading(true);
    try {
      await authApi.forgotPassword({ email: email.trim() });
      // Open OTP modal for resetting password
      setOtpModalOpen(true);
      onOpenChange(false);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Đã xảy ra lỗi. Vui lòng thử lại sau.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (otp: string, newPassword?: string) => {
    if (!newPassword) {
      throw new Error("Vui lòng nhập mật khẩu mới.");
    }
    await authApi.resetPassword({
      token: otp,
      new_password: newPassword,
      email: email.trim(),
    });
    setOtpModalOpen(false);
  };

  const handleResendOtp = async () => {
    await authApi.forgotPassword({ email: email.trim() });
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md bg-canvas dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] shadow-xl p-6 font-sans">
          <DialogHeader className="space-y-2 text-left">
            <DialogTitle className="font-display text-2xl font-normal text-ink dark:text-[#f5f3ed]">
              Khôi phục mật khẩu
            </DialogTitle>
            <DialogDescription className="text-xs text-muted dark:text-[#9c988f]">
              Nhập địa chỉ email tài khoản của bạn để nhận mã xác thực đặt lại mật khẩu.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            {errorMessage && (
              <div
                role="alert"
                className="p-3 rounded-lg bg-error/10 border border-error/20 text-error text-xs flex items-start gap-2"
              >
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div>
              <Label htmlFor="forgot-email" required>
                Email học thuật
              </Label>
              <Input
                id="forgot-email"
                type="email"
                autoComplete="email"
                required
                placeholder="ten.nghiencuu@vienkhoahoc.vn"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                startIcon={<Mail className="w-4 h-4" />}
                disabled={isLoading}
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => onOpenChange(false)}
                disabled={isLoading}
                className="text-xs"
              >
                Hủy bỏ
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={isLoading || !email}
                className="text-xs min-w-[120px]"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                    <span>Đang gửi mã...</span>
                  </>
                ) : (
                  <span>Gửi mã OTP</span>
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* OTP Verification & Password Reset Modal */}
      <OtpVerificationModal
        open={otpModalOpen}
        onOpenChange={setOtpModalOpen}
        email={email}
        mode="forgot_password"
        onVerify={handleVerifyOtp}
        onResendOtp={handleResendOtp}
      />
    </>
  );
}
