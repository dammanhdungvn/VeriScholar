import { evaluatePasswordStrength } from "../hooks/usePasswordValidation";
import { cn } from "@/lib/utils";

export interface PasswordStrengthMeterProps {
  password: string;
  className?: string;
}

export function PasswordStrengthMeter({ password, className }: PasswordStrengthMeterProps) {
  if (!password) return null;

  const strength = evaluatePasswordStrength(password);

  return (
    <div className={cn("mt-1.5 space-y-1 font-sans select-none", className)}>
      {/* Sleek 2px segmented progress bar */}
      <div className="flex items-center gap-1.5">
        {[1, 2, 3, 4].map((tier) => (
          <div
            key={tier}
            className={cn(
              "h-1 flex-1 rounded-full transition-all duration-300",
              tier <= strength.score ? strength.colorClass : "bg-hairline dark:bg-[#332f28]"
            )}
          />
        ))}
      </div>

      <div className="flex items-center justify-between text-3xs text-muted dark:text-[#9c988f]">
        <span>Độ an toàn:</span>
        <div className="flex items-center gap-1.5">
          <span
            className={cn(
              "font-medium",
              strength.score <= 1 && "text-error",
              strength.score === 2 && "text-amber-500",
              strength.score === 3 && "text-accent-teal",
              strength.score >= 4 && "text-success"
            )}
          >
            {strength.label}
          </span>
          {strength.entropy > 0 && (
            <span className="text-muted/70 dark:text-[#787369] font-mono">
              ({strength.entropy} bits)
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
