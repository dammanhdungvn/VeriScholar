import React, { Component, type ReactNode } from "react";
import { AlertTriangle, RefreshCw, Copy } from "lucide-react";
import { ApiError } from "@/lib/api-client";

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  copied: boolean;
}

export class DashboardErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, copied: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, copied: false };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Dashboard caught error:", error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, copied: false });
    this.props.onReset?.();
  };

  handleCopyCode = (code: string) => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(code);
      this.setState({ copied: true });
      setTimeout(() => this.setState({ copied: false }), 2000);
    }
  };

  render() {
    if (this.state.hasError) {
      const err = this.state.error;
      const rawId = err instanceof ApiError ? err.requestId : null;
      const displayId = rawId
        ? rawId.startsWith("REQ-")
          ? rawId
          : `REQ-${rawId.substring(0, 8).toUpperCase()}`
        : null;

      return (
        <div
          role="alert"
          className="flex-1 h-full flex flex-col items-center justify-center p-8 bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef]"
        >
          <div className="max-w-md w-full p-6 rounded-2xl bg-[#f5f0e8] dark:bg-[#201e1b] border border-coral-500/20 text-center space-y-4 shadow-sm">
            <div className="w-12 h-12 mx-auto rounded-full bg-coral-500/10 flex items-center justify-center text-coral-600 dark:text-coral-400">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <div className="space-y-1">
              <h2 className="text-lg font-medium font-display tracking-tight text-ink dark:text-[#f5f3ed]">
                {this.props.fallbackTitle || "Đã xảy ra lỗi không gian làm việc"}
              </h2>
              <p className="text-xs text-muted dark:text-[#9c988f] font-mono break-all">
                {err?.message || "Lỗi không xác định trong quá trình kết xuất."}
              </p>
            </div>

            {displayId && (
              <div className="inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg bg-hairline/40 dark:bg-zinc-800/80 border border-hairline/60 dark:border-zinc-700 text-3xs font-mono text-zinc-600 dark:text-zinc-300">
                <span>Mã tra cứu:</span>
                <code className="font-semibold text-coral-600 dark:text-coral-400 select-all">
                  {displayId}
                </code>
                <button
                  type="button"
                  onClick={() => this.handleCopyCode(rawId || displayId)}
                  title="Sao chép mã lỗi để gửi kỹ thuật viên"
                  className="p-1 hover:text-coral-500 transition-colors cursor-pointer"
                >
                  <Copy className="w-3 h-3" />
                </button>
                {this.state.copied && (
                  <span className="text-emerald-600 dark:text-emerald-400 text-3xs animate-fade-in">
                    Đã chép!
                  </span>
                )}
              </div>
            )}

            <div>
              <button
                onClick={this.handleRetry}
                className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-coral-500 hover:bg-coral-600 text-white text-xs font-medium transition-colors shadow-sm cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Thử lại
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
