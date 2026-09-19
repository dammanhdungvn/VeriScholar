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
import { Mail, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { mockForgotPassword } from "../data/mock-auth";

export interface ForgotPasswordModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultEmail?: string;
}

interface ForgotPasswordContentProps {
  onClose: () => void;
  defaultEmail?: string;
}

function ForgotPasswordContent({ onClose, defaultEmail = "" }: ForgotPasswordContentProps) {
  const [email, setEmail] = React.useState(defaultEmail);
  const [isLoading, setIsLoading] = React.useState(false);
  const [successMessage, setSuccessMessage] = React.useState<string | null>(null);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes("@")) {
      setErrorMessage("Vui lòng nhập địa chỉ email hợp lệ.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await mockForgotPassword(email);
      setSuccessMessage(res.message);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Đã xảy ra lỗi. Vui lòng thử lại sau.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DialogContent className="sm:max-w-md bg-canvas dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] shadow-xl p-6">
      <DialogHeader className="space-y-2 text-left">
        <DialogTitle className="font-display text-2xl font-normal text-ink dark:text-[#f5f3ed]">
          Khôi phục mật khẩu học thuật
        </DialogTitle>
        <DialogDescription className="font-sans text-xs text-muted dark:text-[#9c988f]">
          Nhập địa chỉ email liên kết với tài khoản VeriScholar của bạn để nhận hướng dẫn đặt lại mật khẩu an toàn.
        </DialogDescription>
      </DialogHeader>

      {successMessage ? (
        <div className="py-4 space-y-4 font-sans">
          <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-300 text-xs flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500 mt-0.5" />
            <span>{successMessage}</span>
          </div>
          <Button
            type="button"
            variant="primary"
            onClick={onClose}
            className="w-full text-xs"
          >
            Đóng và quay lại Đăng nhập
          </Button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4 pt-2 font-sans">
          {errorMessage && (
            <div className="p-3 rounded-lg bg-error/10 border border-error/20 text-error text-xs flex items-start gap-2">
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
              onChange={(e) => setEmail(e.target.value)}
              startIcon={<Mail className="w-4 h-4" />}
              disabled={isLoading}
            />
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
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
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Đang gửi...</span>
                </>
              ) : (
                <span>Gửi liên kết</span>
              )}
            </Button>
          </div>
        </form>
      )}
    </DialogContent>
  );
}

export function ForgotPasswordModal({
  open,
  onOpenChange,
  defaultEmail = "",
}: ForgotPasswordModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {open && (
        <ForgotPasswordContent
          onClose={() => onOpenChange(false)}
          defaultEmail={defaultEmail}
        />
      )}
    </Dialog>
  );
}
