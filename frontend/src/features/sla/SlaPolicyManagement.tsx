"use client";

import {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
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
  Input,
  Table,
  Textarea,
  type TableColumn,
} from "@/shared/ui";
import {
  createEmptySlaPolicyForm,
  formatTargetMinutes,
  toSlaPolicyCreateRequest,
  validateSlaPolicyForm,
  type SlaPolicyFieldErrors,
  type SlaPolicyFormValues,
} from "./slaPolicyForm";

export function SlaPolicyManagement() {
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
        err instanceof ApiError
          ? err.message
          : "Unable to load SLA policies.",
      );
    } finally {
      setLoading(false);
    }
  }, [canRead]);

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
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      await createSlaPolicy(toSlaPolicyCreateRequest(values));
      setValues(createEmptySlaPolicyForm());
      setShowCreate(false);
      setActionSuccess("Policy created. Activate it to apply to future complaints.");
      await load();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : "Unable to create policy.",
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
      setActionSuccess(`“${policy.name}” is now the active SLA policy.`);
      await load();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : "Unable to activate policy.",
      );
    } finally {
      setActivatingId(null);
    }
  }

  if (!canRead) {
    return (
      <Alert
        tone="warning"
        title="Access restricted"
        description={
          <>
            You need the <code>sla:read</code> permission to view SLA policies.
          </>
        }
      />
    );
  }

  const columns: TableColumn<SlaPolicy>[] = [
    {
      key: "name",
      header: "Name",
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
      header: "Assignment Target",
      cell: (row) => formatTargetMinutes(row.assignmentTargetMinutes),
    },
    {
      key: "appointment",
      header: "Appointment Target",
      cell: (row) => formatTargetMinutes(row.appointmentTargetMinutes),
    },
    {
      key: "resolution",
      header: "Resolution Target",
      cell: (row) => formatTargetMinutes(row.resolutionTargetMinutes),
    },
    {
      key: "escalation",
      header: "Escalation Target",
      cell: (row) => formatTargetMinutes(row.escalationTargetMinutes),
    },
    {
      key: "overall",
      header: "Overall Target",
      cell: (row) => formatTargetMinutes(row.overallTargetMinutes),
    },
    {
      key: "active",
      header: "Status",
      cell: (row) =>
        row.isActive ? (
          <Badge tone="success" data-testid="sla-policy-active-badge">
            Active
          </Badge>
        ) : (
          <Badge tone="neutral">Inactive</Badge>
        ),
    },
    {
      key: "actions",
      header: "Actions",
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
            {activatingId === row.id ? "Activating…" : "Activate"}
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
            <CardTitle>SLA Policy Management</CardTitle>
            <CardDescription>
              Configure reusable target durations for lifecycle stages. Only one
              policy may be active. Changes apply to future complaints only.
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
              {showCreate ? "Cancel" : "Create Policy"}
            </Button>
          ) : null}
        </CardHeader>
        <CardBody className="space-y-4">
          {actionError ? (
            <Alert
              tone="danger"
              title="Action failed"
              description={actionError}
            />
          ) : null}
          {actionSuccess ? (
            <Alert
              tone="success"
              title="Success"
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
                  label="Name"
                  value={values.name}
                  onChange={(e) => onFieldChange("name", e)}
                  error={fieldErrors.name}
                  required
                  maxLength={100}
                />
                <div className="sm:col-span-2">
                  <Textarea
                    label="Description"
                    value={values.description}
                    onChange={(e) => onFieldChange("description", e)}
                    rows={2}
                  />
                </div>
                <Input
                  label="Assignment Target (minutes)"
                  inputMode="numeric"
                  value={values.assignmentTargetMinutes}
                  onChange={(e) => onFieldChange("assignmentTargetMinutes", e)}
                  error={fieldErrors.assignmentTargetMinutes}
                  required
                />
                <Input
                  label="Appointment Target (minutes)"
                  inputMode="numeric"
                  value={values.appointmentTargetMinutes}
                  onChange={(e) => onFieldChange("appointmentTargetMinutes", e)}
                  error={fieldErrors.appointmentTargetMinutes}
                  required
                />
                <Input
                  label="Resolution Target (minutes)"
                  inputMode="numeric"
                  value={values.resolutionTargetMinutes}
                  onChange={(e) => onFieldChange("resolutionTargetMinutes", e)}
                  error={fieldErrors.resolutionTargetMinutes}
                  required
                />
                <Input
                  label="Escalation Target (minutes)"
                  inputMode="numeric"
                  value={values.escalationTargetMinutes}
                  onChange={(e) => onFieldChange("escalationTargetMinutes", e)}
                  error={fieldErrors.escalationTargetMinutes}
                  required
                />
                <Input
                  label="Overall Target (minutes)"
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
                  {submitting ? "Creating…" : "Save Policy"}
                </Button>
              </div>
            </form>
          ) : null}

          {loadError ? (
            <Alert
              tone="danger"
              title="Unable to load policies"
              description={loadError}
              actionLabel="Retry"
              onAction={() => void load()}
            />
          ) : null}

          {loading ? (
            <p className="text-ecmp-text-secondary">Loading policies…</p>
          ) : (
            <Table
              columns={columns}
              rows={policies}
              getRowKey={(row) => row.id}
              caption="SLA policies"
              emptyMessage="No SLA policies yet. Create one to define target durations."
            />
          )}
        </CardBody>
      </Card>
    </div>
  );
}
