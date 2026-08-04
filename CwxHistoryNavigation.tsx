"use client";

import {
  useCallback,
  useId,
  useMemo,
  useRef,
  type KeyboardEvent,
} from "react";
import { cn } from "@/shared/utils";

export type CwxHistoryTabId = "activity" | "decisions" | "audit";

export type CwxHistoryNavigationProps = {
  /** Controlled selected tab — parent owns state. */
  value: CwxHistoryTabId;
  /** Parent callback only — no routing, URL, query, or persistence. */
  onChange: (tab: CwxHistoryTabId) => void;
  /** Presentation labels — parent supplies translated copy. */
  labels: {
    activity: string;
    decisions: string;
    audit: string;
  };
  /**
   * Audit tab visibility. Use `{ visible: false }` for Aggregate / not READY.
   * Default: visible.
   */
  audit?: {
    visible?: boolean;
  };
  /** Accessible name for the tablist. Parent may pass translated copy. */
  "aria-label"?: string;
  className?: string;
};

type TabDef = {
  id: CwxHistoryTabId;
  label: string;
};

/**
 * CWX-M4 History Navigation — presentation only.
 *
 * Controlled tabs for Activity · Decisions · Audit.
 * Never fetch, route, persist, or select SoT.
 */
export function CwxHistoryNavigation({
  value,
  onChange,
  labels,
  audit,
  "aria-label": ariaLabel,
  className,
}: CwxHistoryNavigationProps) {
  const baseId = useId();
  const auditVisible = audit?.visible !== false;
  const tabRefs = useRef<Partial<Record<CwxHistoryTabId, HTMLButtonElement | null>>>(
    {},
  );

  const tabs = useMemo((): TabDef[] => {
    const list: TabDef[] = [
      { id: "activity", label: labels.activity },
      { id: "decisions", label: labels.decisions },
    ];
    if (auditVisible) {
      list.push({ id: "audit", label: labels.audit });
    }
    return list;
  }, [auditVisible, labels.activity, labels.audit, labels.decisions]);

  const focusTab = useCallback((id: CwxHistoryTabId) => {
    tabRefs.current[id]?.focus();
  }, []);

  const selectTab = useCallback(
    (id: CwxHistoryTabId) => {
      onChange(id);
      focusTab(id);
    },
    [focusTab, onChange],
  );

  const onKeyDown = useCallback(
    (event: KeyboardEvent<HTMLButtonElement>, current: CwxHistoryTabId) => {
      const index = tabs.findIndex((tab) => tab.id === current);
      if (index < 0 || tabs.length === 0) return;

      let nextIndex: number | null = null;
      switch (event.key) {
        case "ArrowRight":
        case "ArrowDown":
          nextIndex = (index + 1) % tabs.length;
          break;
        case "ArrowLeft":
        case "ArrowUp":
          nextIndex = (index - 1 + tabs.length) % tabs.length;
          break;
        case "Home":
          nextIndex = 0;
          break;
        case "End":
          nextIndex = tabs.length - 1;
          break;
        default:
          return;
      }

      event.preventDefault();
      const next = tabs[nextIndex];
      if (next) selectTab(next.id);
    },
    [selectTab, tabs],
  );

  const effectiveValue =
    value === "audit" && !auditVisible
      ? (tabs[0]?.id ?? "activity")
      : tabs.some((tab) => tab.id === value)
        ? value
        : (tabs[0]?.id ?? "activity");

  return (
    <div
      data-testid="cwx-history-navigation"
      className={cn("border-b border-ecmp-border", className)}
    >
      <div
        role="tablist"
        aria-label={ariaLabel}
        aria-orientation="horizontal"
        className="flex flex-wrap gap-1"
      >
        {tabs.map((tab) => {
          const selected = effectiveValue === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`${baseId}-tab-${tab.id}`}
              data-testid={`cwx-history-tab-${tab.id}`}
              aria-selected={selected}
              tabIndex={selected ? 0 : -1}
              ref={(node) => {
                tabRefs.current[tab.id] = node;
              }}
              onClick={() => selectTab(tab.id)}
              onKeyDown={(event) => onKeyDown(event, tab.id)}
              className={cn(
                "relative min-h-[var(--ecmp-touch-min)] rounded-[var(--ecmp-radius-button)] px-3 py-2",
                "text-[length:var(--ecmp-font-body-small-size)] font-medium",
                "transition-[background-color,color] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]",
                "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]",
                selected
                  ? "bg-ecmp-primary-muted text-ecmp-primary"
                  : "text-ecmp-text-secondary hover:bg-ecmp-hover hover:text-ecmp-text-primary",
              )}
            >
              {tab.label}
              {selected ? (
                <span
                  className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-ecmp-primary"
                  aria-hidden
                />
              ) : null}
            </button>
          );
        })}
      </div>
    </div>
  );
}
