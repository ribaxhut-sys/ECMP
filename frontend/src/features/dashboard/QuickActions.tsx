"use client";

import { useAuth } from "@/auth/AuthProvider";
import { EmptyBlock, Panel } from "./ui";
import { QUICK_ACTIONS } from "./quickActionConfig";

function scrollToId(id: string): void {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

export function QuickActions({ onRefresh }: { onRefresh: () => void }) {
  const { hasPermission } = useAuth();
  const actions = QUICK_ACTIONS.filter((action) =>
    hasPermission(action.permission),
  );

  function handleAction(actionId: string): void {
    switch (actionId) {
      case "refresh-reports":
        onRefresh();
        break;
      case "view-complaints":
      case "create-complaint":
      case "assign-complaint":
      case "escalate-complaint":
        scrollToId("latest-complaints");
        break;
      case "manage-users":
      case "create-user":
        scrollToId("quick-actions");
        break;
      default:
        break;
    }
  }

  return (
    <Panel title="Quick Actions">
      <div id="quick-actions" />
      {actions.length === 0 ? (
        <EmptyBlock message="No actions available for your permissions." />
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {actions.map((action) => (
            <button
              key={action.id}
              type="button"
              onClick={() => handleAction(action.id)}
              title={action.description}
              className="rounded-lg border border-white/10 bg-black/20 px-4 py-3 text-left transition hover:border-[var(--accent)]/50 hover:bg-black/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
            >
              <span className="block text-sm font-semibold text-[var(--ink)]">
                {action.label}
              </span>
              <span className="mt-1 block text-xs text-[var(--muted)]">
                {action.description}
              </span>
            </button>
          ))}
        </div>
      )}
    </Panel>
  );
}
