"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
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
  Button,
  DensityToggle,
  Empty,
  ErrorState,
  Input,
  Modal,
  PageContainer,
  PageHeader,
  QuickFilters,
  SectionHeader,
  Skeleton,
  WorkspaceToolbar,
  type TableDensity,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useToast } from "@/shared/providers";
import { CreateUserModal } from "./CreateUserModal";
import { DirectoryPeopleList } from "./DirectoryPeopleList";
import { DirectoryPreviewPanel } from "./DirectoryPreviewPanel";
import {
  matchesDirectoryFilter,
  matchesDirectorySearch,
  type DirectoryFilter,
} from "./directoryHelpers";

type ConfirmTarget = {
  user: UserRef;
};

type RevealedPassword = {
  user: UserRef;
  result: AdminResetPasswordResponse;
};

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
  const router = useRouter();
  const t = useTranslations("users");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { userId, hasPermission } = useAuth();
  const { pushSuccess } = useToast();
  const canRead = hasPermission("users:read");
  const canReset = hasPermission("users:reset_password");
  const canCreate = hasPermission("users:create");

  const [rows, setRows] = useState<UserRef[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [confirmTarget, setConfirmTarget] = useState<ConfirmTarget | null>(null);
  const [revealed, setRevealed] = useState<RevealedPassword | null>(null);
  const [resetting, setResetting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [directoryFilter, setDirectoryFilter] = useState<DirectoryFilter>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [density, setDensity] = useState<TableDensity>("comfortable");
  const [showEmail, setShowEmail] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);

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

  const filteredRows = useMemo(() => {
    return rows.filter(
      (row) =>
        matchesDirectoryFilter(row, directoryFilter) &&
        matchesDirectorySearch(row, searchQuery),
    );
  }, [rows, searchQuery, directoryFilter]);

  const selectedUser = useMemo(
    () => filteredRows.find((row) => row.id === selectedId) ?? null,
    [filteredRows, selectedId],
  );

  useEffect(() => {
    if (selectedId && !filteredRows.some((row) => row.id === selectedId)) {
      setSelectedId(null);
    }
  }, [filteredRows, selectedId]);

  const filterOptions = useMemo(
    () => [
      {
        id: "active",
        label: t("filterActive"),
        active: directoryFilter === "active",
        tone: "healthy" as const,
        count: rows.filter((row) => row.isActive).length,
      },
      {
        id: "inactive",
        label: t("filterInactive"),
        active: directoryFilter === "inactive",
        tone: "default" as const,
        count: rows.filter((row) => !row.isActive).length,
      },
      {
        id: "administrator",
        label: t("filterAdministrators"),
        active: directoryFilter === "administrator",
        tone: "critical" as const,
        count: rows.filter((row) =>
          matchesDirectoryFilter(row, "administrator"),
        ).length,
      },
      {
        id: "supervisor",
        label: t("filterSupervisors"),
        active: directoryFilter === "supervisor",
        tone: "attention" as const,
        count: rows.filter((row) =>
          matchesDirectoryFilter(row, "supervisor"),
        ).length,
      },
      {
        id: "agent",
        label: t("filterAgents"),
        active: directoryFilter === "agent",
        tone: "healthy" as const,
        count: rows.filter((row) => matchesDirectoryFilter(row, "agent")).length,
      },
    ],
    [directoryFilter, rows, t],
  );

  function openConfirm(user: UserRef) {
    setActionError(null);
    setCopied(false);
    setConfirmTarget({ user });
  }

  function closeConfirm() {
    if (resetting) return;
    setConfirmTarget(null);
  }

  function closeRevealed() {
    setRevealed(null);
    setCopied(false);
  }

  async function confirmReset() {
    if (!confirmTarget || !canReset) return;
    setResetting(true);
    setActionError(null);
    try {
      const result = await adminResetPassword(confirmTarget.user.id);
      setRevealed({ user: confirmTarget.user, result });
      setConfirmTarget(null);
      pushSuccess(
        t("resetPassword"),
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
          overline={t("overline")}
          title={t("title")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title") },
          ]}
          description={t("description")}
        />
        <Empty
          title={t("accessRestricted")}
          description={t("accessRestrictedDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("description")}
        actions={
          <div className="flex flex-wrap gap-2">
            {canCreate ? (
              <Button
                className="min-h-[var(--ecmp-touch-min)]"
                onClick={() => setCreateOpen(true)}
              >
                {t("createUser")}
              </Button>
            ) : null}
            <Button
              variant="outline"
              className="min-h-[var(--ecmp-touch-min)]"
              onClick={() => void load()}
              disabled={loading}
            >
              {loading ? tCommon("refreshing") : tCommon("refresh")}
            </Button>
          </div>
        }
      />

      <CreateUserModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={(username) => {
          pushSuccess(t("createdSuccess"), t("createdUserSuccess", { username }));
          void load();
        }}
      />

      {actionError ? (
        <Alert tone="danger" title={t("actionFailed")} description={actionError} />
      ) : null}

      <section className="space-y-[var(--ecmp-panel-gap)]" aria-label={t("quickFilters")}>
        <SectionHeader
          title={t("quickFilters")}
          description={t("quickFiltersDescription")}
        />
        <QuickFilters
          label={t("quickFilters")}
          options={filterOptions}
          onSelect={(id) => {
            const next = id as DirectoryFilter;
            setDirectoryFilter((current) => (current === next ? "all" : next));
          }}
        />
      </section>

      <section className="space-y-[var(--ecmp-panel-gap)]" aria-label={t("directorySearch")}>
        <div className="w-full max-w-xl">
          <Input
            name="directorySearch"
            label={t("directorySearch")}
            placeholder={t("searchPlaceholder")}
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            helper={t("searchHelper")}
          />
        </div>

        <WorkspaceToolbar
          summary={t("directorySummary", { count: filteredRows.length })}
          density={<DensityToggle value={density} onChange={setDensity} />}
          actions={
            <>
              <Button
                variant="outline"
                size="sm"
                className="min-h-[var(--ecmp-touch-min)]"
                onClick={() => void load()}
                disabled={loading}
              >
                {loading ? tCommon("refreshing") : tCommon("refresh")}
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="min-h-[var(--ecmp-touch-min)]"
                aria-pressed={showEmail}
                onClick={() => setShowEmail((current) => !current)}
              >
                {showEmail ? t("columnsHideEmail") : t("columnsShowEmail")}
              </Button>
            </>
          }
        />
      </section>

      <section
        className="space-y-[var(--ecmp-panel-gap)]"
        aria-label={t("directorySection")}
      >
        <SectionHeader
          title={t("directorySection")}
          description={t("directorySectionDescription")}
        />

        {loading ? (
          <Skeleton rows={6} />
        ) : loadError ? (
          <ErrorState
            title={t("unableToLoad")}
            message={loadError}
            actionLabel={tCommon("retry")}
            onRetry={() => void load()}
          />
        ) : filteredRows.length === 0 ? (
          <Empty
            title={
              rows.length === 0 ? t("emptyDirectoryTitle") : t("noUsersFound")
            }
            description={
              rows.length === 0
                ? t("emptyDirectoryDescription")
                : t("adjustFiltersAndRetry")
            }
            primaryAction={{
              label: t("refreshUsers"),
              onClick: () => void load(),
            }}
            secondaryAction={
              searchQuery.trim() || directoryFilter !== "all"
                ? {
                    label: t("clearSearch"),
                    onClick: () => {
                      setSearchQuery("");
                      setDirectoryFilter("all");
                    },
                  }
                : undefined
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] xl:grid-cols-12">
            <div className="xl:col-span-8">
              <DirectoryPeopleList
                rows={filteredRows}
                selectedId={selectedId}
                density={density}
                showEmail={showEmail}
                canReset={canReset}
                currentUserId={userId}
                onSelect={(user) =>
                  setSelectedId((current) =>
                    current === user.id ? null : user.id,
                  )
                }
                onResetPassword={openConfirm}
              />
            </div>
            <div className="xl:col-span-4">
              <DirectoryPreviewPanel
                user={selectedUser}
                canReset={canReset}
                currentUserId={userId}
                onResetPassword={openConfirm}
                onClose={() => setSelectedId(null)}
              />
            </div>
          </div>
        )}
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
              {revealed.result.message}
            </p>
          </div>
        ) : null}
      </Modal>
    </PageContainer>
  );
}
