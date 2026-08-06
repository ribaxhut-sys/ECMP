"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  PageHeader,
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey, isBatchAtLeast } from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "@/features/supervisor-assign/mock/useAssignmentRepository";
import {
  getCustomerByRef,
  isIntakeFormComplete,
  type MockCategory,
  type MockChannel,
  type MockCustomer,
  type MockPriority,
} from "@/features/supervisor-assign/mock/assignmentRepository";
import { CompletenessChecklist } from "./CompletenessChecklist";
import { CustomerReferencePanel } from "./CustomerReferencePanel";
import { IntakeFormFields } from "./IntakeFormFields";
import { RegisterConfirmDialog } from "./RegisterConfirmDialog";

type FormState = {
  subject: string;
  description: string;
  category: MockCategory | "";
  channel: MockChannel | "";
  priority: MockPriority | "";
};

const EMPTY_FORM: FormState = {
  subject: "",
  description: "",
  category: "",
  channel: "",
  priority: "",
};

/**
 * SCR-WS-01 — Workspace — New Intake (Batch B3).
 * Forward / Register when complete · Hold to complete · stay on workspace.
 * R2-B2: closed-only customer → SCR-WS-03 reopen routing.
 */
export function IntakeWorkspace() {
  const t = useTranslations("intake");
  const tShell = useTranslations("shell");
  const router = useRouter();
  const {
    registerIntake,
    holdIntakeDraft,
    listActiveCasesByCustomerRef,
    listClosedCasesByCustomerRef,
    listHeldDrafts,
    consumeHeldDraft,
  } = useAssignmentRepository();
  const reopenEnabled = isBatchAtLeast("R2B2");

  const [customer, setCustomer] = useState<MockCustomer | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [heldMode, setHeldMode] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [savingHold, setSavingHold] = useState(false);
  const [banner, setBanner] = useState<{
    tone: "info" | "danger" | "warning";
    title: string;
  } | null>(null);
  const [fieldErrors, setFieldErrors] = useState<
    Partial<Record<keyof FormState, string>>
  >({});

  // Recomputed each render; repo subscribe triggers refresh after mutations.
  const activeCases = customer
    ? listActiveCasesByCustomerRef(customer.ref)
    : [];
  const closedCases =
    customer && reopenEnabled
      ? listClosedCasesByCustomerRef(customer.ref).filter((c) => !c.reopenPending)
      : [];

  const hasActiveCase = activeCases.length > 0;
  const hasClosedOnly =
    reopenEnabled && !hasActiveCase && closedCases.length > 0;
  const complete = Boolean(
    customer &&
      isIntakeFormComplete({
        customerRef: customer.ref,
        customerName: customer.name,
        ...form,
      }),
  );

  /** Hold disables Forward while the Hold decision is active. */
  const forwardEnabled = complete && !heldMode && !hasActiveCase;

  function resetForNextContact(): void {
    setCustomer(null);
    setForm(EMPTY_FORM);
    setHeldMode(false);
    setFieldErrors({});
    setDialogOpen(false);
  }

  function onHold(): void {
    setBanner(null);
    if (!customer) {
      setBanner({ tone: "danger", title: t("holdError.CUSTOMER_REQUIRED") });
      return;
    }
    setSavingHold(true);
    const result = holdIntakeDraft({
      customerRef: customer.ref,
      customerName: customer.name,
      subject: form.subject,
      description: form.description,
      category: form.category,
      channel: form.channel,
      priority: form.priority,
    });
    setSavingHold(false);
    if (!result.ok) {
      setBanner({ tone: "danger", title: t(`holdError.${result.reason}`) });
      return;
    }
    setHeldMode(true);
    setBanner({ tone: "info", title: t("holdSuccess") });
    resetForNextContact();
  }

  function onRequestRegister(): void {
    setBanner(null);
    if (!customer) {
      setBanner({ tone: "danger", title: t("registerError.CUSTOMER_REQUIRED") });
      return;
    }
    if (hasActiveCase) {
      setBanner({ tone: "warning", title: t("registerError.ACTIVE_CASE_EXISTS") });
      return;
    }
    if (!complete) {
      const next: Partial<Record<keyof FormState, string>> = {};
      if (!form.subject.trim()) next.subject = t("fieldRequired");
      if (!form.description.trim()) next.description = t("fieldRequired");
      if (!form.category) next.category = t("fieldRequired");
      if (!form.channel) next.channel = t("fieldRequired");
      if (!form.priority) next.priority = t("fieldRequired");
      setFieldErrors(next);
      setBanner({ tone: "danger", title: t("registerError.INCOMPLETE") });
      return;
    }
    setDialogOpen(true);
  }

  function onConfirmRegister(): void {
    if (!customer || !form.category || !form.channel || !form.priority) return;
    setConfirming(true);
    const result = registerIntake({
      customerRef: customer.ref,
      customerName: customer.name,
      subject: form.subject,
      description: form.description,
      category: form.category,
      channel: form.channel,
      priority: form.priority,
    });
    setConfirming(false);
    setDialogOpen(false);
    if (!result.ok) {
      setBanner({ tone: "danger", title: t(`registerError.${result.reason}`) });
      return;
    }
    setBanner({
      tone: "info",
      title: t("registerSuccess", { reference: result.complaint.reference }),
    });
    resetForNextContact();
  }

  function resumeHeld(draftId: string): void {
    const draft = consumeHeldDraft(draftId);
    if (!draft) return;
    const cached = getCustomerByRef(draft.customerRef);
    setCustomer(
      cached ?? {
        ref: draft.customerRef,
        name: draft.customerName,
        phone: "—",
        email: "—",
      },
    );
    setForm({
      subject: draft.subject,
      description: draft.description,
      category: draft.category,
      channel: draft.channel,
      priority: draft.priority,
    });
    setHeldMode(false);
    setBanner({ tone: "info", title: t("heldResumed") });
  }

  const heldDrafts = listHeldDrafts();

  return (
    <WorkspaceLayout
      toolbar={
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("newIntakeTitle")}
          description={t("newIntakeDescription")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/workspace" },
            { label: t("newIntakeTitle") },
          ]}
          actions={
            <Badge tone="info" variant="outline">
              {t("modeIntake")}
            </Badge>
          }
        />
      }
    >
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        {banner ? <Alert tone={banner.tone} title={banner.title} /> : null}

        {heldDrafts.length > 0 ? (
          <Card>
            <CardHeader>
              <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
                {t("heldDraftsTitle")}
              </h2>
            </CardHeader>
            <CardBody>
              <ul className="space-y-2">
                {heldDrafts.map((draft) => (
                  <li
                    key={draft.id}
                    className="flex flex-col gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <p className="font-medium text-ecmp-text-primary">
                        {draft.customerName} · {draft.subject || t("heldNoSubject")}
                      </p>
                      <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                        {new Date(draft.heldAt).toLocaleString()}
                      </p>
                    </div>
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => resumeHeld(draft.id)}
                    >
                      {t("resumeHeld")}
                    </Button>
                  </li>
                ))}
              </ul>
            </CardBody>
          </Card>
        ) : null}

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
          <div className="space-y-6">
            <CustomerReferencePanel
              selected={customer}
              onSelect={(next) => {
                setCustomer(next);
                setHeldMode(false);
                setBanner(null);
              }}
              onClear={() => {
                setCustomer(null);
                setHeldMode(false);
              }}
            />

            {hasActiveCase ? (
              <Alert
                tone="warning"
                title={t("activeCaseTitle")}
                description={t("activeCaseDescription")}
              />
            ) : null}

            {hasClosedOnly ? (
              <Alert
                tone="info"
                title={t("closedCaseTitle")}
                description={t("closedCaseDescription")}
              />
            ) : null}

            {hasActiveCase ? (
              <Card>
                <CardHeader>
                  <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
                    {t("activeCasesTitle")}
                  </h2>
                </CardHeader>
                <CardBody>
                  <ul className="space-y-2">
                    {activeCases.map((item) => (
                      <li
                        key={item.id}
                        className="flex flex-col gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
                      >
                        <div>
                          <p className="font-medium text-ecmp-text-primary">
                            {item.reference}
                          </p>
                          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                            {item.subject} · {item.status}
                          </p>
                        </div>
                        <Button
                          type="button"
                          variant="primary"
                          onClick={() =>
                            router.push(`/workspace/follow-up/${item.id}`)
                          }
                        >
                          {t("openFollowUp")}
                        </Button>
                      </li>
                    ))}
                  </ul>
                </CardBody>
              </Card>
            ) : hasClosedOnly ? (
              <Card>
                <CardHeader>
                  <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
                    {t("closedCasesTitle")}
                  </h2>
                </CardHeader>
                <CardBody>
                  <ul className="space-y-2">
                    {closedCases.map((item) => (
                      <li
                        key={item.id}
                        className="flex flex-col gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
                      >
                        <div>
                          <p className="font-medium text-ecmp-text-primary">
                            {item.reference}
                          </p>
                          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                            {item.subject} · CLOSED
                          </p>
                        </div>
                        <Button
                          type="button"
                          variant="primary"
                          onClick={() =>
                            router.push(`/workspace/reopen/${item.id}`)
                          }
                        >
                          {t("openReopenRouting")}
                        </Button>
                      </li>
                    ))}
                  </ul>
                </CardBody>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
                    {t("formTitle")}
                  </h2>
                  {!customer ? (
                    <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                      {t("formEmptyHint")}
                    </p>
                  ) : null}
                </CardHeader>
                <CardBody>
                  <IntakeFormFields
                    {...form}
                    disabled={!customer}
                    errors={fieldErrors}
                    onChange={(patch) => {
                      setForm((prev) => ({ ...prev, ...patch }));
                      setFieldErrors({});
                      setHeldMode(false);
                    }}
                  />
                </CardBody>
              </Card>
            )}
          </div>

          <aside className="space-y-4 lg:sticky lg:top-4 lg:self-start">
            <CompletenessChecklist
              customerRef={customer?.ref ?? ""}
              subject={form.subject}
              description={form.description}
              category={form.category}
              channel={form.channel}
              priority={form.priority}
            />
          </aside>
        </div>

        {!hasActiveCase ? (
          <div className="flex flex-col gap-3 border-t border-ecmp-border/70 pt-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {heldMode ? t("holdDisablesForward") : t("actionHint")}
            </p>
            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <Button
                type="button"
                variant="secondary"
                loading={savingHold}
                disabled={!customer}
                onClick={onHold}
              >
                {t("holdToComplete")}
              </Button>
              <Button
                type="button"
                variant="primary"
                disabled={!forwardEnabled}
                title={
                  heldMode
                    ? t("holdDisablesForward")
                    : !complete
                      ? t("registerError.INCOMPLETE")
                      : undefined
                }
                onClick={onRequestRegister}
              >
                {t("forwardRegister")}
              </Button>
            </div>
          </div>
        ) : null}
      </div>

      <RegisterConfirmDialog
        open={dialogOpen}
        customerName={customer?.name ?? ""}
        subject={form.subject}
        confirming={confirming}
        onConfirm={onConfirmRegister}
        onClose={() => {
          if (!confirming) setDialogOpen(false);
        }}
      />
    </WorkspaceLayout>
  );
}
