"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError, printReportPdf, type ReportPrintCategory } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { Alert, Button, Modal, ModalSection, RadioGroup } from "@/shared/ui";
import { REPORT_PERIOD_LABEL_KEY, reportPeriodRange } from "./reportPeriods";

const PRINT_PERIOD_KEYS = ["thisWeek", "thisMonth", "thisYear"] as const;
type PrintPeriodKey = (typeof PRINT_PERIOD_KEYS)[number];

const PRINT_CATEGORIES: readonly {
  value: ReportPrintCategory;
  labelKey: string;
}[] = [
  { value: "all", labelKey: "printCategoryAll" },
  { value: "created", labelKey: "printCategoryCreated" },
  { value: "resolved", labelKey: "printCategoryResolved" },
  { value: "escalated", labelKey: "printCategoryEscalated" },
  { value: "other", labelKey: "printCategoryOther" },
];

export function PrintReportDialog({
  open,
  onClose,
  branchId,
}: {
  open: boolean;
  onClose: () => void;
  branchId?: string;
}) {
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [category, setCategory] = useState<ReportPrintCategory>("all");
  const [periodKey, setPeriodKey] = useState<PrintPeriodKey>("thisMonth");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleClose() {
    if (submitting) return;
    setError(null);
    onClose();
  }

  async function submit() {
    if (submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const range = reportPeriodRange(periodKey);
      const result = await printReportPdf({
        category,
        periodLabel: t(REPORT_PERIOD_LABEL_KEY[periodKey]),
        dateFrom: range.dateFrom,
        dateTo: range.dateTo,
        branchId,
      });
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = result.filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      onClose();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("printFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={t("printReportTitle")}
      footer={
        <>
          <Button variant="outline" onClick={handleClose} disabled={submitting}>
            {tCommon("cancel")}
          </Button>
          <Button onClick={() => void submit()} disabled={submitting}>
            {submitting ? t("printGenerating") : t("printAction")}
          </Button>
        </>
      }
    >
      <ModalSection>
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("printReportDescription")}
        </p>
        {error ? (
          <Alert tone="danger" title={tCommon("requestFailed")} description={error} />
        ) : null}
        <RadioGroup
          name="printReportCategory"
          label={t("printCategoryLabel")}
          value={category}
          onChange={(value) => setCategory(value as ReportPrintCategory)}
          disabled={submitting}
          options={PRINT_CATEGORIES.map((item) => ({
            value: item.value,
            label: t(item.labelKey),
          }))}
        />
        {category === "other" ? (
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("printCategoryOtherHint")}
          </p>
        ) : null}
        <RadioGroup
          name="printReportPeriod"
          label={t("printPeriodLabel")}
          value={periodKey}
          onChange={(value) => setPeriodKey(value as PrintPeriodKey)}
          disabled={submitting}
          orientation="horizontal"
          options={PRINT_PERIOD_KEYS.map((key) => ({
            value: key,
            label: t(REPORT_PERIOD_LABEL_KEY[key]),
          }))}
        />
      </ModalSection>
    </Modal>
  );
}
