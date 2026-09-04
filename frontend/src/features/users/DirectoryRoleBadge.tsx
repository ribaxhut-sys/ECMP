"use client";

import { useTranslations } from "next-intl";
import type { UserRef } from "@/lib/api";
import { Badge } from "@/shared/ui";
import {
  directoryRoleFamily,
  directoryRoleLabel,
  directoryRoleTone,
  type DirectoryRoleFamily,
} from "./directoryHelpers";

export function DirectoryRoleBadge({
  user,
}: {
  user: Pick<UserRef, "roleCode" | "roleName">;
}) {
  const t = useTranslations("users");
  const tCommon = useTranslations("common");
  const family = directoryRoleFamily(user);
  const labels: Record<DirectoryRoleFamily, string> = {
    administrator: t("roleAdministrator"),
    manager: t("roleManager"),
    supervisor: t("roleSupervisor"),
    officer: t("roleAgent"),
    viewer: t("roleViewer"),
    other: tCommon("emDash"),
  };

  return (
    <Badge tone={directoryRoleTone(family)} variant="soft">
      {directoryRoleLabel(user, labels, tCommon("emDash"))}
    </Badge>
  );
}
