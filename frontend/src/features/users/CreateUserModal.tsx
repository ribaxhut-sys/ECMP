"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {
  createUser,
  fetchBranches,
  fetchRoles,
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
import { filterRolesForUserForm, roleDisplayName } from "./directoryHelpers";

/** Mirrors backend BRANCH_SCOPED_ROLE_CODES. */
export const BRANCH_SCOPED_ROLE_CODES = new Set([
  "AGENT",
  "CS_AGENT",
  "BRANCH_OFFICER",
  "SUPERVISOR",
  "BRANCH_SUPERVISOR",
]);

/** Mirrors backend HEAD_OFFICE_SCOPED_ROLE_CODES (Commit 2). */
export const HEAD_OFFICE_SCOPED_ROLE_CODES = new Set([
  "ADMIN",
  "ADMINISTRATOR",
  "HO_SCHEDULER",
  "HEAD_OFFICE_SCHEDULER",
  "SCHEDULER",
  "HO_ENGINEER",
  "HEAD_OFFICE_ENGINEER",
]);

type CreateUserModalProps = {
  open: boolean;
  onClose: () => void;
  onCreated: (username: string) => void;
};

type FormState = {
  username: string;
  email: string;
  fullName: string;
  password: string;
  roleId: string;
  branchId: string;
  isActive: boolean;
};

const emptyForm = (): FormState => ({
  username: "",
  email: "",
  fullName: "",
  password: "",
  roleId: "",
  branchId: "",
  isActive: true,
});

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
  const [loadingLookups, setLoadingLookups] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setForm(emptyForm());
    setError(null);
    setFieldError(null);
    setLoadingLookups(true);
    void (async () => {
      try {
        const [roleRows, branchRes] = await Promise.all([
          fetchRoles({ activeOnly: true, includeSystem: true }),
          fetchBranches(100),
        ]);
        setRoles(filterRolesForUserForm(roleRows.filter((row) => row.isActive)));
        setBranches(branchRes.data);
      } catch (err) {
        setError(
          resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"),
        );
      } finally {
        setLoadingLookups(false);
      }
    })();
  }, [open, t, tCommon, tErrors]);

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

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setFieldError(null);

    if (!form.roleId) {
      setFieldError(t("selectRole"));
      return;
    }
    if (branchRequired && !form.branchId) {
      setFieldError(t("branchRequiredForRole"));
      return;
    }
    if (isHeadOfficeScoped && form.branchId) {
      setFieldError(t("branchNotAllowedForRole"));
      return;
    }

    setSubmitting(true);
    try {
      const created = await createUser({
        username: form.username.trim(),
        email: form.email.trim(),
        fullName: form.fullName.trim(),
        password: form.password,
        roleId: form.roleId,
        branchId: isHeadOfficeScoped ? null : form.branchId || null,
        isActive: form.isActive,
      });
      onCreated(created.username);
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
            disabled={submitting || loadingLookups}
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
        <Input
          name="fullName"
          label={t("fullName")}
          required
          value={form.fullName}
          disabled={submitting}
          onChange={(e) => setForm((f) => ({ ...f, fullName: e.target.value }))}
        />
        <Input
          name="username"
          label={t("username")}
          required
          autoComplete="off"
          value={form.username}
          disabled={submitting}
          onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
        />
        <Input
          name="email"
          type="email"
          label={t("email")}
          required
          autoComplete="off"
          value={form.email}
          disabled={submitting}
          onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
        />
        <Input
          name="password"
          type="password"
          label={t("password")}
          required
          minLength={8}
          autoComplete="new-password"
          value={form.password}
          disabled={submitting}
          onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
          hint={t("forcePasswordChange")}
        />
        <Select
          name="roleId"
          label={t("role")}
          required
          value={form.roleId}
          disabled={submitting || loadingLookups}
          onChange={(e) => {
            const roleId = e.target.value;
            const role = roles.find((row) => row.id === roleId);
            const needsBranch =
              role != null && BRANCH_SCOPED_ROLE_CODES.has(role.code);
            setForm((f) => ({
              ...f,
              roleId,
              branchId: needsBranch ? f.branchId : "",
            }));
          }}
          options={[
            { value: "", label: t("selectRole") },
            ...roles.map((row) => ({
              value: row.id,
              label: `${roleDisplayName(row, t("roleBranchManager"))} (${row.code})`,
            })),
          ]}
        />
        <Select
          name="branchId"
          label={
            isHeadOfficeScoped
              ? t("headOfficeFixed")
              : branchRequired
                ? t("branchRequired")
                : t("branchOptional")
          }
          required={branchRequired}
          value={isHeadOfficeScoped ? "" : form.branchId}
          disabled={submitting || loadingLookups || isHeadOfficeScoped}
          onChange={(e) =>
            setForm((f) => ({ ...f, branchId: e.target.value }))
          }
          options={[
            {
              value: "",
              label: isHeadOfficeScoped
                ? t("headOfficeFixed")
                : branchRequired
                  ? t("selectBranch")
                  : t("noBranch"),
            },
            ...branches.map((row) => ({
              value: row.id,
              label: `${row.code} — ${row.name}`,
            })),
          ]}
        />
      </form>
    </Modal>
  );
}
