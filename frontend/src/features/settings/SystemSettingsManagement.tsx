"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type KeyboardEvent,
} from "react";
import { useRouter } from "next/navigation";
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
  CardHeader,
  Empty,
  ErrorState,
  Input,
  PanelHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useToast } from "@/shared/providers";
import {
  localizedSettingDescription,
  localizedSettingTitle,
  matchesSearch,
  settingStatus,
} from "./configurationSections";

export function SystemSettingsManagement({
  searchQuery = "",
  onClearSearch,
}: {
  searchQuery?: string;
  onClearSearch?: () => void;
}) {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();
  const { pushSuccess } = useToast();
  const canRead = hasPermission("settings:read");
  const canUpdate = hasPermission("settings:update");

  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
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

  const categoryLabel = useCallback(
    (category: string): string => {
      const map: Record<string, string> = {
        app: t("categoryApp"),
        company: t("categoryCompany"),
        complaint: t("categoryComplaint"),
        dashboard: t("categoryDashboard"),
        notification: t("categoryNotification"),
        storage: t("categoryStorage"),
        hq_schedule: t("categoryHqSchedule"),
      };
      return map[category] ?? category.replace(/\b\w/g, (c) => c.toUpperCase());
    },
    [t],
  );

  const statusLabel = useCallback(
    (key: ReturnType<typeof settingStatus>["key"]): string => {
      switch (key) {
        case "configured":
          return t("statusConfigured");
        case "needsReview":
          return t("statusNeedsReview");
        case "disabled":
          return t("statusDisabled");
        case "default":
          return t("statusDefault");
        default:
          return t("statusConfigured");
      }
    },
    [t],
  );

  const settingTitle = useCallback(
    (row: Setting): string => localizedSettingTitle(row, t),
    [t],
  );

  const settingDescription = useCallback(
    (row: Setting): string =>
      localizedSettingDescription(row, t, t("settingValueHelper")),
    [t],
  );

  const filteredSettings = useMemo(() => {
    return settings.filter((row) =>
      matchesSearch(
        searchQuery,
        settingTitle(row),
        settingDescription(row),
        row.key,
        row.description,
        categoryLabel(row.category),
        row.value,
      ),
    );
  }, [categoryLabel, searchQuery, settingDescription, settingTitle, settings]);

  const grouped = useMemo(() => {
    const map = new Map<string, Setting[]>();
    for (const row of filteredSettings) {
      const key = row.category || "app";
      const list = map.get(key) ?? [];
      list.push(row);
      map.set(key, list);
    }
    return [...map.entries()].sort(([a], [b]) =>
      categoryLabel(a).localeCompare(categoryLabel(b)),
    );
  }, [categoryLabel, filteredSettings]);

  function startEdit(row: Setting) {
    setEditingKey(row.key);
    setDraftValue(row.value);
    setActionError(null);
  }

  function cancelEdit() {
    setEditingKey(null);
    setDraftValue("");
  }

  async function submitSave(): Promise<void> {
    if (!editingKey || !canUpdate || saving) return;
    const current = settings.find((item) => item.key === editingKey);
    if (current && draftValue === current.value) {
      cancelEdit();
      return;
    }
    setSaving(true);
    setActionError(null);
    try {
      const res = await updateSetting(editingKey, { value: draftValue });
      setSettings((prev) =>
        prev.map((item) => (item.key === editingKey ? res.data : item)),
      );
      pushSuccess(
        t("saved"),
        t("updatedSettingMessage", {
          name: settingTitle(res.data),
        }),
      );
      cancelEdit();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUpdateSetting"),
      );
    } finally {
      setSaving(false);
    }
  }

  function onDraftKeyDown(event: KeyboardEvent<HTMLInputElement>): void {
    if (event.key === "Escape") {
      event.preventDefault();
      if (!saving) cancelEdit();
      return;
    }
    if (event.key === "Enter") {
      event.preventDefault();
      void submitSave();
    }
  }

  if (!canRead) {
    return (
      <Empty
        title={tCommon("accessRestricted")}
        description={t("accessRestrictedSystem")}
        primaryAction={{
          label: tCommon("goHome"),
          onClick: () => router.push("/dashboard"),
        }}
      />
    );
  }

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      data-testid="system-settings-card"
    >
      <SectionHeader
        title={t("systemSettingsTitle")}
        description={t("systemSettingsDescription")}
      />

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

      {loading ? (
        <Skeleton rows={5} />
      ) : !loadError && grouped.length === 0 ? (
        <Empty
          title={t("noSettingsFound")}
          description={
            searchQuery.trim()
              ? t("noSettingsMatchSearch")
              : t("noSettingsFoundDescription")
          }
          primaryAction={{
            label: t("refreshSettings"),
            onClick: () => void load(),
          }}
          secondaryAction={
            searchQuery.trim() && onClearSearch
              ? {
                  label: t("clearSearch"),
                  onClick: onClearSearch,
                }
              : undefined
          }
        />
      ) : !loadError ? (
        <div className="space-y-[var(--ecmp-card-gap)]">
          {grouped.map(([category, rows]) => (
            <Card key={category}>
              <CardHeader
                action={
                  <Badge tone="info">
                    {t("categorySettingsCount", { count: rows.length })}
                  </Badge>
                }
              >
                <PanelHeader
                  title={categoryLabel(category)}
                  description={t("categoryGroupDescription", {
                    category: categoryLabel(category),
                  })}
                  className="mb-0 border-0 pb-0"
                />
              </CardHeader>
              <CardBody className="space-y-[var(--ecmp-panel-gap)]">
                {rows.map((row) => {
                  const title = settingTitle(row);
                  const description = settingDescription(row);
                  const status = settingStatus(row);
                  const editing = editingKey === row.key;

                  return (
                    <article
                      key={row.id}
                      data-testid={`setting-key-${row.key}`}
                      className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-[var(--ecmp-panel-gap)]"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="min-w-0 space-y-1">
                          <h4 className="text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] text-ecmp-text-primary">
                            {title}
                          </h4>
                          <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                            {description}
                          </p>
                        </div>
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge tone={status.tone}>{statusLabel(status.key)}</Badge>
                          <Badge tone="neutral" variant="outline">
                            {row.visibility === "PUBLIC"
                              ? t("visibilityPublic")
                              : t("visibilityProtected")}
                          </Badge>
                        </div>
                      </div>

                      <div className="mt-3 space-y-3">
                        {editing ? (
                          <Input
                            name={`setting-${row.key}`}
                            value={draftValue}
                            onChange={(e) => setDraftValue(e.target.value)}
                            onKeyDown={onDraftKeyDown}
                            label={t("valueColumn")}
                            aria-label={t("valueAriaLabel", { key: title })}
                            autoFocus
                          />
                        ) : (
                          <p className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface px-3 py-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                            {row.value === "" ? tCommon("emDash") : row.value}
                          </p>
                        )}

                        {canUpdate ? (
                          <div className="flex flex-wrap gap-2">
                            {editing ? (
                              <>
                                <Button
                                  type="button"
                                  size="sm"
                                  loading={saving}
                                  onClick={() => void submitSave()}
                                  className="min-h-[var(--ecmp-touch-min)]"
                                >
                                  {tCommon("save")}
                                </Button>
                                <Button
                                  type="button"
                                  size="sm"
                                  variant="outline"
                                  onClick={cancelEdit}
                                  disabled={saving}
                                  className="min-h-[var(--ecmp-touch-min)]"
                                >
                                  {tCommon("cancel")}
                                </Button>
                              </>
                            ) : (
                              <Button
                                type="button"
                                size="sm"
                                variant="secondary"
                                onClick={() => startEdit(row)}
                                disabled={editingKey !== null}
                                className="min-h-[var(--ecmp-touch-min)]"
                              >
                                {tCommon("edit")}
                              </Button>
                            )}
                          </div>
                        ) : null}
                      </div>
                    </article>
                  );
                })}
              </CardBody>
            </Card>
          ))}
        </div>
      ) : null}
    </section>
  );
}
