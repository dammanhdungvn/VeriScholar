import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ShieldCheck, Info, KeyRound, ArrowRight } from "lucide-react";

export interface SocialConnectModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  provider: "google" | "github" | "orcid" | null;
  onAcknowledge?: () => void;
  onGoogleTokenSubmit?: (token: string) => void;
  onGitHubTokenSubmit?: (tokenOrCode: string) => void;
  isLoading?: boolean;
}

export function SocialConnectModal({
  open,
  onOpenChange,
  provider,
  onAcknowledge,
  onGoogleTokenSubmit,
  onGitHubTokenSubmit,
  isLoading = false,
}: SocialConnectModalProps) {
  const isGoogle = provider === "google";
  const isGitHub = provider === "github";
  const isOrcid = provider === "orcid";
  const [manualToken, setManualToken] = React.useState("");

  const handleClose = () => {
    onOpenChange(false);
    onAcknowledge?.();
  };

  const handleTokenSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualToken.trim()) return;
    if (isGitHub) {
      onGitHubTokenSubmit?.(manualToken.trim());
    } else {
      onGoogleTokenSubmit?.(manualToken.trim());
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-canvas dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] shadow-xl p-6 font-sans">
        <DialogHeader className="space-y-3 text-left">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-surface-soft dark:bg-[#2a2622] border border-hairline dark:border-[#38332c] flex items-center justify-center shrink-0">
              {isGoogle ? (
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
              ) : isGitHub ? (
                <svg className="w-5 h-5 fill-current text-ink dark:text-zinc-100" viewBox="0 0 24 24">
                  <path
                    fillRule="evenodd"
                    clipRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  />
                </svg>
              ) : isOrcid ? (
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
              ) : (
                <ShieldCheck className="w-5 h-5 text-primary" />
              )}
            </div>
            <div>
              <DialogTitle className="text-base sm:text-lg font-semibold text-ink dark:text-[#f5f3ed]">
                {isGoogle
                  ? "Đăng nhập Google"
                  : isGitHub
                    ? "Đăng nhập GitHub"
                    : isOrcid
                      ? "Liên kết ORCID"
                      : "Liên kết tài khoản"}
              </DialogTitle>
            </div>
          </div>

          <DialogDescription className="text-xs text-body dark:text-[#c4c0b6] leading-relaxed pt-2">
            {isGoogle
              ? "Cổng đăng nhập Google đang chờ cấu hình bổ sung. Vui lòng sử dụng tài khoản email."
              : isGitHub
                ? "Đăng nhập nhanh hoặc liên kết qua tài khoản GitHub."
                : isOrcid
                  ? "Cổng liên kết tài khoản định danh nghiên cứu ORCID."
                  : "Dịch vụ liên kết tài khoản đang được hoàn thiện."}
          </DialogDescription>
        </DialogHeader>

        {isGitHub && (
          <div className="space-y-3.5 my-3">
            {onGitHubTokenSubmit && (
              <form onSubmit={handleTokenSubmit} className="space-y-2">
                <Label htmlFor="manual-github-token" className="text-2xs font-medium text-muted dark:text-zinc-300">
                  Nhập GitHub OAuth Authorization Code hoặc Access Token:
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="manual-github-token"
                    type="text"
                    value={manualToken}
                    onChange={(e) => setManualToken(e.target.value)}
                    placeholder="gho_... hoặc mã code GitHub"
                    className="h-8 text-xs font-mono"
                    disabled={isLoading}
                  />
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={isLoading || !manualToken.trim()}
                    className="h-8 px-3 text-2xs shrink-0 flex items-center gap-1 bg-zinc-800 hover:bg-zinc-900 text-white dark:bg-zinc-700 dark:hover:bg-zinc-600"
                  >
                    <span>Xác nhận</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </form>
            )}
          </div>
        )}

        {isGoogle && (
          <div className="space-y-3.5 my-3">
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-800 dark:text-amber-300 space-y-1.5">
              <div className="flex items-center gap-2 font-semibold">
                <KeyRound className="w-4 h-4 shrink-0 text-amber-600 dark:text-amber-400" />
                <span>Hướng dẫn cấu hình Google Client ID (VITE_GOOGLE_CLIENT_ID):</span>
              </div>
              <p className="text-2xs leading-relaxed text-amber-900/80 dark:text-amber-200/80">
                1. Truy cập <strong>Google Cloud Console</strong> &rarr; APIs &amp; Services &rarr; Credentials.<br />
                2. Tạo OAuth 2.0 Client ID (Web Application) với Authorized JavaScript origin: <code className="px-1 py-0.5 rounded bg-black/10 dark:bg-white/10 font-mono">https://verischolar.duckdns.org</code>.<br />
                3. Thiết lập biến môi trường tại <code className="px-1 py-0.5 rounded bg-black/10 dark:bg-white/10 font-mono">apps/web/.env</code>:
                <br />
                <code className="block mt-1 p-1.5 rounded bg-black/15 dark:bg-black/30 font-mono text-2xs break-all">
                  VITE_GOOGLE_CLIENT_ID=&quot;your-id.apps.googleusercontent.com&quot;
                </code>
              </p>
            </div>

            {onGoogleTokenSubmit && (
              <form onSubmit={handleTokenSubmit} className="space-y-2">
                <Label htmlFor="manual-google-token" className="text-2xs font-medium text-muted dark:text-zinc-300">
                  Hoặc dán Google ID Token / Token kiểm thử để xác thực trực tiếp:
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="manual-google-token"
                    type="text"
                    value={manualToken}
                    onChange={(e) => setManualToken(e.target.value)}
                    placeholder="mock_google:scholar@oxford.ac.uk hoặc Google JWT"
                    className="h-8 text-xs font-mono"
                    disabled={isLoading}
                  />
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={isLoading || !manualToken.trim()}
                    className="h-8 px-3 text-2xs shrink-0 flex items-center gap-1 bg-amber-600 hover:bg-amber-700 text-white"
                  >
                    <span>Xác nhận</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </form>
            )}
          </div>
        )}

        <div className="my-3 p-3.5 rounded-xl bg-surface-soft/80 dark:bg-[#1a1815] border border-hairline dark:border-[#38332c] flex items-start gap-2.5">
          <Info className="w-4 h-4 text-primary shrink-0 mt-0.5" />
          <p className="text-2xs text-muted dark:text-[#9c988f] leading-relaxed">
            Để bảo chứng trọn vẹn dữ liệu nghiên cứu và triệt tiêu rủi ro giả mạo tài khoản, vui lòng đăng nhập hoặc đăng ký tài khoản trực tiếp bằng địa chỉ <strong className="text-ink dark:text-white">Email học thuật</strong> của bạn.
          </p>
        </div>

        <div className="pt-2 flex justify-end">
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            className="w-full sm:w-auto text-xs px-5 h-9 font-medium"
          >
            Tôi đã hiểu, quay lại biểu mẫu
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
