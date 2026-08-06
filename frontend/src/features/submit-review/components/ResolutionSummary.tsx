"use client";

import { useTranslations } from "next-intl";
import { Textarea } from "@/shared/ui";

export interface ResolutionSummaryProps {
  value: string;
  error?: string;
  onChange: (value: string) => void;
}

/** Resolution summary input (SCR-WS-05). */
export function ResolutionSummary({
  value,
  error,
  onChange,
}: ResolutionSummaryProps) {
  const t = useTranslations("submitReview");

  return (
    <Textarea
      id="b4-resolution-summary"
      name="resolutionSummary"
      label={t("resolutionLabel")}
      description={t("resolutionHint")}
      required
      rows={5}
      value={value}
      error={error}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
