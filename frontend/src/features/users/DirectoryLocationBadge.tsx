"use client";

import { useTranslations } from "next-intl";
import type { UserRef } from "@/lib/api";
import { Badge } from "@/shared/ui";
import { directoryLocationTone, userLocationKind } from "./directoryHelpers";

export function DirectoryLocationBadge({
  user,
}: {
  user: Pick<UserRef, "branchId">;
}) {
  const t = useTranslations("users");
  const kind = userLocationKind(user);

  return (
    <Badge tone={directoryLocationTone(kind)} variant="outline">
      {kind === "branch" ? t("locationBranch") : t("locationHeadOffice")}
    </Badge>
  );
}
