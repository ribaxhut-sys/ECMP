import type { AuthMe } from "@/lib/api/types";

export type MockPersonaId =
  | "complaint_officer"
  | "supervisor"
  | "manager"
  | "administrator";

/** Officer work mode — maps to NAV-001 Entry Points (B0). */
export type OfficerWorkMode = "intake" | "handling";

export interface MockSession {
  user: AuthMe;
  persona: MockPersonaId;
  officerWorkMode: OfficerWorkMode;
}

const STORAGE_KEY = "ecmp.mock.auth.v1";

/** Shell-scoped permission placeholders (nav hide/show only — not backend AuthZ). */
export const SHELL_PERMISSIONS = {
  workspaceIntake: "shell:workspace_intake",
  queueAssigned: "shell:queue_assigned",
  queueSupervisor: "shell:queue_supervisor",
  settings: "shell:settings",
  adminDirectory: "shell:admin",
} as const;

function buildUser(
  id: string,
  username: string,
  fullName: string,
  roleLabel: string,
  permissions: string[],
): AuthMe {
  const now = new Date().toISOString();
  return {
    id,
    username,
    email: `${username}@ecmp.local`,
    fullName,
    roleId: id,
    branchId: "branch-lab-01",
    isActive: true,
    forcePasswordChange: false,
    lastLoginAt: now,
    createdAt: now,
    updatedAt: now,
    preferredLanguage: "en",
    roles: [roleLabel],
    permissions,
  };
}

export interface MockAccount {
  username: string;
  /** Any non-empty password accepted in mock mode. */
  persona: MockPersonaId;
  officerWorkMode: OfficerWorkMode;
  user: AuthMe;
}

export const MOCK_ACCOUNTS: readonly MockAccount[] = [
  {
    username: "officer",
    persona: "complaint_officer",
    officerWorkMode: "intake",
    user: buildUser(
      "mock-officer",
      "officer",
      "Demo CRO",
      "CRO",
      [
        SHELL_PERMISSIONS.workspaceIntake,
        SHELL_PERMISSIONS.queueAssigned,
      ],
    ),
  },
  {
    username: "supervisor",
    persona: "supervisor",
    officerWorkMode: "handling",
    user: buildUser(
      "mock-supervisor",
      "supervisor",
      "Demo Staff KaSatPel",
      "Staff KaSatPel",
      [SHELL_PERMISSIONS.queueSupervisor],
    ),
  },
  {
    username: "manager",
    persona: "manager",
    officerWorkMode: "handling",
    user: buildUser(
      "mock-manager",
      "manager",
      "Demo KaSatPel",
      "KaSatPel",
      [],
    ),
  },
  {
    username: "admin",
    persona: "administrator",
    officerWorkMode: "handling",
    user: buildUser(
      "mock-admin",
      "admin",
      "Demo Administrator",
      "Administrator",
      [SHELL_PERMISSIONS.settings, SHELL_PERMISSIONS.adminDirectory],
    ),
  },
] as const;

export function findMockAccount(username: string): MockAccount | undefined {
  const key = username.trim().toLowerCase();
  return MOCK_ACCOUNTS.find((a) => a.username === key);
}

export function readMockSession(): MockSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as MockSession;
    if (!parsed?.user?.id || !parsed.persona) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writeMockSession(session: MockSession): void {
  window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function clearMockSession(): void {
  window.sessionStorage.removeItem(STORAGE_KEY);
}

export function mockLogin(
  username: string,
  password: string,
): MockSession {
  if (!password.trim()) {
    throw new Error("MOCK_PASSWORD_REQUIRED");
  }
  const account = findMockAccount(username);
  if (!account) {
    throw new Error("MOCK_USER_NOT_FOUND");
  }
  const session: MockSession = {
    user: account.user,
    persona: account.persona,
    officerWorkMode: account.officerWorkMode,
  };
  writeMockSession(session);
  return session;
}

export function updateOfficerWorkMode(mode: OfficerWorkMode): MockSession | null {
  const current = readMockSession();
  if (!current || current.persona !== "complaint_officer") return null;
  const next: MockSession = { ...current, officerWorkMode: mode };
  writeMockSession(next);
  return next;
}

/** Post-login Entry Point per NAV-001 / WF-001-R1 B0. */
export function mockEntryHref(session: MockSession): string {
  switch (session.persona) {
    case "complaint_officer":
      return session.officerWorkMode === "intake" ? "/workspace" : "/queue";
    case "supervisor":
      return "/queue";
    case "administrator":
      return "/settings";
    case "manager":
      return "/workspace";
    default:
      return "/workspace";
  }
}
