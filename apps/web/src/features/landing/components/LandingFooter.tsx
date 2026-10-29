import { Mail, Code2, Sparkles, BookOpen, ShieldCheck, Heart } from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";

export function LandingFooter() {
  return (
    <footer id="about" className="bg-[#181715] dark:bg-[#181715] text-on-dark-soft pt-14 sm:pt-16 pb-12 border-t border-[#2e2c28] dark:border-[#2e2a24] transition-colors">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Main Content Grid: Product Introduction + Author Card */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 pb-10 sm:pb-12 border-b border-[#2e2c28] dark:border-[#2a2721]">
          {/* Left Block: VeriScholar Overview & Mission (from PRD) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <AcademicLogo size="lg" inverted showWordmark />
              <span className="px-2.5 py-0.5 rounded-full text-[10.5px] font-mono uppercase tracking-wider bg-[#d97757]/15 border border-[#d97757]/30 text-[#e8a55a]">
                Academic Research Project
              </span>
            </div>

            <p className="font-sans text-sm text-zinc-200 leading-relaxed">
              <strong className="text-on-dark font-medium">VeriScholar</strong> là nền tảng Trợ lý AI hỗ trợ đọc hiểu sâu, đối soát và soạn thảo bài báo khoa học, được nghiên cứu và xây dựng nhằm giải quyết triệt để vấn nạn lớn nhất của giới nghiên cứu: <span className="text-[#e8a55a]">ảo giác AI (Hallucination) và trích dẫn bịa đặt</span>.
            </p>

            <p className="font-sans text-xs text-on-dark-soft leading-relaxed">
              Mọi khẳng định, số liệu và công thức đều được đối soát và bảo chứng nguồn gốc thông qua <strong>hộp trích dẫn trực quan</strong> trên trang PDF gốc. Kết hợp cùng trợ lý <strong>Socratic Assistant</strong> gợi mở tư duy và cam kết bảo mật tuyệt đối cho các bản thảo nghiên cứu chưa công bố.
            </p>

            {/* Core Capability Badges */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] font-mono text-zinc-300">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#22201c] dark:bg-[#201e1b] border border-[#332f28] dark:border-[#332f27]">
                <ShieldCheck className="w-3.5 h-3.5 text-[#5db872]" />
                Đối soát trực quan
              </span>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#22201c] dark:bg-[#201e1b] border border-[#332f28] dark:border-[#332f27]">
                <Sparkles className="w-3.5 h-3.5 text-[#d97757]" />
                Socratic Assistant
              </span>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#22201c] dark:bg-[#201e1b] border border-[#332f28] dark:border-[#332f27]">
                <BookOpen className="w-3.5 h-3.5 text-[#5db8a6]" />
                Bảo mật bản thảo
              </span>
            </div>
          </div>

          {/* Right Block: Author Dam Manh Dung & Contact Info */}
          <div className="lg:col-span-5 space-y-3.5">
            <h3 className="font-sans text-xs font-semibold text-on-dark uppercase tracking-wider flex items-center gap-2">
              <Code2 className="w-3.5 h-3.5 text-[#d97757]" />
              Tác giả & Phát triển
            </h3>

            <div className="p-4 sm:p-5 rounded-xl bg-[#1e1c18] dark:bg-[#201e1a] border border-[#332f27] dark:border-[#353028] space-y-3.5 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-serif text-base sm:text-lg font-medium text-on-dark tracking-tight">
                      Dam Manh Dung
                    </span>
                    <span className="font-mono text-xs text-[#d97757] bg-[#d97757]/10 px-1.5 py-0.5 rounded border border-[#d97757]/20">
                      @dammanhdung
                    </span>
                  </div>
                  <p className="text-xs text-on-dark-soft mt-1">
                    Dự án nghiên cứu & kỹ thuật độc lập (Personal Research Project)
                  </p>
                </div>
              </div>

              <div className="pt-2 border-t border-[#2d2a23] dark:border-[#2e2a24] space-y-2.5 text-xs font-sans">
                {/* Email Contact */}
                <a
                  href="mailto:dammanhdungvn@gmail.com"
                  data-testid="author-email-link"
                  className="flex items-center gap-2.5 text-zinc-300 hover:text-white transition-colors group"
                >
                  <div className="w-6 h-6 rounded-md bg-[#28251f] dark:bg-[#25221d] border border-[#3a352c] dark:border-[#363128] flex items-center justify-center shrink-0 text-zinc-400 group-hover:text-[#e8a55a] group-hover:border-[#d97757]/40 transition-colors">
                    <Mail className="w-3.5 h-3.5" />
                  </div>
                  <span className="font-mono text-xs">dammanhdungvn@gmail.com</span>
                </a>

                {/* GitHub Profile */}
                <a
                  href="https://github.com/dammanhdungvn"
                  target="_blank"
                  rel="noopener noreferrer"
                  data-testid="author-github-profile"
                  className="flex items-center gap-2.5 text-zinc-300 hover:text-white transition-colors group"
                >
                  <div className="w-6 h-6 rounded-md bg-[#28251f] dark:bg-[#25221d] border border-[#3a352c] dark:border-[#363128] flex items-center justify-center shrink-0 text-zinc-400 group-hover:text-white group-hover:border-[#d97757]/40 transition-colors">
                    <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24" aria-hidden="true">
                      <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                    </svg>
                  </div>
                  <span className="font-mono text-xs">github.com/dammanhdungvn</span>
                </a>

                {/* Project Repository */}
                <a
                  href="https://github.com/dammanhdungvn/VeriScholar"
                  target="_blank"
                  rel="noopener noreferrer"
                  data-testid="author-project-repo"
                  className="flex items-center gap-2.5 text-zinc-300 hover:text-white transition-colors group"
                >
                  <div className="w-6 h-6 rounded-md bg-[#28251f] dark:bg-[#25221d] border border-[#3a352c] dark:border-[#363128] flex items-center justify-center shrink-0 text-[#d97757] group-hover:border-[#d97757]/40 transition-colors">
                    <Code2 className="w-3.5 h-3.5" />
                  </div>
                  <span className="font-mono text-xs">github.com/dammanhdungvn/VeriScholar</span>
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Closing Bar: Academic Attribution & Disclaimer */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-sans text-zinc-400">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 text-center sm:text-left">
            <span>© 2026</span>
            <strong className="text-zinc-200 font-medium">Dam Manh Dung (dammanhdung)</strong>
            <span>•</span>
            <span>Dự án nghiên cứu độc lập phục vụ cộng đồng học thuật</span>
          </div>

          <div className="flex items-center gap-1.5 text-zinc-400">
            <span>Xây dựng với</span>
            <Heart className="w-3.5 h-3.5 text-[#d97757] fill-[#d97757]/30 inline" />
            <span>dành cho người làm khoa học</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
