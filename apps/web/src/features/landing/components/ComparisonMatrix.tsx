import { Check, Minus, Sparkles, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function ComparisonMatrix() {
  const comparisons = [
    {
      feature: "Visual Grounding",
      detail: "Bảo chứng tọa độ nhị phân",
      verischolar: "Bounding Box ISO 32000-1",
      others: "Số trang thô / URL",
      highlight: true,
    },
    {
      feature: "Zero-Hallucination",
      detail: "Triệt tiêu hoàn toàn bịa đặt",
      verischolar: "Abstention Guardrail < 0.35",
      others: "Tự sinh trích dẫn giả",
      highlight: true,
    },
    {
      feature: "Socratic AI",
      detail: "Phản biện tiền đề câu hỏi",
      verischolar: "Presupposition Check",
      others: "A dua mù quáng",
      highlight: false,
    },
    {
      feature: "Table & Math Stitching",
      detail: "Bảo toàn bảng & công thức",
      verischolar: "Composite Box 100%",
      others: "Vỡ ký hiệu LaTeX",
      highlight: false,
    },
    {
      feature: "Self-Healing TeXLive",
      detail: "Biên dịch & tự sửa lỗi",
      verischolar: "DeepMind SAFE + Sandbox",
      others: "Không hỗ trợ",
      highlight: false,
    },
  ];

  return (
    <section id="comparison" className="py-14 md:py-20 relative scroll-mt-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 relative z-10">
        {/* Minimal Header */}
        <div className="text-center max-w-xl mx-auto mb-10">
          <div className="inline-flex items-center gap-2 mb-3 px-3 py-1 rounded-full bg-surface-card border border-hairline text-xs font-mono text-muted">
            <Sparkles className="w-3.5 h-3.5 text-primary" />
            <span className="font-semibold text-ink uppercase tracking-wider text-[11px]">Benchmark</span>
          </div>

          <h2 className="font-display text-3xl sm:text-4xl md:text-[42px] font-normal text-ink tracking-tight">
            Đối Sánh Năng Lực
          </h2>

          <p className="mt-2 text-sm text-body font-mono">
            Tiêu chuẩn học thuật chuyên sâu.
          </p>
        </div>

        {/* Clean Comparison Rows */}
        <div className="space-y-3">
          {comparisons.map((c, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-xl border transition-all duration-200 ${
                c.highlight
                  ? "bg-surface-card/90 border-[#d97757]/40 shadow-xs ring-1 ring-[#d97757]/20"
                  : "bg-surface-card/60 border-hairline hover:bg-surface-card/90"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                {/* Feature Name */}
                <div className="sm:w-1/3">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-semibold text-sm text-ink">
                      {c.feature}
                    </span>
                    {c.highlight && (
                      <Badge variant="amber" className="text-[9px] px-1.5 py-0 font-mono">
                        Key
                      </Badge>
                    )}
                  </div>
                  <div className="text-xs text-muted font-sans mt-0.5">
                    {c.detail}
                  </div>
                </div>

                {/* Comparison Values */}
                <div className="grid grid-cols-2 gap-2.5 sm:w-2/3">
                  {/* VeriScholar Side */}
                  <div className="p-2.5 rounded-lg bg-[#d97757]/10 border border-[#d97757]/30 flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-primary shrink-0 stroke-[3]" />
                    <span className="text-xs font-mono font-semibold text-primary truncate">
                      {c.verischolar}
                    </span>
                  </div>

                  {/* Generic AI Side */}
                  <div className="p-2.5 rounded-lg bg-surface-soft/80 border border-hairline flex items-center gap-2">
                    <Minus className="w-3.5 h-3.5 text-muted-soft shrink-0 stroke-[2]" />
                    <span className="text-xs font-mono text-muted truncate">
                      {c.others}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Minimal Footnote */}
        <div className="mt-6 p-3 rounded-lg bg-surface-card/60 border border-hairline flex items-center justify-between text-xs font-mono text-muted">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5 text-success shrink-0" />
            <span>Zero-Retention: Xóa dữ liệu tạm thời ngay sau phiên làm việc.</span>
          </div>
          <span className="text-muted-soft hidden sm:inline">ACID CAS</span>
        </div>
      </div>
    </section>
  );
}
