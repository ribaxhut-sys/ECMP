"use client";

import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { fetchSettings, updateSetting } from "@/lib/api";
import type { Setting } from "@/lib/api/types";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  Input,
  SectionHeader,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

export function SystemSettingsManagement() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();
  const canRead = hasPermission("settings:read");
  const canUpdate = hasPermission("settings:update");

  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [draftValue, setDraftValue] = useState("");
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      setSettings([]);
      setLoadError(null);
      return;
    }
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchSettings();
      setSettings(res.data);
    } catch (err) {
      setSettings([]);
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

  function startEdit(row: Setting) {
    setEditingKey(row.key);
    setDraftValue(row.value);
    setActionError(null);
    setActionSuccess(null);
  }

  function cancelEdit() {
    setEditingKey(null);
    setDraftValue("");
  }

  async function onSave(event: FormEvent) {
    event.preventDefault();
    if (!editingKey || !canUpdate) return;
    setSaving(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      const res = await updateSetting(editingKey, { value: draftValue });
      setSettings((prev) =>
        prev.map((item) => (item.key === editingKey ? res.data : item)),
      );
      setActionSuccess(t("updatedKeyMessage", { key: editingKey }));
      cancelEdit();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUpdateSetting"),
      );
    } finally {
      setSaving(false);
    }
  }

  const categoryLabel = (category: string): string => {
    const map: Record<string, string> = {
      app: t("categoryApp"),
      company: t("categoryCompany"),
      complaint: t("categoryComplaint"),
      dashboard: t("categoryDashboard"),
      notification: t("categoryNotification"),
      storage: t("categoryStorage"),
    };
    return map[category] ?? category;
  };

  const visibilityLabel = (visibility: string): string => {
    if (visibility === "PUBLIC") return t("visibilityPublic");
    if (visibility === "PROTECTED") return t("visibilityProtected");
    return visibility;
  };

  if (!canRead) {
    return (
      <Empty
        title={tCommon("accessRestricted")}
        description={t("accessRestrictedSystem")}
      />
    );
  }

  const columns: TableColumn<Setting>[] = [
    {
      key: "key",
      header: t("keyColumn"),
      cell: (row) => <code data-testid={`setting-key-${row.key}`}>{row.key}</code>,
    },
    {
      key: "value",
      header: t("valueColumn"),
      cell: (row) =>
        editingKey === row.key ? (
          <Input
            value={draftValue}
            onChange={(e) => setDraftValue(e.target.value)}
            aria-label={t("valueAriaLabel", { key: row.key })}
          />
        ) : (
          <span>{row.value === "" ? "—" : row.value}</span>
        ),
    },
    {
      key: "valueType",
      header: t("typeColumn"),
      cell: (row) => <Badge tone="info">{row.valueType}</Badge>,
    },
    {
      key: "visibility",
      header: t("visibilityColumn"),
      cell: (row) => (
        <Badge tone={row.visibility === "PUBLIC" ? "success" : "neutral"}>
          {visibilityLabel(row.visibility)}
        </Badge>
      ),
    },
    {
      key: "category",
      header: t("categoryColumn"),
      cell: (row) => categoryLabel(row.category),
    },
    {
      key: "actions",
      header: tCommon("actions"),
      hideOnMobile: false,
      cell: (row) => {
        if (!canUpdate) return null;
        if (editingKey === row.key) {
          return (
            <div className="flex flex-wrap gap-2">
              <Button type="submit" size="sm" loading={saving}>
                {tCommon("save")}
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={cancelEdit}
                disabled={saving}
              >
                {tCommon("cancel")}
              </Button>
            </div>
          );
        }
        return (
          <Button
            type="button"
            size="sm"
            variant="secondary"
            onClick={() => startEdit(row)}
            disabled={editingKey !== null}
          >
            {tCommon("edit")}
          </Button>
        );
      },
    },
  ];

  return (
    <section className="space-y-[var(--ecmp-panel-gap)]" data-testid="system-settings-card">
      <SectionHeader
        title={t("systemSettingsTitle")}
        description={t("systemSettingsDescription")}
      />
      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {loadError ? (
            <ErrorState
              title={t("unableToLoad")}
              message={loadError}
              onRetry={() => void load()}
            />
          ) : null}
          {actionError ? (
            <Alert tone="danger" title={t("updateFailed")} description={actionError} />
          ) : null}
          {actionSuccess ? (
            <Alert tone="success" title={t("saved")} description={actionSuccess} />
          ) : null}
          <form onSubmit={onSave}>
            {loading ? (
              <Skeleton rows={5} />
            ) : !loadError ? (
              <Table
                columns={columns}
                rows={settings}
                getRowKey={(row) => row.key}
                emptyMessage={t("noSettingsFound")}
              />
            ) : null}
          </form>
        </CardBody>
      </Card>
    </section>
  );
}
