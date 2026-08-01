"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { subscribeLoading } from "@/lib/api/client";

/**
 * Top progress bar driven by Axios pending-request count.
 * Visible whenever at least one API call is in flight.
 */
export function GlobalLoadingBar() {
  const t = useTranslations("common");
  const [pending, setPending] = useState(0);

  useEffect(() => subscribeLoading(setPending), []);

  if (pending <= 0) return null;

  return (
    <div
      className="pointer-events-none fixed inset-x-0 top-0 z-[70] h-0.5 overflow-hidden"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuetext={t("loading")}
      aria-busy="true"
    >
      <div className="ecmp-global-loading-bar h-full w-1/3 bg-ecmp-primary" />
    </div>
  );
}
