import { Check, Sparkles } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AVAILABLE_MODELS } from "../data/mockDashboardData";
import { useDashboardStore } from "../stores/useDashboardStore";
import type { ModelOption } from "@/types/dashboard";

export function ModelSelectorModal() {
  const isOpen = useDashboardStore((s) => s.isModelModalOpen);
  const setIsOpen = useDashboardStore((s) => s.setModelModalOpen);
  const selectedModel = useDashboardStore((s) => s.selectedModel);
  const setSelectedModel = useDashboardStore((s) => s.setSelectedModel);
  const effortLevel = useDashboardStore((s) => s.effortLevel);
  const setEffortLevel = useDashboardStore((s) => s.setEffortLevel);

  const handleSelectModel = (model: ModelOption) => {
    setSelectedModel(model);
    if (model.effortLevels && !model.effortLevels.includes(effortLevel)) {
      setEffortLevel(model.effortLevels[0]);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="max-w-md bg-canvas dark:bg-[#1e1c18] border-hairline dark:border-[#38332c] p-5">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <div className="p-1 rounded-md bg-primary/10 text-primary">
              <Sparkles className="w-4 h-4" />
            </div>
            <DialogTitle className="text-lg font-display text-ink dark:text-[#f5f3ed]">
              Lựa Chọn Mô Hình Học Thuật
            </DialogTitle>
          </div>
          <DialogDescription className="text-2xs text-muted dark:text-zinc-400">
            Tùy chọn mô hình AI chuyên trách cho từng phương pháp nghiên cứu.
          </DialogDescription>
        </DialogHeader>

        {/* Models List */}
        <div className="space-y-2 py-2">
          {AVAILABLE_MODELS.map((model) => {
            const isSelected = model.id === selectedModel.id;

            return (
              <div
                key={model.id}
                onClick={() => handleSelectModel(model)}
                className={`p-3 rounded-xl border transition-all cursor-pointer ${
                  isSelected
                    ? "border-primary bg-primary/5 dark:bg-primary/10"
                    : "border-hairline dark:border-[#332f28] hover:border-hairline/80 dark:hover:border-[#443e34] bg-surface-soft/40 dark:bg-[#22201b]"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-xs text-ink dark:text-zinc-100 font-sans">
                      {model.name}
                    </span>
                    {model.badge && (
                      <span className="px-1.5 py-0.2 rounded text-3xs font-mono bg-primary/20 text-primary border border-primary/30">
                        {model.badge}
                      </span>
                    )}
                  </div>
                  {isSelected && <Check className="w-3.5 h-3.5 text-primary" />}
                </div>
                <p className="text-3xs text-muted dark:text-zinc-400 font-sans mt-1">
                  {model.description}
                </p>
              </div>
            );
          })}
        </div>

        {/* Effort Level Selection */}
        {selectedModel.effortLevels && selectedModel.effortLevels.length > 1 && (
          <div className="pt-2 border-t border-hairline dark:border-[#2d2b27] space-y-1.5">
            <div className="text-3xs font-mono font-medium text-muted dark:text-zinc-400 uppercase tracking-wider">
              Mức độ suy luận (Reasoning Effort):
            </div>
            <div className="flex gap-2">
              {selectedModel.effortLevels.map((lvl) => (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => setEffortLevel(lvl)}
                  className={`flex-1 py-1 px-2 rounded-lg text-2xs font-sans transition-all cursor-pointer border ${
                    effortLevel === lvl
                      ? "bg-primary text-on-primary border-primary shadow-2xs font-medium"
                      : "bg-surface-soft dark:bg-[#25231e] text-muted hover:text-ink dark:text-zinc-300 border-hairline dark:border-zinc-700/60"
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>
        )}

        <DialogFooter className="pt-2">
          <Button
            type="button"
            variant="primary"
            size="sm"
            onClick={() => setIsOpen(false)}
            className="w-full text-xs"
          >
            Xác nhận
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
