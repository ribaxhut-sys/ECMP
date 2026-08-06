"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Alert, Button, Card, CardBody, CardHeader, Textarea } from "@/shared/ui";
import type { MockProgressNote } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface ProgressNotesPanelProps {
  notes: readonly MockProgressNote[];
  canRecord: boolean;
  onRecord: (text: string) => { ok: boolean; errorKey?: string };
}

/** Current work — progress notes (SCR-WS-04). Not a Timeline / Comment Panel. */
export function ProgressNotesPanel({
  notes,
  canRecord,
  onRecord,
}: ProgressNotesPanelProps) {
  const t = useTranslations("officerHandle");
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  function submit(): void {
    setSaved(false);
    const result = onRecord(draft);
    if (!result.ok) {
      setError(result.errorKey ? t(result.errorKey) : t("progressEmpty"));
      return;
    }
    setError(null);
    setDraft("");
    setSaved(true);
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
          {t("progressTitle")}
        </h2>
      </CardHeader>
      <CardBody className="space-y-4">
        {notes.length === 0 ? (
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("progressEmptyList")}
          </p>
        ) : (
          <ul className="space-y-3">
            {notes.map((note) => (
              <li
                key={note.id}
                className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-ecmp-surface-sunken/40 p-3"
              >
                <p className="text-ecmp-text-primary">{note.text}</p>
                <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                  {new Date(note.recordedAt).toLocaleString()}
                </p>
              </li>
            ))}
          </ul>
        )}

        {canRecord ? (
          <div className="space-y-3 border-t border-ecmp-border/70 pt-4">
            <Textarea
              id="b2-progress-note"
              name="progressNote"
              label={t("progressInputLabel")}
              description={t("progressInputHint")}
              value={draft}
              rows={3}
              onChange={(event) => {
                setDraft(event.target.value);
                setError(null);
                setSaved(false);
              }}
            />
            {error ? <Alert tone="danger" title={error} /> : null}
            {saved ? (
              <Alert tone="info" title={t("progressSaved")} />
            ) : null}
            <div className="flex justify-end">
              <Button type="button" variant="primary" onClick={submit}>
                {t("recordProgress")}
              </Button>
            </div>
          </div>
        ) : (
          <Alert tone="info" title={t("progressStartFirst")} />
        )}
      </CardBody>
    </Card>
  );
}
