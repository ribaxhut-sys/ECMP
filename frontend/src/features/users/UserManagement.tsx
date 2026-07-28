"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
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
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";

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
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>ECMP temporary password</title>
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
  <h1>ECMP — Temporary password</h1>
  <p class="warn"><strong>Show once.</strong> Store securely and share out-of-band.
  The user must change this password on next login.</p>
  <p><strong>User:</strong> ${escaped(payload.fullName)} (${escaped(payload.username)})</p>
  <p><strong>Temporary password</strong><br /><span class="pw">${escaped(payload.temporaryPassword)}</span></p>
  <p class="meta">${escaped(payload.message)}</p>
  <p class="meta">Printed ${escaped(new Date().toISOString())}</p>
  <script>window.onload = function () { window.print(); };</script>
</body>
</html>`);
  win.document.close();
}

export function UserManagement() {
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
        err instanceof ApiError
          ? err.message
          : "Unable to load users.",
      );
    } finally {
      setLoading(false);
    }
  }, [canRead]);

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
        `Password reset for ${confirmTarget.user.username}. Audit event password.admin_reset recorded. Share the temporary password now — it will not be shown again.`,
      );
    } catch (err) {
      setActionError(
        err instanceof ApiError
          ? err.message
          : "Unable to reset password.",
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
      setActionError("Unable to copy to clipboard. Select and copy manually.");
    }
  }

  if (!canRead) {
    return (
      <Empty
        title="Access restricted"
        description="You need the users:read permission to view user administration."
      />
    );
  }

  const columns: TableColumn<UserRef>[] = [
    {
      key: "username",
      header: "Username",
      cell: (row) => (
        <div>
          <div className="font-medium text-ecmp-text-primary">{row.username}</div>
          <div className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {row.fullName}
          </div>
        </div>
      ),
    },
    {
      key: "email",
      header: "Email",
      cell: (row) => row.email,
    },
    {
      key: "role",
      header: "Role",
      cell: (row) => row.roleCode ?? row.roleName ?? "—",
    },
    {
      key: "status",
      header: "Status",
      cell: (row) => (
        <Badge tone={row.isActive ? "success" : "neutral"}>
          {row.isActive ? "Active" : "Inactive"}
        </Badge>
      ),
    },
    {
      key: "lastLogin",
      header: "Last login",
      hideOnMobile: true,
      cell: (row) => formatWhen(row.lastLoginAt),
    },
    {
      key: "actions",
      header: "Actions",
      cell: (row) => {
        if (!canReset) {
          return (
            <span className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
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
                ? "Use Change Password for your own account"
                : row.isActive
                  ? "Reset password and force change on next login"
                  : "Inactive users cannot be reset"
            }
            onClick={() => openConfirm(row)}
          >
            Reset password
          </Button>
        );
      },
    },
  ];

  return (
    <>
      <Card>
        <CardBody className="space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-[length:var(--ecmp-font-title-size)] font-semibold text-ecmp-text-primary">
                User administration
              </h2>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                Reset a user password (API-413). The temporary password is shown once.
              </p>
            </div>
            <Button variant="outline" size="sm" onClick={() => void load()}>
              Refresh
            </Button>
          </div>

          {actionError ? (
            <Alert tone="danger" title="Action failed" description={actionError} />
          ) : null}
          {actionSuccess ? (
            <Alert tone="success" title="Password reset" description={actionSuccess} />
          ) : null}

          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : loadError ? (
            <ErrorState
              title="Unable to load users"
              message={loadError}
              actionLabel="Retry"
              onRetry={() => void load()}
            />
          ) : (
            <Table
              columns={columns}
              rows={rows}
              getRowKey={(row) => row.id}
              caption="ECMP users"
              emptyMessage="No users found."
            />
          )}
        </CardBody>
      </Card>

      <Modal
        open={confirmTarget != null}
        onClose={closeConfirm}
        title="Confirm password reset"
        footer={
          <>
            <Button variant="outline" onClick={closeConfirm} disabled={resetting}>
              Cancel
            </Button>
            <Button variant="danger" loading={resetting} onClick={() => void confirmReset()}>
              {resetting ? "Resetting…" : "Reset password"}
            </Button>
          </>
        }
      >
        {confirmTarget ? (
          <div className="space-y-3">
            <Alert
              tone="warning"
              title="This cannot be undone from the UI"
              description="A temporary password will be generated, all refresh sessions revoked, and the user must change their password on next login. The temporary password is shown only once."
            />
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
              Reset password for{" "}
              <strong>{confirmTarget.user.fullName}</strong> (
              {confirmTarget.user.username} / {confirmTarget.user.email})?
            </p>
          </div>
        ) : null}
      </Modal>

      <Modal
        open={revealed != null}
        onClose={closeRevealed}
        title="Temporary password (show once)"
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
                });
              }}
            >
              Print
            </Button>
            <Button variant="secondary" onClick={() => void copyTemporaryPassword()}>
              {copied ? "Copied" : "Copy"}
            </Button>
            <Button variant="primary" onClick={closeRevealed}>
              Done — I saved it
            </Button>
          </>
        }
      >
        {revealed ? (
          <div className="space-y-4">
            <Alert
              tone="warning"
              title="Visible only in this dialog"
              description="Closing this dialog permanently hides the temporary password. It is not stored in the UI and cannot be retrieved again."
            />
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              User: <strong className="text-ecmp-text-primary">{revealed.user.username}</strong>
            </p>
            <div>
              <p className="mb-2 text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                Temporary password
              </p>
              <code
                className="block break-all rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-background px-3 py-3 font-mono text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary"
                data-testid="temporary-password"
              >
                {revealed.result.temporaryPassword}
              </code>
            </div>
            <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {revealed.result.message} Audit:{" "}
              <code>password.admin_reset</code>
            </p>
          </div>
        ) : null}
      </Modal>
    </>
  );
}
