import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  FileText,
  Download,
  AlertTriangle,
  Loader2,
  Calendar,
  Lock,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { Button } from "@/components/ui/button";
import { sharesApi } from "../api/sharesApi";
import type { PublicShareResource } from "@/types/share";

export function PublicShareReader() {
  const { token } = useParams<{ token: string }>();
  const [data, setData] = useState<PublicShareResource | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);

  useEffect(() => {
    if (!token) {
      setError("Mã liên kết không hợp lệ.");
      setIsLoading(false);
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    sharesApi
      .getPublicShare(token)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(
            err.message?.includes("410")
              ? "Liên kết chia sẻ này đã hết hạn hoặc bị tác giả thu hồi."
              : err.message || "Không thể tải tài liệu được chia sẻ."
          );
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [token]);

  const resourceData = (data?.resource_data || {}) as Record<string, any>;
  const shareTitle = String(resourceData.title || resourceData.filename || "Tài liệu nghiên cứu");
  const ownerName = String(resourceData.owner_name || "Nhà nghiên cứu");
  const expiresAt = resourceData.expires_at ? String(resourceData.expires_at) : null;

  const handleDownloadFile = async () => {
    if (!token) return;
    try {
      setIsDownloading(true);
      const blob = await sharesApi.streamSharedFile(token);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${shareTitle}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to stream shared PDF:", err);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#faf8f4] dark:bg-[#161513] text-ink dark:text-zinc-100 flex flex-col">
      {/* Top Header */}
      <header className="h-16 border-b border-[#e8e4dc] dark:border-[#2a2824] bg-white/80 dark:bg-[#1c1b18]/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2">
            <AcademicLogo size="sm" />
          </Link>
          <span className="hidden sm:inline-block text-xs font-mono px-2 py-0.5 rounded-full bg-coral-500/10 text-coral-600 dark:text-coral-400 font-medium">
            Chia sẻ công khai
          </span>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm" className="text-xs">
              Đăng nhập
            </Button>
          </Link>
          <Link to="/register">
            <Button size="sm" className="bg-coral-500 hover:bg-coral-600 text-white text-xs">
              Bắt đầu nghiên cứu
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-10 flex flex-col">
        {isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center py-20 text-muted">
            <Loader2 className="w-8 h-8 animate-spin text-coral-500 mb-3" />
            <p className="text-sm font-medium">Đang tải tài liệu chia sẻ...</p>
          </div>
        )}

        {!isLoading && error && (
          <div className="my-auto bg-white dark:bg-[#201e1b] border border-amber-500/30 rounded-2xl p-8 text-center shadow-xs">
            <div className="w-12 h-12 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 mx-auto flex items-center justify-center mb-4">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-semibold text-ink dark:text-zinc-100 mb-2">
              Không thể truy cập tài liệu
            </h2>
            <p className="text-sm text-muted mb-6 max-w-md mx-auto">{error}</p>
            <Link to="/">
              <Button variant="secondary" size="sm">
                Về trang chủ VeriScholar
              </Button>
            </Link>
          </div>
        )}

        {!isLoading && !error && data && (
          <article className="bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2e2a25] rounded-2xl p-6 md:p-10 shadow-xs space-y-8">
            {/* Title & Metadata Header */}
            <div className="border-b border-[#ece8df] dark:border-[#2e2a25] pb-6 space-y-4">
              <div className="flex items-center gap-2 text-xs text-muted font-mono">
                <span className="capitalize">{data.resource_type}</span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(data.created_at).toLocaleDateString("vi-VN")}
                </span>
                {expiresAt && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                      <Lock className="w-3.5 h-3.5" />
                      Hết hạn: {new Date(expiresAt).toLocaleDateString("vi-VN")}
                    </span>
                  </>
                )}
              </div>

              <h1 className="text-2xl md:text-3xl font-serif font-bold text-ink dark:text-[#f7f5f0] tracking-tight leading-snug">
                {shareTitle}
              </h1>

              <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-coral-500/10 text-coral-600 flex items-center justify-center font-bold text-xs">
                    {ownerName.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-ink dark:text-zinc-200">
                      {ownerName}
                    </p>
                    <p className="text-[11px] text-muted">Tác giả chia sẻ</p>
                  </div>
                </div>

                {data.resource_type === "document" && (
                  <Button
                    onClick={handleDownloadFile}
                    disabled={isDownloading}
                    size="sm"
                    className="bg-coral-500 hover:bg-coral-600 text-white text-xs gap-1.5 shadow-2xs"
                  >
                    {isDownloading ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Download className="w-3.5 h-3.5" />
                    )}
                    <span>Tải PDF gốc</span>
                  </Button>
                )}
              </div>
            </div>

            {/* Content Display based on Resource Type */}
            {data.resource_type === "draft" && (
              <div className="space-y-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-muted font-mono">
                  Nội dung bản thảo khoa học
                </h3>
                <div className="bg-[#fcfaf7] dark:bg-[#1a1917] p-6 rounded-xl border border-[#ece8df] dark:border-[#2e2a25] font-mono text-sm leading-relaxed whitespace-pre-wrap select-text">
                  {typeof resourceData.content === "string"
                    ? resourceData.content
                    : JSON.stringify(resourceData, null, 2)}
                </div>
              </div>
            )}

            {data.resource_type === "document" && (
              <div className="space-y-6">
                {resourceData.summary && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-muted font-mono">
                      Tóm tắt có bằng chứng (Executive Summary)
                    </h3>
                    <p className="text-sm text-ink dark:text-zinc-300 leading-relaxed font-serif bg-surface-cream dark:bg-[#1c1b18] p-4 rounded-xl border border-[#ece8df] dark:border-[#2a2824]">
                      {String(resourceData.summary)}
                    </p>
                  </div>
                )}

                <div className="space-y-3">
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted font-mono">
                    Thông tin tệp PDF
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                    <div className="p-3 rounded-lg border border-[#ece8df] dark:border-[#2a2824] bg-surface-cream dark:bg-[#1c1b18]">
                      <span className="text-muted block mb-1">Tên file</span>
                      <span className="font-semibold truncate block">
                        {String(resourceData.filename || shareTitle)}
                      </span>
                    </div>
                    <div className="p-3 rounded-lg border border-[#ece8df] dark:border-[#2a2824] bg-surface-cream dark:bg-[#1c1b18]">
                      <span className="text-muted block mb-1">Số trang</span>
                      <span className="font-semibold">
                        {String(resourceData.page_count || "—")} trang
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {data.resource_type === "session" && (
              <div className="space-y-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-muted font-mono">
                  Lịch sử hội thoại nghiên cứu
                </h3>
                <div className="space-y-4">
                  {Array.isArray(resourceData.messages) ? (
                    resourceData.messages.map((msg: any, idx: number) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-xl text-sm leading-relaxed ${
                          msg.role === "assistant"
                            ? "bg-[#fcfaf7] dark:bg-[#1a1917] border border-[#ece8df] dark:border-[#2e2a25]"
                            : "bg-coral-50 dark:bg-coral-950/20 border border-coral-200 dark:border-coral-800/30"
                        }`}
                      >
                        <span className="block font-semibold text-xs text-muted mb-1 uppercase font-mono">
                          {msg.role === "assistant" ? "VeriScholar AI" : "Nhà nghiên cứu"}
                        </span>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 rounded-xl bg-surface-cream dark:bg-[#1c1b18] text-sm font-mono whitespace-pre-wrap">
                      {JSON.stringify(resourceData, null, 2)}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Bottom Call to Action */}
            <div className="pt-6 border-t border-[#ece8df] dark:border-[#2e2a25] flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-xs text-muted">
                <FileText className="w-4 h-4 text-coral-500" />
                <span>Được xác thực và bảo chứng bởi VeriScholar Hybrid RAG</span>
              </div>
              <Link to="/register">
                <Button variant="secondary" size="sm" className="text-xs gap-1.5">
                  <span>Trải nghiệm VeriScholar miễn phí</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </div>
          </article>
        )}
      </main>
    </div>
  );
}
