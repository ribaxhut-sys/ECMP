"use client";

import { type ChangeEvent, type ReactNode } from "react";
import { useTranslations } from "next-intl";
import { Input, Select, Textarea } from "@/shared/ui";
import type {
  AnnouncementFieldErrors,
  AnnouncementFormValues,
} from "./announcementForm";

export function AnnouncementFormFields({
  values,
  fieldErrors,
  onChange,
  attachmentSlot,
  showStartAt = true,
}: {
  values: AnnouncementFormValues;
  fieldErrors: AnnouncementFieldErrors;
  onChange: <K extends keyof AnnouncementFormValues>(
    key: K,
    value: AnnouncementFormValues[K],
  ) => void;
  /** Below the meta row (Prioritas | Mulai | Berakhir). */
  attachmentSlot?: ReactNode;
  /** Create/publish and scheduled edit show startAt; draft edit may hide it. */
  showStartAt?: boolean;
}) {
  const t = useTranslations("announcements");
  const tValidation = useTranslations("validation");

  function fieldLabel(key: keyof AnnouncementFormValues): string {
    switch (key) {
      case "title":
        return t("fieldTitleLabel");
      case "body":
        return t("fieldBodyLabel");
      case "priority":
        return t("fieldPriorityLabel");
      case "startAt":
        return t("fieldStartAtLabel");
      default:
        return t("fieldEndAtLabel");
    }
  }

  function errorMessage(code: string): string {
    switch (code) {
      case "announcementTitleMax":
        return t("announcementTitleMax");
      case "announcementStartAtInvalid":
        return t("announcementStartAtInvalid");
      case "announcementStartBeforeEnd":
        return t("announcementStartBeforeEnd");
      case "announcementEndAtInvalid":
        return t("announcementEndAtInvalid");
      default:
        return code;
    }
  }

  const fieldError = (key: keyof AnnouncementFormValues): string | undefined => {
    const code = fieldErrors[key];
    if (!code) return undefined;
    if (code === "required") {
      return tValidation("required", { field: fieldLabel(key) });
    }
    return errorMessage(code);
  };

  return (
    <div className="space-y-[var(--ecmp-form-gap)]">
      <Input
        label={t("fieldTitleLabel")}
        value={values.title}
        onChange={(e: ChangeEvent<HTMLInputElement>) =>
          onChange("title", e.target.value)
        }
        error={fieldError("title")}
        required
        maxLength={200}
      />
      <Textarea
        label={t("fieldBodyLabel")}
        value={values.body}
        onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
          onChange("body", e.target.value)
        }
        error={fieldError("body")}
        required
        rows={10}
      />
      <div className="grid grid-cols-1 items-start gap-[var(--ecmp-form-gap)] md:grid-cols-3">
        <Select
          label={t("fieldPriorityLabel")}
          value={values.priority}
          onChange={(e) =>
            onChange(
              "priority",
              e.target.value as AnnouncementFormValues["priority"],
            )
          }
          options={[
            { value: "NORMAL", label: t("priorityNormal") },
            { value: "IMPORTANT", label: t("priorityImportant") },
          ]}
        />
        {showStartAt ? (
          <Input
            type="datetime-local"
            label={t("fieldStartAtLabel")}
            helper={t("fieldStartAtHelper")}
            value={values.startAt}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange("startAt", e.target.value)
            }
            error={fieldError("startAt")}
          />
        ) : null}
        <Input
          type="datetime-local"
          label={t("fieldEndAtLabel")}
          helper={t("fieldEndAtHelper")}
          value={values.endAt}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            onChange("endAt", e.target.value)
          }
          error={fieldError("endAt")}
        />
      </div>
      {attachmentSlot ? (
        <div className="min-w-0">{attachmentSlot}</div>
      ) : null}
    </div>
  );
}
