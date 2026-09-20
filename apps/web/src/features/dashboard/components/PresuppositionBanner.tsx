import { ShieldAlert, Compass } from "lucide-react";
import type { PresuppositionAlertData } from "@/types/dashboard";
import { useDashboardStore } from "../stores/useDashboardStore";

interface PresuppositionBannerProps {
  alert: PresuppositionAlertData;
}

export function PresuppositionBanner({ alert }: PresuppositionBannerProps) {
  const setActiveBbox = useDashboardStore((s) => s.setActiveBbox);

  return (
    <div className="my-3 p-3.5 rounded-xl border border-amber-500/30 bg-amber-500/10 dark:bg-amber-950/20 text-ink dark:text-zinc-200 space-y-2 text-xs">
      <div className="flex items-center gap-2 font-medium text-amber-700 dark:text-amber-400">
        <ShieldAlert className="w-4 h-4 shrink-0" />
        <span className="font-sans font-semibold uppercase tracking-wider text-2xs">
          Thẩm Định Tiền Đề Socratic
        </span>
      </div>

      <div className="space-y-1 font-sans pl-6 border-l-2 border-amber-500/40 text-2xs sm:text-xs">
        <div>
          <span className="text-muted dark:text-zinc-400">Tiền đề câu hỏi:</span>{" "}
          <span className="line-through opacity-75">{alert.flawed_premise}</span>
        </div>
        <div>
          <span className="text-muted dark:text-zinc-400">Thực tế tài liệu:</span>{" "}
          <span className="font-medium text-amber-900 dark:text-amber-200">
            {alert.correction}
          </span>
        </div>
      </div>

      <div className="flex justify-end pt-1">
        <button
          type="button"
          onClick={() => setActiveBbox(alert.grounded_bbox)}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/20 hover:bg-amber-500/30 text-amber-800 dark:text-amber-300 font-mono text-2xs transition-colors cursor-pointer"
        >
          <Compass className="w-3 h-3" />
          <span>Kiểm chứng tại Trang {alert.page}</span>
        </button>
      </div>
    </div>
  );
}
