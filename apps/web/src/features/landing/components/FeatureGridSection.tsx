import { Target, Compass, Terminal, ArrowRight, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function FeatureGridSection() {
  const features = [
    {
      id: "visual-grounding",
      icon: Target,
      badge: "Module 1",
      accent: "#d97757",
      title: "Visual Grounding",
      subtitle: "Bảo Chứng Tọa Độ Nhị Phân",
      points: [
        "Bounding Box [x0, y0, x1, y1, page]",
        "Dynamic Viewport Matrix (Zoom 50% — 300%)",
        "Table Stitching & Composite Math Box",
      ],
    },
    {
      id: "socratic-mentor",
      icon: Compass,
      badge: "Module 1",
      accent: "#e8a55a",
      title: "Socratic Mentorship",
      subtitle: "Thẩm Định Tiền Đề & Phản Biện",
      points: [
        "Presupposition Validation Engine",
        "Abstention Guardrail (Rerank Score < 0.35)",
        "Active Recall Quiz & Flashcard Synthesis",
      ],
    },
    {
      id: "safe-fact-check",
      icon: Terminal,
      badge: "Module 2",
      accent: "#5db8a6",
      title: "SAFE & TeXLive Sandbox",
      subtitle: "Kiểm Chứng Khẳng Định & Tự Vá Lỗi",
      points: [
        "DeepMind SAFE Atomic Claims NLI",
        "Agentic Self-Healing LaTeX Compiler",
        "BibTeX Strict Syntax Synchronization",
      ],
    },
  ];

  return (
    <section id="features" className="py-14 md:py-20 relative scroll-mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10">
        {/* Minimalist Section Header */}
        <div className="text-center max-w-xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 mb-3 px-3 py-1 rounded-full bg-surface-card border border-hairline text-xs font-mono text-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
            <span className="font-semibold text-ink uppercase tracking-wider text-[11px]">3 Trụ Cột Kỹ Thuật</span>
          </div>

          <h2 className="font-display text-3xl sm:text-4xl md:text-[42px] font-normal text-ink tracking-tight">
            Năng Lực Cốt Lõi
          </h2>

          <p className="mt-2 text-sm text-body font-mono">
            Chuẩn mực học thuật khắt khe.
          </p>
        </div>

        {/* 3-Up Feature Cards - Keyword Centric */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {features.map((f) => {
            const Icon = f.icon;
            return (
              <div
                key={f.id}
                className="relative bg-surface-card/90 hover:bg-surface-cream-strong/70 transition-all duration-300 rounded-xl p-6 border border-hairline shadow-xs flex flex-col justify-between group hover:-translate-y-1 hover:shadow-md"
              >
                {/* Top Accent Line */}
                <div
                  className="absolute top-0 left-6 right-6 h-0.5 rounded-full transition-opacity opacity-0 group-hover:opacity-100 duration-300"
                  style={{ backgroundColor: f.accent }}
                />

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center transition-transform group-hover:scale-105"
                      style={{
                        backgroundColor: `${f.accent}18`,
                        color: f.accent,
                        border: `1px solid ${f.accent}30`,
                      }}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <Badge variant="outline" className="text-[11px] bg-canvas/80 font-mono">
                      {f.badge}
                    </Badge>
                  </div>

                  <h3 className="font-display text-xl text-ink leading-snug">
                    {f.title}
                  </h3>
                  <div className="text-xs font-mono text-muted mb-5">
                    {f.subtitle}
                  </div>

                  <ul className="space-y-3 pt-3 border-t border-hairline-soft">
                    {f.points.map((pt, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-xs text-body font-mono">
                        <div className="w-4 h-4 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0 mt-0.5">
                          <Check className="w-2.5 h-2.5 stroke-[2.5]" />
                        </div>
                        <span className="leading-snug">{pt}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-6 pt-3.5 border-t border-hairline flex items-center gap-1.5 text-xs font-mono font-medium text-primary group-hover:translate-x-1 transition-transform">
                  <span>Architecture Specs</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
