"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError, printReportPdf, type ReportPrintCategory } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { Alert, Button, Modal, ModalSection, RadioGroup, Select } from "@/shared/ui";
import {
  DEFAULT_REPORT_PERIOD,
  REPORT_PERIOD_KEYS,
  REPORT_PERIOD_LABEL_KEY,
  reportPeriodRange,
  type ReportPeriodKey,
} from "./reportPeriods";

const PRINT_CATEGORIES: readonly {
  value: ReportPrintCategory;
  labelKey: string;
}[] = [
  { value: "all", labelKey: "printCategoryAll" },
  { value: "created", labelKey: "printCategoryCreated" },
  { value: "resolved", labelKey: "printCategoryResolved" },
  { value: "escalated", labelKey: "printCategoryEscalated" },
];

export function PrintReportDialog({
  open,
  onClose,
  period = DEFAULT_REPORT_PERIOD,
  branchId,
}: {
  open: boolean;
  onClose: () => void;
  period?: ReportPeriodKey;
  branchId?: string;
}) {
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [category, setCategory] = useState<ReportPrintCategory>("all");
  const [periodKey, setPeriodKey] = useState<ReportPeriodKey>(period);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setPeriodKey(period);
    setError(null);
  }, [open, period]);

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
        <Select
          name="printReportPeriod"
          label={t("printPeriodLabel")}
          value={periodKey}
          disabled={submitting}
          onChange={(e) => setPeriodKey(e.target.value as ReportPeriodKey)}
          options={REPORT_PERIOD_KEYS.map((key) => ({
            value: key,
            label: t(REPORT_PERIOD_LABEL_KEY[key]),
          }))}
        />
      </ModalSection>
    </Modal>
  );
}
