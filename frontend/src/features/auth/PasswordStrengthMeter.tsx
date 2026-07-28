import { cn } from "@/shared/utils";
import {
  evaluatePasswordStrength,
  type PasswordStrengthLevel,
} from "./passwordPolicy";

const barTone: Record<PasswordStrengthLevel, string> = {
  empty: "bg-ecmp-border",
  weak: "bg-ecmp-danger",
  fair: "bg-ecmp-warning",
  good: "bg-ecmp-info",
  strong: "bg-ecmp-success",
};

const fillWidth: Record<PasswordStrengthLevel, string> = {
  empty: "w-0",
  weak: "w-1/4",
  fair: "w-2/4",
  good: "w-3/4",
  strong: "w-full",
};

export function PasswordStrengthMeter({ password }: { password: string }) {
  const strength = evaluatePasswordStrength(password);

  return (
    <div className="space-y-1" aria-live="polite">
      <div
        className="h-1.5 w-full overflow-hidden rounded-full bg-ecmp-border"
        role="meter"
        aria-label="Password strength"
        aria-valuemin={0}
        aria-valuemax={5}
        aria-valuenow={strength.score}
        aria-valuetext={strength.label}
      >
        <div
          className={cn(
            "h-full transition-all duration-200",
            barTone[strength.level],
            fillWidth[strength.level],
          )}
        />
      </div>
      <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
        Strength: {strength.label}
      </p>
    </div>
  );
}
