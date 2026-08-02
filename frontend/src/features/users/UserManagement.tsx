"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  adminResetPassword,
  fetchUsers,
  type UserRef,
} from "@/lib/api";
import type { AdminResetPasswordResponse } from "@/lib/api/types";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  Modal,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

type ConfirmTarget = {
  user: UserRef;
};

type RevealedPassword = {
  user: UserRef;
  result: AdminResetPasswordResponse;
};

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function printTemporaryPassword(payload: {
  username: string;
  fullName: string;
  temporaryPassword: string;
  message: string;
  labels: {
    documentTitle: string;
    heading: string;
    showOnce: string;
    showOnceDescription: string;
    user: string;
    temporaryPassword: string;
    printed: string;
  };
}): void {
  const win = window.open("", "_blank", "noopener,noreferrer,width=640,height=480");
  if (!win) return;
  const escaped = (value: string) =>
    value
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  win.document.write(`<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>${escaped(payload.labels.documentTitle)}</title>
  <style>
    body { font-family: system-ui, sans-serif; padding: 2rem; color: #0f172a; }
    h1 { font-size: 1.25rem; margin: 0 0 0.5rem; }
    .warn { color: #b45309; margin: 1rem 0; }
    .pw { font-family: ui-monospace, monospace; font-size: 1.25rem;
          letter-spacing: 0.04em; border: 1px solid #cbd5e1; padding: 0.75rem 1rem;
          display: inline-block; margin-top: 0.5rem; }
    .meta { color: #475569; font-size: 0.9rem; margin-top: 1.25rem; }
  </style>
</head>
<body>
  <h1>${escaped(payload.labels.heading)}</h1>
  <p class="warn"><strong>${escaped(payload.labels.showOnce)}</strong> ${escaped(payload.labels.showOnceDescription)}</p>
  <p><strong>${escaped(payload.labels.user)}:</strong> ${escaped(payload.fullName)} (${escaped(payload.username)})</p>
  <p><strong>${escaped(payload.labels.temporaryPassword)}</strong><br /><span class="pw">${escaped(payload.temporaryPassword)}</span></p>
  <p class="meta">${escaped(payload.message)}</p>
  <p class="meta">${escaped(payload.labels.printed)} ${escaped(new Date().toISOString())}</p>
  <script>window.onload = function () { window.print(); };</script>
</body>
</html>`);
  win.document.close();
}

export function UserManagement() {
  const t = useTranslations("users");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { userId, hasPermission } = useAuth();
  const canRead = hasPermission("users:read");
  const canReset = hasPermission("users:reset_password");

  const [rows, setRows] = useState<UserRef[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [confirmTarget, setConfirmTarget] = useState<ConfirmTarget | null>(null);
  const [revealed, setRevealed] = useState<RevealedPassword | null>(null);
  const [resetting, setResetting] = useState(false);
  const [copied, setCopied] = useState(false);

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      setRows([]);
      setLoadError(null);
      return;
    }
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchUsers({ pageSize: 100 });
      setRows(res.data);
    } catch (err) {
      setRows([]);
      setLoadError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  function openConfirm(user: UserRef) {
    setActionError(null);
    setActionSuccess(null);
    setCopied(false);
    setConfirmTarget({ user });
  }

  function closeConfirm() {
    if (resetting) return;
    setConfirmTarget(null);
  }

  /** Closing discards the temporary password permanently from UI state. */
  function closeRevealed() {
    setRevealed(null);
    setCopied(false);
  }

  async function confirmReset() {
    if (!confirmTarget || !canReset) return;
    setResetting(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      const result = await adminResetPassword(confirmTarget.user.id);
      setRevealed({ user: confirmTarget.user, result });
      setConfirmTarget(null);
      setActionSuccess(
        t("passwordResetSuccess", { username: confirmTarget.user.username }),
      );
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToResetPassword"),
      );
      setConfirmTarget(null);
    } finally {
      setResetting(false);
    }
  }

  async function copyTemporaryPassword() {
    const value = revealed?.result.temporaryPassword;
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
    } catch {
      setActionError(t("unableToCopyPassword"));
    }
  }

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("title")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={t("accessRestricted")}
          description={t("accessRestrictedDescription")}
        />
      </PageContainer>
    );
  }

  const columns: TableColumn<UserRef>[] = [
    {
      key: "username",
      header: t("username"),
      cell: (row) => (
        <div className="space-y-0.5">
          <div className="font-medium text-ecmp-text-primary">{row.username}</div>
          <div className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
            {row.fullName}
          </div>
        </div>
      ),
    },
    {
      key: "email",
      header: t("email"),
      cell: (row) => row.email,
    },
    {
      key: "role",
      header: t("role"),
      cell: (row) => (
        <Badge tone="neutral">{row.roleCode ?? row.roleName ?? "—"}</Badge>
      ),
    },
    {
      key: "status",
      header: tCommon("status"),
      cell: (row) => (
        <Badge tone={row.isActive ? "success" : "neutral"}>
          {row.isActive ? tCommon("active") : tCommon("inactive")}
        </Badge>
      ),
    },
    {
      key: "lastLogin",
      header: t("lastLogin"),
      hideOnMobile: true,
      cell: (row) => formatWhen(row.lastLoginAt),
    },
    {
      key: "actions",
      header: tCommon("actions"),
      cell: (row) => {
        if (!canReset) {
          return (
            <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              —
            </span>
          );
        }
        const isSelf = row.id === userId;
        return (
          <Button
            variant="outline"
            size="sm"
            disabled={!row.isActive || isSelf}
            title={
              isSelf
                ? t("resetOwnPasswordHint")
                : row.isActive
                  ? t("resetPasswordHint")
                  : t("inactiveResetHint")
            }
            onClick={() => openConfirm(row)}
          >
            {t("resetPassword")}
          </Button>
        );
      },
    },
  ];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("managementDescription")}
        actions={
          <Button variant="outline" size="sm" onClick={() => void load()}>
            {tCommon("refresh")}
          </Button>
        }
      />

      {actionError ? (
        <Alert tone="danger" title={t("actionFailed")} description={actionError} />
      ) : null}
      {actionSuccess ? (
        <Alert tone="success" title={t("resetPassword")} description={actionSuccess} />
      ) : null}

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader title={t("title")} description={t("managementDescription")} />
        <Card>
          <CardBody>
            {loading ? (
              <div className="space-y-[var(--ecmp-form-gap)]">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : loadError ? (
              <ErrorState
                title={t("unableToLoad")}
                message={loadError}
                actionLabel={tCommon("retry")}
                onRetry={() => void load()}
              />
            ) : (
              <Table
                columns={columns}
                rows={rows}
                getRowKey={(row) => row.id}
                caption={t("title")}
                emptyMessage={t("noUsersFound")}
              />
            )}
          </CardBody>
        </Card>
      </section>

      <Modal
        open={confirmTarget != null}
        onClose={closeConfirm}
        title={t("confirmResetTitle")}
        footer={
          <>
            <Button variant="outline" onClick={closeConfirm} disabled={resetting}>
              {tCommon("cancel")}
            </Button>
            <Button variant="danger" loading={resetting} onClick={() => void confirmReset()}>
              {resetting ? t("resetting") : t("resetPassword")}
            </Button>
          </>
        }
      >
        {confirmTarget ? (
          <div className="space-y-[var(--ecmp-panel-gap)]">
            <Alert
              tone="warning"
              title={t("resetWarningTitle")}
              description={t("resetWarningDescription")}
            />
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
              {t("resetPasswordFor")}{" "}
              <strong>{confirmTarget.user.fullName}</strong> (
              {confirmTarget.user.username} / {confirmTarget.user.email})?
            </p>
          </div>
        ) : null}
      </Modal>

      <Modal
        open={revealed != null}
        onClose={closeRevealed}
        title={t("temporaryPasswordTitle")}
        footer={
          <>
            <Button
              variant="outline"
              onClick={() => {
                if (!revealed) return;
                printTemporaryPassword({
                  username: revealed.user.username,
                  fullName: revealed.user.fullName,
                  temporaryPassword: revealed.result.temporaryPassword,
                  message: revealed.result.message,
                  labels: {
                    documentTitle: t("temporaryPasswordTitle"),
                    heading: t("temporaryPasswordTitle"),
                    showOnce: t("printShowOnce"),
                    showOnceDescription: t("printShowOnceDescription"),
                    user: tCommon("user"),
                    temporaryPassword: t("temporaryPassword"),
                    printed: t("printedAt"),
                  },
                });
              }}
            >
              {t("print")}
            </Button>
            <Button variant="secondary" onClick={() => void copyTemporaryPassword()}>
              {copied ? t("copied") : t("copy")}
            </Button>
            <Button variant="primary" onClick={closeRevealed}>
              {t("doneSaved")}
            </Button>
          </>
        }
      >
        {revealed ? (
          <div className="space-y-[var(--ecmp-panel-gap)]">
            <Alert
              tone="warning"
              title={t("temporaryPasswordWarningTitle")}
              description={t("temporaryPasswordWarningDescription")}
            />
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {tCommon("user")}:{" "}
              <strong className="text-ecmp-text-primary">{revealed.user.username}</strong>
            </p>
            <div className="space-y-2">
              <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                {t("temporaryPassword")}
              </p>
              <code
                className="block break-all rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken px-3 py-3 font-mono text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary"
                data-testid="temporary-password"
              >
                {revealed.result.temporaryPassword}
              </code>
            </div>
            <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              {revealed.result.message} Audit:{" "}
              <code>password.admin_reset</code>
            </p>
          </div>
        ) : null}
      </Modal>
    </PageContainer>
  );
}
