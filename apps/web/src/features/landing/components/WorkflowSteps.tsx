import { Upload, BookOpen, BrainCircuit, PenTool, ArrowRight } from "lucide-react";

export function WorkflowSteps() {
  const steps = [
    {
      number: "01",
      icon: Upload,
      title: "Ingest & Hash",
      tagline: "Bóc tách 2 cột & SHA-256 CAS",
      badge: "INGEST",
    },
    {
      number: "02",
      icon: BookOpen,
      title: "Deep Read & Ground",
      tagline: "Hybrid Search & Bounding Box",
      badge: "GROUND",
    },
    {
      number: "03",
      icon: BrainCircuit,
      title: "Socratic Synthesis",
      tagline: "Thẩm định tiền đề & Active Recall",
      badge: "SYNTHESIZE",
    },
    {
      number: "04",
      icon: PenTool,
      title: "SAFE & TeXLive",
      tagline: "Kiểm chứng sự thật & tự vá lỗi",
      badge: "VERIFY",
    },
  ];

  return (
    <section id="workflow" className="py-14 md:py-20 relative scroll-mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10">
        {/* Minimal Header */}
        <div className="text-center max-w-xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 mb-3 px-3 py-1 rounded-full bg-surface-card border border-hairline text-xs font-mono text-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
            <span className="font-semibold text-ink uppercase tracking-wider text-[11px]">Pipeline</span>
          </div>

          <h2 className="font-display text-3xl sm:text-4xl md:text-[42px] font-normal text-ink tracking-tight">
            Quy Trình 4 Bước
          </h2>

          <p className="mt-2 text-sm text-body font-mono">
            Khép kín từ nạp tài liệu đến xuất bản.
          </p>
        </div>

        {/* 4 Steps Horizontal Flow */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {steps.map((s, idx) => {
            const Icon = s.icon;
            return (
              <div
                key={idx}
                className="relative bg-surface-card/80 hover:bg-surface-card transition-all duration-300 p-5 rounded-xl border border-hairline flex flex-col justify-between group hover:-translate-y-1 hover:shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-mono text-2xl font-bold text-primary">
                      {s.number}
                    </span>
                    <div className="w-8 h-8 rounded-lg bg-surface-soft border border-hairline flex items-center justify-center text-ink group-hover:text-primary transition-colors">
                      <Icon className="w-4 h-4" />
                    </div>
                  </div>

                  <h3 className="font-display text-lg font-normal text-ink mb-1">
                    {s.title}
                  </h3>

                  <p className="text-xs font-mono text-muted leading-relaxed">
                    {s.tagline}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-hairline-soft flex items-center justify-between">
                  <span className="text-[10px] font-mono font-semibold text-muted uppercase tracking-wider">
                    {s.badge}
                  </span>
                  {idx < steps.length - 1 && (
                    <ArrowRight className="w-3.5 h-3.5 text-muted-soft hidden lg:block group-hover:translate-x-1 transition-transform" />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
