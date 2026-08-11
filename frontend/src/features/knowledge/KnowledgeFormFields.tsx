"use client";

import { type ChangeEvent } from "react";
import { useTranslations } from "next-intl";
import { Input, Select, Textarea } from "@/shared/ui";
import type { KnowledgeType } from "@/lib/api/types";
import { knowledgeTypeKey } from "./KnowledgeBadges";
import type { KnowledgeFieldErrors, KnowledgeFormValues } from "./knowledgeForm";

const KNOWLEDGE_TYPE_VALUES: readonly KnowledgeType[] = [
  "SOP",
  "PERATURAN",
  "SURAT_EDARAN",
  "KEPUTUSAN",
  "PANDUAN",
];

export function KnowledgeFormFields({
  values,
  fieldErrors,
  onChange,
  /** ACTIVE/ARCHIVED — title, jenis, and versi are locked server-side (KM §17). */
  identityLocked = false,
}: {
  values: KnowledgeFormValues;
  fieldErrors: KnowledgeFieldErrors;
  onChange: <K extends keyof KnowledgeFormValues>(
    key: K,
    value: KnowledgeFormValues[K],
  ) => void;
  identityLocked?: boolean;
}) {
  const t = useTranslations("knowledge");
  const tValidation = useTranslations("validation");

  function fieldLabel(key: keyof KnowledgeFormValues): string {
    switch (key) {
      case "title":
        return t("fieldTitleLabel");
      case "knowledgeType":
        return t("fieldTypeLabel");
      case "documentNumber":
        return t("fieldDocumentNumberLabel");
      case "versionLabel":
        return t("fieldVersionLabel");
      case "summary":
        return t("fieldSummaryLabel");
      case "effectiveFrom":
        return t("fieldEffectiveFromLabel");
      default:
        return t("fieldEffectiveToLabel");
    }
  }

  function errorMessage(code: string): string {
    switch (code) {
      case "knowledgeTitleMax":
        return t("knowledgeTitleMax");
      case "knowledgeEffectiveFromInvalid":
        return t("knowledgeEffectiveFromInvalid");
      case "knowledgeEffectiveToInvalid":
        return t("knowledgeEffectiveToInvalid");
      case "knowledgeEffectiveToBeforeFrom":
        return t("knowledgeEffectiveToBeforeFrom");
      default:
        return code;
    }
  }

  const fieldError = (key: keyof KnowledgeFormValues): string | undefined => {
    const code = fieldErrors[key];
    if (!code) return undefined;
    if (code === "required") {
      return tValidation("required", { field: fieldLabel(key) });
    }
    return errorMessage(code);
  };

  const typeOptions = KNOWLEDGE_TYPE_VALUES.map((value) => ({
    value,
    label: t(knowledgeTypeKey(value)),
  }));

  return (
    <div className="space-y-[var(--ecmp-form-gap)]">
      {identityLocked ? (
        <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          {t("identityLockedHint")}
        </p>
      ) : null}
      <Input
        label={t("fieldTitleLabel")}
        value={values.title}
        onChange={(e: ChangeEvent<HTMLInputElement>) => onChange("title", e.target.value)}
        error={fieldError("title")}
        required
        maxLength={200}
        disabled={identityLocked}
      />
      <div className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2">
        <Select
          label={t("fieldTypeLabel")}
          value={values.knowledgeType}
          onChange={(e) => onChange("knowledgeType", e.target.value as KnowledgeType)}
          options={typeOptions}
          disabled={identityLocked}
        />
        <Input
          label={t("fieldVersionLabel")}
          placeholder={t("fieldVersionPlaceholder")}
          value={values.versionLabel}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            onChange("versionLabel", e.target.value)
          }
          disabled={identityLocked}
        />
      </div>
      <Input
        label={t("fieldDocumentNumberLabel")}
        placeholder={t("fieldDocumentNumberPlaceholder")}
        value={values.documentNumber}
        onChange={(e: ChangeEvent<HTMLInputElement>) =>
          onChange("documentNumber", e.target.value)
        }
      />
      <Textarea
        label={t("fieldSummaryLabel")}
        value={values.summary}
        onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
          onChange("summary", e.target.value)
        }
        rows={4}
      />
      <div className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2">
        <Input
          type="datetime-local"
          label={t("fieldEffectiveFromLabel")}
          value={values.effectiveFrom}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            onChange("effectiveFrom", e.target.value)
          }
          error={fieldError("effectiveFrom")}
        />
        <Input
          type="datetime-local"
          label={t("fieldEffectiveToLabel")}
          value={values.effectiveTo}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            onChange("effectiveTo", e.target.value)
          }
          error={fieldError("effectiveTo")}
        />
      </div>
    </div>
  );
}
