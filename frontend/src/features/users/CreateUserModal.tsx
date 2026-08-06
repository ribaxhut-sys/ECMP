"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {
  createUser,
  fetchBranches,
  fetchRoles,
  fetchUsers,
  type RoleRef,
} from "@/lib/api";
import type { Branch } from "@/lib/api/branches";
import {
  Alert,
  Button,
  Input,
  Modal,
  Select,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  BRANCH_SCOPED_ROLE_CODES,
  filterRolesForHomeUnit,
  filterRolesForUserForm,
  HEAD_OFFICE_SCOPED_ROLE_CODES,
  roleDisplayName,
} from "./directoryHelpers";
import {
  highlightMatchSegments,
  isHeadOfficeCandidate,
  searchModuleUserCandidates,
  type ModuleUserCandidate,
} from "./moduleUserCandidates";

export {
  BRANCH_SCOPED_ROLE_CODES,
  HEAD_OFFICE_SCOPED_ROLE_CODES,
} from "./directoryHelpers";

function HighlightedText({
  text,
  query,
  className,
}: {
  text: string;
  query: string;
  className?: string;
}) {
  return (
    <span className={className}>
      {highlightMatchSegments(text, query).map((segment, index) =>
        segment.matched ? (
          <strong
            key={`${index}-${segment.text}`}
            className="text-[length:calc(1em+2px)] font-semibold text-ecmp-info"
          >
            {segment.text}
          </strong>
        ) : (
          <span key={`${index}-${segment.text}`}>{segment.text}</span>
        ),
      )}
    </span>
  );
}

type CreateUserModalProps = {
  open: boolean;
  onClose: () => void;
  onCreated: (username: string) => void;
};

type FormState = {
  username: string;
  email: string;
  fullName: string;
  roleId: string;
  isActive: boolean;
};

const emptyForm = (): FormState => ({
  username: "",
  email: "",
  fullName: "",
  roleId: "",
  isActive: true,
});

/**
 * Mode A API-213 still requires a password body field. Temporary Password is
 * not an ECMP product surface (SSO is the target), so the UI never shows it.
 * Lab hedge: one shared temporary password so operators can login with ID+pass
 * while testing — replace/retire when Enterprise SSO is unlocked.
 */
export const MODE_A_LAB_TEMP_PASSWORD = "LabTemp!2026";

function opaqueModeAPassword(): string {
  return MODE_A_LAB_TEMP_PASSWORD;
}

export function CreateUserModal({
  open,
  onClose,
  onCreated,
}: CreateUserModalProps) {
  const t = useTranslations("users");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");

  const [form, setForm] = useState<FormState>(emptyForm);
  const [roles, setRoles] = useState<RoleRef[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [registeredUsernames, setRegisteredUsernames] = useState<Set<string>>(
    () => new Set(),
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCandidate, setSelectedCandidate] =
    useState<ModuleUserCandidate | null>(null);
  const [loadingLookups, setLoadingLookups] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setForm(emptyForm());
    setSearchQuery("");
    setSelectedCandidate(null);
    setError(null);
    setFieldError(null);
    setLoadingLookups(true);
    void (async () => {
      try {
        const [roleRows, branchRes, registered] = await Promise.all([
          fetchRoles({ activeOnly: true, includeSystem: true }),
          fetchBranches(100),
          // API-214 pageSize max is 100 (Query le=100); page through if needed.
          (async () => {
            const names = new Set<string>();
            let page = 1;
            for (;;) {
              const res = await fetchUsers({ page, pageSize: 100 });
              for (const row of res.data) names.add(row.username);
              const total = res.meta?.totalItems ?? res.data.length;
              if (names.size >= total || res.data.length === 0) break;
              page += 1;
              if (page > 50) break;
            }
            return names;
          })(),
        ]);
        setRoles(filterRolesForUserForm(roleRows.filter((row) => row.isActive)));
        setBranches(branchRes.data);
        setRegisteredUsernames(registered);
      } catch (err) {
        setError(
          resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"),
        );
      } finally {
        setLoadingLookups(false);
      }
    })();
  }, [open, t, tCommon, tErrors]);

  const searchHits = useMemo(() => {
    if (selectedCandidate) return [];
    return searchModuleUserCandidates(searchQuery, {
      excludeUsernames: registeredUsernames,
      limit: 8,
    });
  }, [searchQuery, registeredUsernames, selectedCandidate]);

  // A person's home unit decides Admin eligibility: cabang candidates cannot
  // hold ADMIN; Pusat candidates get the same operational personas as cabang
  // plus Admin (Pusat also receives complaints).
  const candidateAtHeadOffice = selectedCandidate
    ? isHeadOfficeCandidate(selectedCandidate)
    : false;

  const availableRoles = useMemo(() => {
    if (!selectedCandidate) return roles;
    return filterRolesForHomeUnit(roles, candidateAtHeadOffice);
  }, [roles, selectedCandidate, candidateAtHeadOffice]);

  const selectedRole = useMemo(
    () => roles.find((row) => row.id === form.roleId) ?? null,
    [roles, form.roleId],
  );

  const branchRequired = Boolean(
    selectedRole && BRANCH_SCOPED_ROLE_CODES.has(selectedRole.code),
  );
  const isHeadOfficeScoped = Boolean(
    selectedRole && HEAD_OFFICE_SCOPED_ROLE_CODES.has(selectedRole.code),
  );

  // Unit comes from the candidate's directory home unit (matched by branch
  // code). Head-office-scoped roles (ADMIN, …) still carry no unit — backend
  // HEAD_OFFICE_SCOPED_ROLE_CODES. Operational roles at Pusat use the PUSAT
  // branch row so complaint intake stays branch-scoped.
  const candidateBranch = useMemo(
    () =>
      branches.find((row) => row.code === selectedCandidate?.homeBranchCode) ??
      null,
    [branches, selectedCandidate?.homeBranchCode],
  );
  const effectiveBranchId = isHeadOfficeScoped
    ? ""
    : candidateBranch?.id ?? "";

  function applyCandidate(candidate: ModuleUserCandidate) {
    // Identity only — role is chosen by admin, Unit is derived from admin scope.
    setSelectedCandidate(candidate);
    setSearchQuery(`${candidate.displayName} (${candidate.username})`);
    setForm((f) => ({
      ...f,
      username: candidate.username,
      fullName: candidate.displayName,
      email: candidate.email,
      roleId: "",
    }));
    setFieldError(null);
    setError(null);
  }

  function clearCandidate() {
    setSelectedCandidate(null);
    setSearchQuery("");
    setForm(emptyForm());
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setFieldError(null);

    if (!selectedCandidate) {
      setFieldError(t("selectCandidateRequired"));
      return;
    }
    if (!form.roleId) {
      setFieldError(t("selectRole"));
      return;
    }
    if (branchRequired && !effectiveBranchId) {
      setFieldError(t("branchRequiredForRole"));
      return;
    }

    setSubmitting(true);
    try {
      const created = await createUser({
        username: form.username.trim(),
        email: form.email.trim(),
        fullName: form.fullName.trim(),
        password: opaqueModeAPassword(),
        roleId: form.roleId,
        branchId: effectiveBranchId || null,
        isActive: form.isActive,
      });
      onCreated(created.fullName || created.username);
      onClose();
    } catch (err) {
      setError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToCreate"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={() => {
        if (!submitting) onClose();
      }}
      title={t("createUserTitle")}
      size="md"
      footer={
        <>
          <Button
            type="button"
            variant="outline"
            disabled={submitting}
            onClick={onClose}
          >
            {tCommon("cancel")}
          </Button>
          <Button
            type="submit"
            form="create-user-form"
            disabled={submitting || loadingLookups || !selectedCandidate}
          >
            {submitting ? t("creating") : t("createUser")}
          </Button>
        </>
      }
    >
      <p className="mb-[var(--ecmp-form-gap)] text-sm text-ecmp-text-secondary">
        {t("createUserDescription")}
      </p>
      {error ? (
        <Alert tone="danger" title={t("actionFailed")} description={error} />
      ) : null}
      {fieldError ? (
        <Alert tone="danger" title={t("actionFailed")} description={fieldError} />
      ) : null}
      <form
        id="create-user-form"
        className="space-y-[var(--ecmp-form-gap)]"
        onSubmit={onSubmit}
      >
        <div className="relative space-y-2">
          <Input
            name="candidateSearch"
            label={t("candidateSearch")}
            required
            autoComplete="off"
            value={searchQuery}
            disabled={submitting || loadingLookups || Boolean(selectedCandidate)}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setSelectedCandidate(null);
              setForm(emptyForm());
            }}
            hint={t("candidateSearchHelper")}
            placeholder={t("candidateSearchPlaceholder")}
          />
          {selectedCandidate ? (
            <Button
              type="button"
              variant="outline"
              className="min-h-[var(--ecmp-touch-min)]"
              disabled={submitting}
              onClick={clearCandidate}
            >
              {t("clearCandidate")}
            </Button>
          ) : null}
          {!selectedCandidate && searchHits.length > 0 ? (
            <ul
              className="max-h-56 overflow-auto rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface p-1 shadow-sm"
              role="listbox"
              aria-label={t("candidateResults")}
            >
              {searchHits.map((row) => (
                <li key={row.username}>
                  <button
                    type="button"
                    className="flex w-full flex-col gap-0.5 rounded-[var(--ecmp-radius-sm)] px-3 py-2 text-left hover:bg-ecmp-surface-muted"
                    onClick={() => applyCandidate(row)}
                  >
                    <HighlightedText
                      text={row.displayName}
                      query={searchQuery}
                      className="text-sm font-medium text-ecmp-text"
                    />
                    <span className="text-xs text-ecmp-text-secondary">
                      <HighlightedText text={row.username} query={searchQuery} />
                      {" · "}
                      {row.homeBranchName}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
          {!selectedCandidate &&
          searchQuery.trim().length >= 1 &&
          searchHits.length === 0 &&
          !loadingLookups ? (
            <p className="text-sm text-ecmp-text-secondary">
              {t("candidateNotFound")}
            </p>
          ) : null}
        </div>

        {/* Enterprise Directory information — displayed only, never edited here. */}
        <p className="text-sm text-ecmp-text-secondary">
          {t("identityFromDirectory")}
        </p>
        <Input
          name="fullName"
          label={t("fullName")}
          required
          value={form.fullName}
          disabled
          readOnly
        />
        <Input
          name="username"
          label={t("employeeId")}
          required
          autoComplete="off"
          value={form.username}
          disabled
          readOnly
        />
        <Input
          name="email"
          type="email"
          label={t("email")}
          required
          autoComplete="off"
          value={form.email}
          disabled
          readOnly
        />
        <Select
          name="roleId"
          label={t("role")}
          required
          value={form.roleId}
          disabled={submitting || loadingLookups || !selectedCandidate}
          onChange={(e) =>
            setForm((f) => ({ ...f, roleId: e.target.value }))
          }
          options={[
            { value: "", label: t("selectRole") },
            ...availableRoles.map((row) => ({
              value: row.id,
              label: `${roleDisplayName(row, t("roleBranchManager"))} (${row.code})`,
            })),
          ]}
        />
        <Input
          name="branchId"
          label={t("unit")}
          value={
            isHeadOfficeScoped
              ? t("locationHeadOffice")
              : candidateBranch
                ? `${candidateBranch.code} — ${candidateBranch.name}`
                : selectedCandidate
                  ? candidateAtHeadOffice
                    ? t("locationHeadOffice")
                    : t("unitUnknown")
                  : ""
          }
          disabled
          readOnly
          hint={
            isHeadOfficeScoped
              ? t("unitHeadOfficeHint")
              : t("unitFromDirectoryHint")
          }
        />
        <Select
          name="isActive"
          label={t("initialStatus")}
          value={form.isActive ? "true" : "false"}
          disabled={submitting || !selectedCandidate}
          onChange={(e) =>
            setForm((f) => ({ ...f, isActive: e.target.value === "true" }))
          }
          options={[
            { value: "true", label: t("statusActive") },
            { value: "false", label: t("statusInactive") },
          ]}
        />
      </form>
    </Modal>
  );
}
