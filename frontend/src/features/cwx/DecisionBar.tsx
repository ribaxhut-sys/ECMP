"use client";

import { useId, useState } from "react";
import { Button } from "@/shared/ui";

export type CwxDecisionAction = {
  id: string;
  label: string;
  onClick: () => void;
  /** When true, rendered as primary emphasis (still subject to max-3 primary slot). */
  emphasize?: boolean;
  busy?: boolean;
};

export type CwxDecisionBarProps = {
  /** Already filtered: Role ∧ Permission ∧ State ∧ BR. */
  actions: readonly CwxDecisionAction[];
  overflowLabel: string;
  emptyLabel: string;
};

const PRIMARY_MAX = 3;

/**
 * CWX-M1 Decision Bar — only pre-validated actions; max 3 primary + overflow.
 */
export function CwxDecisionBar({
  actions,
  overflowLabel,
  emptyLabel,
}: CwxDecisionBarProps) {
  const listId = useId();
  const [open, setOpen] = useState(false);
  const primary = actions.slice(0, PRIMARY_MAX);
  const overflow = actions.slice(PRIMARY_MAX);

  return (
    <div
      data-testid="cwx-decision-bar"
      className="sticky bottom-0 z-20 border-t border-ecmp-border/60 bg-ecmp-background/95 px-1 py-2.5 backdrop-blur-sm"
    >
      {actions.length === 0 ? (
        <p className="text-[12px] text-ecmp-text-secondary">{emptyLabel}</p>
      ) : (
        <div className="relative flex flex-wrap items-center gap-2">
          {primary.map((action, index) => (
            <Button
              key={action.id}
              type="button"
              size="sm"
              variant={
                action.emphasize || index === 0 ? "primary" : "outline"
              }
              disabled={action.busy}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          ))}

          {overflow.length > 0 ? (
            <div className="relative">
              <Button
                type="button"
                size="sm"
                variant="ghost"
                aria-haspopup="menu"
                aria-expanded={open}
                aria-controls={listId}
                onClick={() => setOpen((prev) => !prev)}
              >
                {overflowLabel}
              </Button>
              {open ? (
                <ul
                  id={listId}
                  role="menu"
                  className="absolute bottom-full right-0 z-30 mb-1 min-w-[10rem] overflow-hidden rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface py-1 shadow-ecmp-md"
                >
                  {overflow.map((action) => (
                    <li key={action.id} role="none">
                      <button
                        type="button"
                        role="menuitem"
                        disabled={action.busy}
                        className="flex w-full px-3 py-2 text-left text-[13px] text-ecmp-text-primary hover:bg-ecmp-hover/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus disabled:opacity-50"
                        onClick={() => {
                          setOpen(false);
                          action.onClick();
                        }}
                      >
                        {action.label}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
