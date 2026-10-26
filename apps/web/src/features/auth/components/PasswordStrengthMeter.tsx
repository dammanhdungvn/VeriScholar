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
    <div className={cn("mt-1.5 font-sans select-none", className)}>
      {/* Sleek segmented progress bar */}
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
    </div>
  );
}
