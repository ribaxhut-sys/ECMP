"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  fetchBranches,
  fetchRoles,
  fetchUsers,
  updateUserRole,
  updateUserStatus,
  type Branch,
  type RoleRef,
  type UserRef,
} from "@/lib/api";
import {
  Button,
  Empty,
  ErrorState,
  Input,
  Modal,
  PageContainer,
  PageHeader,
  QuickFilters,
  SectionHeader,
  Select,
  Skeleton,
  WorkspaceToolbar,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { CreateUserModal } from "./CreateUserModal";
import { DirectoryPeopleList } from "./DirectoryPeopleList";
import { DirectoryPreviewPanel } from "./DirectoryPreviewPanel";
import {
  filterRolesForHomeUnit,
  filterRolesForUserForm,
  HEAD_OFFICE_SCOPED_ROLE_CODES,
  matchesDirectoryFilter,
  matchesDirectorySearch,
  roleDisplayName,
  type DirectoryFilter,
} from "./directoryHelpers";
import { HEAD_OFFICE_UNIT_CODE } from "./moduleUserCandidates";
import { useToast } from "@/shared/providers";

export function UserManagement() {
  const router = useRouter();
  const t = useTranslations("users");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { hasPermission, roles, userId } = useAuth();
  const { pushError, pushSuccess } = useToast();
  const canRead = hasPermission("users:read");
  const canCreate = hasPermission("users:create");
  const canUpdate = hasPermission("users:update");
  const isHeadOfficeAdmin = roles.some((role) =>
    ["ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"].includes(role.toUpperCase()),
  );

  const [rows, setRows] = useState<UserRef[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [roleOptions, setRoleOptions] = useState<RoleRef[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [directoryFilter, setDirectoryFilter] = useState<DirectoryFilter>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [statusCandidate, setStatusCandidate] = useState<UserRef | null>(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [roleCandidate, setRoleCandidate] = useState<UserRef | null>(null);
  const [newRoleId, setNewRoleId] = useState("");
  const [updatingRole, setUpdatingRole] = useState(false);

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
      const [userRes, branchRes, roleRows] = await Promise.all([
        fetchUsers({ pageSize: 100 }),
        fetchBranches(100),
        fetchRoles({ activeOnly: true, includeSystem: true }),
      ]);
      setRows(userRes.data);
      setBranches(branchRes.data);
      setRoleOptions(
        filterRolesForUserForm(roleRows.filter((row) => row.isActive)),
      );
    } catch (err) {
      setRows([]);
      setBranches([]);
      setRoleOptions([]);
      setLoadError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, t, tCommon, tErrors]);

  const unitLabelByBranchId = useMemo(
    () =>
      new Map(
        branches.map((branch) => [
          branch.id,
          `${branch.code} — ${branch.name}`,
        ]),
      ),
    [branches],
  );

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

  async function confirmStatusChange() {
    if (!statusCandidate) return;
    const nextActive = !statusCandidate.isActive;
    setUpdatingStatus(true);
    try {
      const updated = await updateUserStatus(statusCandidate.id, nextActive);
      setRows((current) =>
        current.map((row) => (row.id === updated.id ? updated : row)),
      );
      setStatusCandidate(null);
      pushSuccess(
        t("statusUpdated"),
        t(nextActive ? "activatedUser" : "deactivatedUser", {
          username: updated.fullName || updated.username,
        }),
      );
    } catch (error) {
      pushError(error, t("unableToUpdateStatus"));
    } finally {
      setUpdatingStatus(false);
    }
  }

  const pusatBranchId = useMemo(
    () =>
      branches.find(
        (branch) => branch.code.toUpperCase() === HEAD_OFFICE_UNIT_CODE,
      )?.id ?? null,
    [branches],
  );

  // Cabang: no Admin. Pusat (null unit or PUSAT branch): same personas + Admin.
  const selectableRoles = useMemo(() => {
    if (!roleCandidate) return [];
    const atHeadOffice =
      !roleCandidate.branchId || roleCandidate.branchId === pusatBranchId;
    return filterRolesForHomeUnit(roleOptions, atHeadOffice).filter(
      (role) => role.id !== roleCandidate.roleId,
    );
  }, [roleOptions, roleCandidate, pusatBranchId]);

  function openRoleModal(user: UserRef) {
    setNewRoleId("");
    setRoleCandidate(user);
  }

  async function confirmRoleChange() {
    if (!roleCandidate || !newRoleId) return;
    const targetRole = roleOptions.find((role) => role.id === newRoleId);
    if (!targetRole) return;
    // Admin clears unit; operational roles keep the directory unit (or PUSAT
    // when promoting a null-unit Pusat member into a branch-scoped role).
    const nextBranchId = HEAD_OFFICE_SCOPED_ROLE_CODES.has(targetRole.code)
      ? null
      : roleCandidate.branchId ?? pusatBranchId;
    setUpdatingRole(true);
    try {
      const updated = await updateUserRole(
        roleCandidate.id,
        newRoleId,
        nextBranchId,
      );
      setRows((current) =>
        current.map((row) => (row.id === updated.id ? updated : row)),
      );
      setRoleCandidate(null);
      setNewRoleId("");
      pushSuccess(
        t("roleUpdated"),
        t("roleUpdatedFor", {
          username: updated.fullName || updated.username,
        }),
      );
    } catch (error) {
      pushError(error, t("unableToUpdateRole"));
    } finally {
      setUpdatingRole(false);
    }
  }

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

      <Modal
        open={Boolean(statusCandidate)}
        onClose={() => {
          if (!updatingStatus) setStatusCandidate(null);
        }}
        title={
          statusCandidate?.isActive
            ? t("deactivateUserTitle")
            : t("activateUserTitle")
        }
        size="sm"
        footer={
          <>
            <Button
              variant="outline"
              disabled={updatingStatus}
              onClick={() => setStatusCandidate(null)}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              variant={statusCandidate?.isActive ? "danger" : "success"}
              loading={updatingStatus}
              onClick={() => void confirmStatusChange()}
            >
              {statusCandidate?.isActive ? t("deactivate") : t("activate")}
            </Button>
          </>
        }
      >
        <p className="text-sm text-ecmp-text-secondary">
          {statusCandidate
            ? t(
                statusCandidate.isActive
                  ? "deactivateUserConfirm"
                  : "activateUserConfirm",
                {
                  username:
                    statusCandidate.fullName || statusCandidate.username,
                },
              )
            : null}
        </p>
      </Modal>

      <Modal
        open={Boolean(roleCandidate)}
        onClose={() => {
          if (!updatingRole) {
            setRoleCandidate(null);
            setNewRoleId("");
          }
        }}
        title={t("changeRoleTitle")}
        size="sm"
        footer={
          <>
            <Button
              variant="outline"
              disabled={updatingRole}
              onClick={() => {
                setRoleCandidate(null);
                setNewRoleId("");
              }}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              loading={updatingRole}
              disabled={!newRoleId}
              onClick={() => void confirmRoleChange()}
            >
              {t("changeRole")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-form-gap)]">
          <p className="text-sm text-ecmp-text-secondary">
            {roleCandidate
              ? t("changeRoleConfirm", {
                  username:
                    roleCandidate.fullName || roleCandidate.username,
                })
              : null}
          </p>
          <Select
            name="newRoleId"
            label={t("newRole")}
            value={newRoleId}
            disabled={updatingRole}
            onChange={(event) => setNewRoleId(event.target.value)}
            options={[
              { value: "", label: t("selectRole") },
              ...selectableRoles.map((role) => ({
                value: role.id,
                label: `${roleDisplayName(role, t("roleBranchManager"))} (${role.code})`,
              })),
            ]}
          />
        </div>
      </Modal>

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
          actions={
            <Button
              variant="outline"
              size="sm"
              className="min-h-[var(--ecmp-touch-min)]"
              onClick={() => void load()}
              disabled={loading}
            >
              {loading ? tCommon("refreshing") : tCommon("refresh")}
            </Button>
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
                unitLabelByBranchId={unitLabelByBranchId}
                onSelect={(user) =>
                  setSelectedId((current) =>
                    current === user.id ? null : user.id,
                  )
                }
              />
            </div>
            <div className="xl:col-span-4">
              <DirectoryPreviewPanel
                user={selectedUser}
                unitLabel={
                  selectedUser
                    ? selectedUser.branchId
                      ? unitLabelByBranchId.get(selectedUser.branchId) ??
                        t("unitUnknown")
                      : t("locationHeadOffice")
                    : null
                }
                canUpdateStatus={Boolean(
                  selectedUser &&
                    canUpdate &&
                    isHeadOfficeAdmin &&
                    selectedUser.id !== userId,
                )}
                updatingStatus={updatingStatus}
                onRequestStatusChange={setStatusCandidate}
                canUpdateRole={Boolean(
                  selectedUser &&
                    canUpdate &&
                    isHeadOfficeAdmin &&
                    selectedUser.id !== userId,
                )}
                onRequestRoleChange={openRoleModal}
                onClose={() => setSelectedId(null)}
              />
            </div>
          </div>
        )}
      </section>
    </PageContainer>
  );
}
