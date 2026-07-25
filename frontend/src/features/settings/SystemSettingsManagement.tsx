"use client";

import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from "react";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchSettings, updateSetting } from "@/lib/api";
import type { Setting } from "@/lib/api/types";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Empty,
  ErrorState,
  Input,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";

export function SystemSettingsManagement() {
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
        err instanceof ApiError
          ? err.message
          : "Unable to load system settings.",
      );
    } finally {
      setLoading(false);
    }
  }, [canRead]);

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
      setActionSuccess(`Updated ${editingKey}.`);
      cancelEdit();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : "Unable to update setting.",
      );
    } finally {
      setSaving(false);
    }
  }

  if (!canRead) {
    return (
      <Empty
        title="Access restricted"
        description="You need the settings:read permission to view system settings."
      />
    );
  }

  const columns: TableColumn<Setting>[] = [
    {
      key: "key",
      header: "Key",
      cell: (row) => <code data-testid={`setting-key-${row.key}`}>{row.key}</code>,
    },
    {
      key: "value",
      header: "Value",
      cell: (row) =>
        editingKey === row.key ? (
          <Input
            value={draftValue}
            onChange={(e) => setDraftValue(e.target.value)}
            aria-label={`Value for ${row.key}`}
          />
        ) : (
          <span>{row.value === "" ? "—" : row.value}</span>
        ),
    },
    {
      key: "valueType",
      header: "Type",
      cell: (row) => <Badge tone="info">{row.valueType}</Badge>,
    },
    {
      key: "visibility",
      header: "Visibility",
      cell: (row) => (
        <Badge tone={row.visibility === "PUBLIC" ? "success" : "neutral"}>
          {row.visibility}
        </Badge>
      ),
    },
    {
      key: "category",
      header: "Category",
      cell: (row) => row.category,
    },
    {
      key: "actions",
      header: "Actions",
      hideOnMobile: false,
      cell: (row) => {
        if (!canUpdate) return null;
        if (editingKey === row.key) {
          return (
            <div className="flex flex-wrap gap-2">
              <Button type="submit" size="sm" loading={saving}>
                Save
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={cancelEdit}
                disabled={saving}
              >
                Cancel
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
            Edit
          </Button>
        );
      },
    },
  ];

  return (
    <Card data-testid="system-settings-card">
      <CardHeader>
        <CardTitle>System Settings</CardTitle>
        <CardDescription>
          Application configuration keys (typed values, PUBLIC / PROTECTED).
        </CardDescription>
      </CardHeader>
      <CardBody className="space-y-4">
        {loadError ? (
          <ErrorState
            title="Unable to load settings"
            message={loadError}
            onRetry={() => void load()}
          />
        ) : null}
        {actionError ? (
          <Alert tone="danger" title="Update failed" description={actionError} />
        ) : null}
        {actionSuccess ? (
          <Alert tone="success" title="Saved" description={actionSuccess} />
        ) : null}
        <form onSubmit={onSave}>
          {loading ? (
            <Skeleton rows={5} />
          ) : !loadError ? (
            <Table
              columns={columns}
              rows={settings}
              getRowKey={(row) => row.key}
              emptyMessage="No settings found."
            />
          ) : null}
        </form>
      </CardBody>
    </Card>
  );
}
