"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  Input,
} from "@/shared/ui";
import type { MockEvidenceItem } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface EvidenceListMinProps {
  items: readonly MockEvidenceItem[];
  canAdd: boolean;
  onAdd: (fileName: string) => { ok: boolean; errorKey?: string };
}

/**
 * C-EVID-MIN — filename + attach status only.
 * Not formal Evidence Supporting Views (R2).
 */
export function EvidenceListMin({
  items,
  canAdd,
  onAdd,
}: EvidenceListMinProps) {
  const t = useTranslations("submitReview");
  const [fileName, setFileName] = useState("");
  const [error, setError] = useState<string | null>(null);

  function submitAdd(): void {
    const result = onAdd(fileName);
    if (!result.ok) {
      setError(result.errorKey ? t(result.errorKey) : t("evidenceAddEmpty"));
      return;
    }
    setError(null);
    setFileName("");
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
          {t("evidenceTitle")}
        </h2>
        <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("evidenceHint")}
        </p>
      </CardHeader>
      <CardBody className="space-y-4">
        {items.length === 0 ? (
          <Alert tone="warning" title={t("evidenceEmptyWarning")} />
        ) : (
          <ul className="space-y-2">
            {items.map((item) => (
              <li
                key={item.id}
                className="flex items-center justify-between gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 px-3 py-2"
              >
                <span className="truncate text-ecmp-text-primary">
                  {item.fileName}
                </span>
                <Badge
                  tone={item.status === "ATTACHED" ? "success" : "warning"}
                  variant="outline"
                >
                  {t(`evidenceStatus.${item.status}`)}
                </Badge>
              </li>
            ))}
          </ul>
        )}

        {canAdd ? (
          <div className="space-y-3 border-t border-ecmp-border/70 pt-4">
            <Input
              id="b4-evidence-filename"
              name="evidenceFileName"
              label={t("evidenceAddLabel")}
              description={t("evidenceAddHint")}
              value={fileName}
              onChange={(event) => {
                setFileName(event.target.value);
                setError(null);
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  submitAdd();
                }
              }}
            />
            {error ? <Alert tone="danger" title={error} /> : null}
            <div className="flex justify-end">
              <Button type="button" variant="secondary" onClick={submitAdd}>
                {t("evidenceAdd")}
              </Button>
            </div>
          </div>
        ) : null}
      </CardBody>
    </Card>
  );
}
