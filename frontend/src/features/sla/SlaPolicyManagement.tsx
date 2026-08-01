"use client";

import {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  activateSlaPolicy,
  createSlaPolicy,
  fetchSlaPolicies,
} from "@/lib/api";
import type { SlaPolicy } from "@/lib/api/types";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Empty,
  ErrorState,
  Input,
  Skeleton,
  Table,
  Textarea,
  type TableColumn,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  createEmptySlaPolicyForm,
  toSlaPolicyCreateRequest,
  validateSlaPolicyForm,
  type SlaPolicyFieldErrors,
  type SlaPolicyFormValues,
} from "./slaPolicyForm";

export function SlaPolicyManagement() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();
  const canRead = hasPermission("sla:read");
  const canManage = hasPermission("sla:manage");

  const [policies, setPolicies] = useState<SlaPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [activatingId, setActivatingId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [values, setValues] = useState<SlaPolicyFormValues>(
    createEmptySlaPolicyForm,
  );
  const [fieldErrors, setFieldErrors] = useState<SlaPolicyFieldErrors>({});
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      setPolicies([]);
      setLoadError(null);
      return;
    }
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchSlaPolicies();
      setPolicies(res.data);
    } catch (err) {
      setPolicies([]);
      setLoadError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoadPolicies"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  function onFieldChange(
    key: keyof SlaPolicyFormValues,
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) {
    const next = event.target.value;
    setValues((prev) => ({ ...prev, [key]: next }));
    setFieldErrors((prev) => {
      if (!prev[key]) return prev;
      const copy = { ...prev };
      delete copy[key];
      return copy;
    });
  }

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    if (!canManage) return;
    setActionError(null);
    setActionSuccess(null);
    const errors = validateSlaPolicyForm(values);
    const fieldLabels: Partial<Record<keyof SlaPolicyFormValues, string>> = {
      assignmentTargetMinutes: t("assignmentTargetFieldLabel"),
      appointmentTargetMinutes: t("appointmentTargetFieldLabel"),
      resolutionTargetMinutes: t("resolutionTargetFieldLabel"),
      escalationTargetMinutes: t("escalationTargetFieldLabel"),
      overallTargetMinutes: t("overallTargetFieldLabel"),
    };
    setFieldErrors(
      Object.fromEntries(
        Object.entries(errors).map(([field, key]) => {
          const label = fieldLabels[field as keyof SlaPolicyFormValues];
          if (key === "required" && label) {
            return [field, tValidation("required", { field: label })];
          }
          if (key === "fieldWholeNumber" && label) {
            return [field, tValidation("fieldWholeNumber", { field: label })];
          }
          if (key === "fieldAtLeast" && label) {
            return [field, tValidation("fieldAtLeast", { field: label, min: 1 })];
          }
          if (key === "policyNameMax") {
            return [field, tValidation(key, { max: 100 })];
          }
          return [field, tValidation(key!)];
        }),
      ),
    );
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      await createSlaPolicy(toSlaPolicyCreateRequest(values));
      setValues(createEmptySlaPolicyForm());
      setShowCreate(false);
      setActionSuccess(t("policyCreatedSuccess"));
      await load();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToCreatePolicy"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function onActivate(policy: SlaPolicy) {
    if (!canManage || policy.isActive) return;
    setActionError(null);
    setActionSuccess(null);
    setActivatingId(policy.id);
    try {
      await activateSlaPolicy(policy.id);
      setActionSuccess(t("nowActiveMessage", { name: policy.name }));
      await load();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToActivatePolicy"),
      );
    } finally {
      setActivatingId(null);
    }
  }

  if (!canRead) {
    return (
      <Empty
        title={tCommon("accessRestricted")}
        description={t("accessRestrictedSla")}
      />
    );
  }

  const columns: TableColumn<SlaPolicy>[] = [
    {
      key: "name",
      header: t("nameColumn"),
      cell: (row) => (
        <div className="space-y-1">
          <div className="font-medium text-ecmp-text-primary">{row.name}</div>
          {row.description ? (
            <div className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {row.description}
            </div>
          ) : null}
        </div>
      ),
    },
    {
      key: "assignment",
      header: t("assignmentTargetColumn"),
      cell: (row) => formatTargetMinutes(row.assignmentTargetMinutes, t),
    },
    {
      key: "appointment",
      header: t("appointmentTargetColumn"),
      cell: (row) => formatTargetMinutes(row.appointmentTargetMinutes, t),
    },
    {
      key: "resolution",
      header: t("resolutionTargetColumn"),
      cell: (row) => formatTargetMinutes(row.resolutionTargetMinutes, t),
    },
    {
      key: "escalation",
      header: t("escalationTargetColumn"),
      cell: (row) => formatTargetMinutes(row.escalationTargetMinutes, t),
    },
    {
      key: "overall",
      header: t("overallTargetColumn"),
      cell: (row) => formatTargetMinutes(row.overallTargetMinutes, t),
    },
    {
      key: "active",
      header: tCommon("status"),
      cell: (row) =>
        row.isActive ? (
          <Badge tone="success" data-testid="sla-policy-active-badge">
            {tCommon("active")}
          </Badge>
        ) : (
          <Badge tone="neutral">{tCommon("inactive")}</Badge>
        ),
    },
    {
      key: "actions",
      header: tCommon("actions"),
      hideOnMobile: !canManage,
      cell: (row) =>
        canManage && !row.isActive ? (
          <Button
            type="button"
            size="sm"
            variant="secondary"
            disabled={activatingId === row.id}
            onClick={() => void onActivate(row)}
          >
            {activatingId === row.id ? t("activating") : t("activate")}
          </Button>
        ) : (
          <span className="text-ecmp-text-secondary">—</span>
        ),
    },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-1">
            <CardTitle>{t("managementTitle")}</CardTitle>
            <CardDescription>
              {t("managementDescription")}
            </CardDescription>
          </div>
          {canManage ? (
            <Button
              type="button"
              onClick={() => {
                setShowCreate((prev) => !prev);
                setActionError(null);
                setActionSuccess(null);
              }}
            >
              {showCreate ? tCommon("cancel") : t("createPolicy")}
            </Button>
          ) : null}
        </CardHeader>
        <CardBody className="space-y-4">
          {actionError ? (
            <Alert
              tone="danger"
              title={t("actionFailed")}
              description={actionError}
            />
          ) : null}
          {actionSuccess ? (
            <Alert
              tone="success"
              title={tCommon("success")}
              description={actionSuccess}
            />
          ) : null}

          {showCreate && canManage ? (
            <form
              className="space-y-4 rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-4"
              onSubmit={(event) => void onCreate(event)}
              noValidate
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <Input
                  label={t("name")}
                  value={values.name}
                  onChange={(e) => onFieldChange("name", e)}
                  error={fieldErrors.name}
                  required
                  maxLength={100}
                />
                <div className="sm:col-span-2">
                  <Textarea
                    label={t("descriptionLabel")}
                    value={values.description}
                    onChange={(e) => onFieldChange("description", e)}
                    rows={2}
                  />
                </div>
                <Input
                  label={t("assignmentTargetLabel")}
                  inputMode="numeric"
                  value={values.assignmentTargetMinutes}
                  onChange={(e) => onFieldChange("assignmentTargetMinutes", e)}
                  error={fieldErrors.assignmentTargetMinutes}
                  required
                />
                <Input
                  label={t("appointmentTargetLabel")}
                  inputMode="numeric"
                  value={values.appointmentTargetMinutes}
                  onChange={(e) => onFieldChange("appointmentTargetMinutes", e)}
                  error={fieldErrors.appointmentTargetMinutes}
                  required
                />
                <Input
                  label={t("resolutionTargetLabel")}
                  inputMode="numeric"
                  value={values.resolutionTargetMinutes}
                  onChange={(e) => onFieldChange("resolutionTargetMinutes", e)}
                  error={fieldErrors.resolutionTargetMinutes}
                  required
                />
                <Input
                  label={t("escalationTargetLabel")}
                  inputMode="numeric"
                  value={values.escalationTargetMinutes}
                  onChange={(e) => onFieldChange("escalationTargetMinutes", e)}
                  error={fieldErrors.escalationTargetMinutes}
                  required
                />
                <Input
                  label={t("overallTargetLabel")}
                  inputMode="numeric"
                  value={values.overallTargetMinutes}
                  onChange={(e) => onFieldChange("overallTargetMinutes", e)}
                  error={fieldErrors.overallTargetMinutes}
                  required
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  type="submit"
                  disabled={submitting}
                >
                  {submitting ? t("creating") : t("savePolicy")}
                </Button>
              </div>
            </form>
          ) : null}

          {loadError ? (
            <ErrorState
              title={t("unableToLoadPolicies")}
              message={loadError}
              onRetry={() => void load()}
            />
          ) : null}

          {loading ? (
            <Skeleton rows={5} />
          ) : !loadError ? (
            <Table
              columns={columns}
              rows={policies}
              getRowKey={(row) => row.id}
              caption={t("slaPoliciesCaption")}
              emptyMessage={t("noPoliciesTableMessage")}
            />
          ) : null}
        </CardBody>
      </Card>
    </div>
  );
}

function formatTargetMinutes(
  minutes: number,
  t: ReturnType<typeof useTranslations<"settings">>,
): string {
  if (minutes < 60 || minutes % 60 !== 0) {
    return t("minutesShort", { count: minutes });
  }
  return t("hoursShort", { count: minutes / 60 });
}
