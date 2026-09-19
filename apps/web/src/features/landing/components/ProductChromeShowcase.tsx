import { Cpu } from "lucide-react";

export function ProductChromeShowcase() {
  const metrics = [
    {
      value: "< 2.4s",
      label: "SLA Response",
      description: "Hybrid Search + Cross-Encoder Rerank + BBox",
    },
    {
      value: "100%",
      label: "Grounding Rate",
      description: "Mọi khẳng định liên kết trực tiếp tọa độ PDF",
    },
    {
      value: "1 — 5",
      label: "Multi-Doc Cluster",
      description: "Cross-Doc Namespacing không nhầm lẫn ngữ cảnh",
    },
    {
      value: "Zero",
      label: "Data Retention",
      description: "ACID CAS Storage • Xóa vĩnh viễn sau phiên",
    },
  ];

  return (
    <section className="py-14 md:py-20 bg-surface-dark text-on-dark border-y border-[#2e2c28]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Minimalist Section Header */}
        <div className="text-center max-w-xl mx-auto mb-10">
          <div className="inline-flex items-center gap-2 mb-3 px-3 py-1 rounded-full bg-surface-dark-elevated border border-[#383632] text-xs font-mono text-accent-teal">
            <Cpu className="w-3.5 h-3.5" />
            <span>Production Infrastructure</span>
          </div>

          <h2 className="font-display text-3xl sm:text-4xl md:text-[42px] font-normal text-on-dark tracking-tight">
            Kiến Trúc Hạ Tầng
          </h2>

          <p className="mt-2 text-sm text-on-dark-soft font-mono">
            Độ trễ thấp. Bằng chứng nguyên tử.
          </p>
        </div>

        {/* Code Window / Terminal Card Showcase */}
        <div className="bg-surface-dark-elevated rounded-xl border border-[#383632] overflow-hidden shadow-2xl mb-10 max-w-4xl mx-auto">
          {/* Terminal Window Chrome Titlebar */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-[#1f1e1b] border-b border-[#2e2c28] text-xs font-mono text-on-dark-soft">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
              <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
              <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
              <span className="ml-2 text-on-dark-soft">verischolar-sandbox — safe-fact-checker</span>
            </div>
            <span className="text-[11px] text-accent-teal flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-teal animate-pulse" />
              TeXLive Sandbox
            </span>
          </div>

          {/* Terminal Content Body */}
          <div className="p-4 sm:p-5 font-mono text-xs text-on-dark space-y-3 bg-surface-dark-soft overflow-x-auto leading-relaxed">
            <div>
              <span className="text-muted-soft">// [Giai đoạn 1] Phân rã văn bản (Atomic Claims)</span>
              <p className="text-accent-teal mt-0.5">
                $ verischolar decompose --input &quot;Transformer đạt 28.4 BLEU trên WMT 2014 En-De, vượt qua ConvS2S&quot;
              </p>
              <div className="pl-3 mt-1 text-on-dark-soft border-l border-[#383632] space-y-0.5">
                <p>[Claim 1] Transformer đạt 28.4 BLEU WMT 2014 En-De. <span className="text-success">[Atomic]</span></p>
                <p>[Claim 2] Transformer vượt qua mô hình ConvS2S. <span className="text-success">[Atomic]</span></p>
              </div>
            </div>

            <div>
              <span className="text-muted-soft">// [Giai đoạn 2] NLI Scoring & Bounding Box Lock</span>
              <p className="text-accent-teal mt-0.5">
                $ verischolar verify --claims &quot;Claim 1, Claim 2&quot; --doc &quot;vaswani2017.pdf&quot;
              </p>
              <div className="pl-3 mt-1 text-on-dark-soft border-l border-[#383632] space-y-0.5">
                <p className="text-success">✔ Claim 1: SUPPORTED (Score: 0.982) | Tr. 8, Bảng 2 [0.52, 0.44, 0.91, 0.62]</p>
                <p className="text-success">✔ Claim 2: SUPPORTED (Score: 0.965) | Tr. 8, Mục 5.1 [0.09, 0.68, 0.48, 0.79]</p>
              </div>
            </div>

            <div>
              <span className="text-muted-soft">// [Giai đoạn 3] TeXLive Sandbox Build</span>
              <p className="text-accent-teal mt-0.5">
                $ tectonic --no-shell-escape main.tex
              </p>
              <p className="text-on-dark-soft pl-3 border-l border-[#383632]">
                SUCCESS: Compiled 12 pages in 1.42s without syntax warnings. ISO 32000-1 embedded.
              </p>
            </div>
          </div>
        </div>

        {/* 4 Metric Cards - Minimalist Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {metrics.map((m, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-surface-dark-elevated border border-[#383632] text-center"
            >
              <div className="font-mono text-2xl sm:text-3xl font-bold text-accent-teal mb-1">
                {m.value}
              </div>
              <div className="text-xs font-mono font-semibold text-on-dark uppercase tracking-wider mb-1">
                {m.label}
              </div>
              <div className="text-[11px] text-on-dark-soft font-mono">
                {m.description}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
