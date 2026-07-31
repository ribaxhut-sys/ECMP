"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  createUser,
  fetchBranches,
  fetchRoles,
  fetchUsers,
  type Branch,
  type RoleRef,
  type UserRef,
} from "@/lib/api";
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
  Input,
  Select,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";

export function UsersManagement() {
  const { hasPermission } = useAuth();
  const canRead = hasPermission("users:read");
  const canCreate = hasPermission("users:create");
  const canReadRoles = hasPermission("role:read") || hasPermission("*");

  const [users, setUsers] = useState<UserRef[]>([]);
  const [roles, setRoles] = useState<RoleRef[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [roleId, setRoleId] = useState("");
  const [branchId, setBranchId] = useState("");

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      setUsers([]);
      setLoadError(null);
      return;
    }
    setLoading(true);
    setLoadError(null);
    try {
      const [usersRes, rolesRes, branchesRes] = await Promise.all([
        fetchUsers({ pageSize: 100 }),
        canReadRoles
          ? fetchRoles({ activeOnly: true }).catch(() => ({ data: [] as RoleRef[] }))
          : Promise.resolve({ data: [] as RoleRef[] }),
        fetchBranches(100).catch(() => ({ data: [] as Branch[], meta: { page: 1, pageSize: 100, totalItems: 0 } })),
      ]);
      setUsers(usersRes.data);
      setRoles(rolesRes.data);
      setBranches(branchesRes.data);
      setRoleId((current) => {
        if (current) return current;
        if (rolesRes.data.length === 0) return current;
        const agent = rolesRes.data.find((r) => r.code === "AGENT");
        return (agent ?? rolesRes.data[0]).id;
      });
    } catch (err) {
      setUsers([]);
      setLoadError(
        err instanceof ApiError ? err.message : "Unable to load users.",
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, canReadRoles]);

  useEffect(() => {
    void load();
  }, [load]);

  const roleOptions = useMemo(
    () =>
      roles.map((role) => ({
        value: role.id,
        label: `${role.code} — ${role.name}`,
      })),
    [roles],
  );

  const branchOptions = useMemo(
    () => [
      { value: "", label: "No branch" },
      ...branches.map((branch) => ({
        value: branch.id,
        label: `${branch.code} — ${branch.name}`,
      })),
    ],
    [branches],
  );

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    if (!canCreate) return;
    setSaving(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      const res = await createUser({
        username: username.trim(),
        email: email.trim(),
        fullName: fullName.trim(),
        password,
        roleId,
        branchId: branchId || null,
        isActive: true,
      });
      setActionSuccess(`Created user ${res.data.username}.`);
      setUsername("");
      setEmail("");
      setFullName("");
      setPassword("");
      await load();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : "Unable to create user.",
      );
    } finally {
      setSaving(false);
    }
  }

  if (!canRead) {
    return (
      <Alert
        tone="warning"
        title="Access restricted"
        description={
          <>
            You need the <code>users:read</code> permission to view users.
          </>
        }
      />
    );
  }

  const columns: TableColumn<UserRef>[] = [
    {
      key: "username",
      header: "Username",
      cell: (row) => (
        <span className="font-medium text-ecmp-text-primary">{row.username}</span>
      ),
    },
    {
      key: "fullName",
      header: "Name",
      cell: (row) => row.fullName,
    },
    {
      key: "email",
      header: "Email",
      cell: (row) => (
        <span className="text-ecmp-text-secondary">{row.email}</span>
      ),
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
  ];

  return (
    <div className="grid gap-6">
      {canCreate ? (
        <Card>
          <CardHeader>
            <CardTitle>Create user</CardTitle>
            <CardDescription>
              New accounts receive IAM permissions automatically (user_roles sync).
            </CardDescription>
          </CardHeader>
          <CardBody>
            {!canReadRoles || roleOptions.length === 0 ? (
              <form onSubmit={onCreate} className="grid gap-4 md:grid-cols-2">
                <Alert
                  tone="warning"
                  title="Role catalog limited"
                  description="role:read is missing — paste a role UUID (from admin) to create a user."
                />
                <Input
                  name="username"
                  label="Username"
                  required
                  minLength={3}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="off"
                />
                <Input
                  name="email"
                  label="Email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="off"
                />
                <Input
                  name="fullName"
                  label="Full name"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
                <Input
                  name="password"
                  label="Password"
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
                />
                <Input
                  name="roleId"
                  label="Role ID (UUID)"
                  required
                  value={roleId}
                  onChange={(e) => setRoleId(e.target.value)}
                  hint="Ask an admin for AGENT / SUPERVISOR role id."
                />
                <Select
                  name="branchId"
                  label="Branch"
                  options={branchOptions}
                  value={branchId}
                  onChange={(e) => setBranchId(e.target.value)}
                />
                <div className="md:col-span-2">
                  <Button type="submit" disabled={saving || !roleId}>
                    {saving ? "Creating…" : "Create user"}
                  </Button>
                </div>
              </form>
            ) : (
              <form onSubmit={onCreate} className="grid gap-4 md:grid-cols-2">
                <Input
                  name="username"
                  label="Username"
                  required
                  minLength={3}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="off"
                />
                <Input
                  name="email"
                  label="Email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="off"
                />
                <Input
                  name="fullName"
                  label="Full name"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
                <Input
                  name="password"
                  label="Password"
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
                />
                <Select
                  name="roleId"
                  label="Role"
                  required
                  options={roleOptions}
                  value={roleId}
                  onChange={(e) => setRoleId(e.target.value)}
                />
                <Select
                  name="branchId"
                  label="Branch"
                  options={branchOptions}
                  value={branchId}
                  onChange={(e) => setBranchId(e.target.value)}
                />
                <div className="md:col-span-2">
                  <Button type="submit" disabled={saving || !roleId}>
                    {saving ? "Creating…" : "Create user"}
                  </Button>
                </div>
              </form>
            )}
            {actionError ? (
              <div className="mt-4">
                <Alert tone="danger" title="Create failed" description={actionError} />
              </div>
            ) : null}
            {actionSuccess ? (
              <div className="mt-4">
                <Alert tone="success" title="Created" description={actionSuccess} />
              </div>
            ) : null}
          </CardBody>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Directory</CardTitle>
          <CardDescription>
            Active and inactive users visible to your role.
          </CardDescription>
        </CardHeader>
        <CardBody>
          {loadError ? (
            <Alert tone="danger" title="Unable to load users" description={loadError} />
          ) : null}
          {loading ? (
            <Skeleton rows={5} />
          ) : users.length === 0 ? (
            <Empty
              title="No users"
              description="Create the first account above, or seed lab users via API."
            />
          ) : (
            <Table
              columns={columns}
              rows={users}
              getRowKey={(row) => row.id}
            />
          )}
        </CardBody>
      </Card>
    </div>
  );
}
