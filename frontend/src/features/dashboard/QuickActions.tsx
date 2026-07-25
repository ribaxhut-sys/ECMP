"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { Button, Card, CardBody, CardHeader, CardTitle, Empty } from "@/shared/ui";
import { QUICK_ACTIONS } from "./quickActionConfig";

export function QuickActions({ onRefresh }: { onRefresh: () => void }) {
  const router = useRouter();
  const { hasPermission } = useAuth();
  const actions = QUICK_ACTIONS.filter((action) =>
    hasPermission(action.permission),
  );

  function handleAction(actionId: string): void {
    switch (actionId) {
      case "refresh-reports":
        onRefresh();
        break;
      case "create-complaint":
        router.push("/complaints/new");
        break;
      case "view-complaints":
        router.push("/complaints");
        break;
      case "view-queue":
        router.push("/queue");
        break;
      case "assign-complaint":
        router.push("/assignments");
        break;
      case "escalate-complaint":
        router.push("/resolutions");
        break;
      case "manage-users":
        router.push("/users");
        break;
      default:
        break;
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardBody>
        <div id="quick-actions" />
        {actions.length === 0 ? (
          <Empty
            title="No actions"
            description="No actions available for your permissions."
          />
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {actions.map((action) => (
              <Button
                key={action.id}
                type="button"
                variant="outline"
                fullWidth
                onClick={() => handleAction(action.id)}
                title={action.description}
                className="h-auto !min-h-[44px] flex-col items-start gap-1 px-4 py-3 text-left whitespace-normal"
              >
                <span className="block text-[length:var(--ecmp-font-body-size)] font-semibold text-ecmp-text-primary">
                  {action.label}
                </span>
                <span className="block text-[length:var(--ecmp-font-caption-size)] font-normal text-ecmp-text-secondary">
                  {action.description}
                </span>
              </Button>
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
