"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { cn } from "@/shared/utils";
import {
  FormField,
  controlSurfaceClass,
  formFieldDescribedBy,
} from "@/shared/ui/form-field";

const WEEKDAY_LABELS = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"];
const MONTH_LABELS = [
  "Januari", "Februari", "Maret", "April", "Mei", "Juni",
  "Juli", "Agustus", "September", "Oktober", "November", "Desember",
];

function parseISO(iso: string | undefined): Date | null {
  if (!iso) return null;
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return null;
  return new Date(y, m - 1, d);
}

function toISO(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

/** "2026-09-16" -> "16/09/2026" — app-controlled, not the browser's locale. */
export function formatDateDDMMYYYY(iso: string): string {
  const date = parseISO(iso);
  if (!date) return "";
  return `${String(date.getDate()).padStart(2, "0")}/${String(date.getMonth() + 1).padStart(2, "0")}/${date.getFullYear()}`;
}

function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function addMonths(date: Date, months: number): Date {
  return new Date(date.getFullYear(), date.getMonth() + months, 1);
}

function isSameDate(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

/** Monday-start 6-week grid covering the given month. */
function buildCalendarGrid(monthStart: Date): Date[] {
  const isoWeekday = monthStart.getDay() === 0 ? 7 : monthStart.getDay();
  const gridStart = new Date(monthStart);
  gridStart.setDate(gridStart.getDate() - (isoWeekday - 1));
  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(gridStart);
    d.setDate(gridStart.getDate() + i);
    return d;
  });
}

function CalendarGlyph({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 20 20" fill="none" className={className} aria-hidden="true">
      <rect x="3" y="4" width="14" height="13" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M3 8h14M7 2.5v3M13 2.5v3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function ChevronGlyph({ direction, className }: { direction: "left" | "right"; className?: string }) {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="none"
      className={cn(className, direction === "left" && "rotate-180")}
      aria-hidden="true"
    >
      <path d="M7.5 4.5 13 10l-5.5 5.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export interface DatePickerProps {
  id?: string;
  name?: string;
  label?: string;
  description?: string;
  helper?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  loading?: boolean;
  /** ISO `yyyy-mm-dd`, or "" for no selection. */
  value: string;
  /** Receives ISO `yyyy-mm-dd`. */
  onChange: (value: string) => void;
  /** ISO `yyyy-mm-dd` bounds (inclusive). */
  min?: string;
  max?: string;
  /** Days of week to disable (0=Sunday..6=Saturday, matches `Date#getDay`). */
  disabledWeekdays?: readonly number[];
  /** Specific ISO `yyyy-mm-dd` dates to disable (e.g. holidays). */
  disabledDates?: readonly string[];
  placeholder?: string;
}

const POPOVER_ESTIMATED_HEIGHT = 320;

/**
 * App-controlled date picker — always renders dd/mm/yyyy, regardless of the
 * browser/OS locale (native `<input type="date">` cannot guarantee that).
 * Value in/out is ISO `yyyy-mm-dd`, matching the rest of the API surface.
 */
export function DatePicker({
  id,
  name,
  label,
  description,
  helper,
  error,
  required,
  disabled,
  loading,
  value,
  onChange,
  min,
  max,
  disabledWeekdays,
  disabledDates,
  placeholder = "dd/mm/yyyy",
}: DatePickerProps) {
  const inputId = id ?? name ?? "date-picker";
  const describedBy = formFieldDescribedBy(inputId, { description, helper, error });
  const [open, setOpen] = useState(false);
  const [placement, setPlacement] = useState<"down" | "up">("down");
  const selected = parseISO(value);
  const minDate = parseISO(min);
  const maxDate = parseISO(max);
  // Anchor the initially-open month on the selection, else the min bound,
  // else today — opening on "today" when today is outside [min, max] would
  // show an all-disabled month, which isn't a useful default.
  const defaultAnchor = () => selected ?? minDate ?? new Date();
  const [viewMonth, setViewMonth] = useState<Date>(() => startOfMonth(defaultAnchor()));
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setViewMonth(startOfMonth(defaultAnchor()));
    // Re-sync the visible month whenever the selected value changes externally.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const disabledDateSet = useMemo(
    () => new Set(disabledDates ?? []),
    [disabledDates],
  );

  function isDisabledDate(date: Date): boolean {
    if (minDate && date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    if (disabledWeekdays?.includes(date.getDay())) return true;
    if (disabledDateSet.has(toISO(date))) return true;
    return false;
  }

  function toggleOpen() {
    setOpen((wasOpen) => {
      const nextOpen = !wasOpen;
      if (nextOpen && containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        const spaceBelow = window.innerHeight - rect.bottom;
        const spaceAbove = rect.top;
        setPlacement(
          spaceBelow < POPOVER_ESTIMATED_HEIGHT && spaceAbove > spaceBelow ? "up" : "down",
        );
      }
      return nextOpen;
    });
  }

  const grid = useMemo(() => buildCalendarGrid(viewMonth), [viewMonth]);
  const today = new Date();

  return (
    <FormField
      id={inputId}
      label={label}
      description={description}
      helper={helper}
      error={error}
      required={required}
      disabled={disabled}
      loading={loading}
    >
      <div ref={containerRef} className="relative">
        <button
          type="button"
          id={inputId}
          name={name}
          disabled={disabled || loading}
          aria-haspopup="dialog"
          aria-expanded={open}
          aria-describedby={describedBy}
          onClick={toggleOpen}
          className={cn(
            "ecmp-touch flex w-full items-center justify-between gap-2 rounded-[var(--ecmp-radius-input)] px-3 text-left",
            controlSurfaceClass(error),
            !value && "text-ecmp-muted",
          )}
        >
          <span>{value ? formatDateDDMMYYYY(value) : placeholder}</span>
          <CalendarGlyph className="h-4 w-4 shrink-0 text-ecmp-text-secondary" />
        </button>

        {open ? (
          <div
            role="dialog"
            aria-label={label}
            className={cn(
              "absolute left-0 z-[var(--ecmp-z-dropdown)] w-72 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface p-3 shadow-ecmp-md",
              placement === "up" ? "bottom-full mb-2" : "top-full mt-2",
            )}
          >
            <div className="mb-2 flex items-center justify-between">
              <button
                type="button"
                aria-label="Bulan sebelumnya"
                onClick={() => setViewMonth((m) => addMonths(m, -1))}
                className="rounded-[var(--ecmp-radius-sm)] p-1 text-ecmp-text-secondary hover:bg-ecmp-hover"
              >
                <ChevronGlyph direction="left" className="h-4 w-4" />
              </button>
              <span className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                {MONTH_LABELS[viewMonth.getMonth()]} {viewMonth.getFullYear()}
              </span>
              <button
                type="button"
                aria-label="Bulan berikutnya"
                onClick={() => setViewMonth((m) => addMonths(m, 1))}
                className="rounded-[var(--ecmp-radius-sm)] p-1 text-ecmp-text-secondary hover:bg-ecmp-hover"
              >
                <ChevronGlyph direction="right" className="h-4 w-4" />
              </button>
            </div>

            <div className="grid grid-cols-7 gap-1 text-center text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {WEEKDAY_LABELS.map((w) => (
                <span key={w}>{w}</span>
              ))}
            </div>

            <div className="mt-1 grid grid-cols-7 gap-1">
              {grid.map((date) => {
                const inMonth = date.getMonth() === viewMonth.getMonth();
                const iso = toISO(date);
                const isSelected = selected != null && isSameDate(date, selected);
                const isToday = isSameDate(date, today);
                const disabledCell = isDisabledDate(date);
                return (
                  <button
                    key={iso}
                    type="button"
                    disabled={disabledCell}
                    onClick={() => {
                      onChange(iso);
                      setOpen(false);
                    }}
                    aria-label={formatDateDDMMYYYY(iso)}
                    aria-current={isToday ? "date" : undefined}
                    className={cn(
                      "ecmp-touch rounded-[var(--ecmp-radius-sm)] text-[length:var(--ecmp-font-caption-size)]",
                      !inMonth && "text-ecmp-muted",
                      inMonth && !isSelected && "text-ecmp-text-primary",
                      isToday && !isSelected && "border border-ecmp-primary",
                      isSelected && "bg-ecmp-primary text-ecmp-primary-foreground",
                      disabledCell && "cursor-not-allowed opacity-40 hover:bg-transparent",
                      !disabledCell && !isSelected && "hover:bg-ecmp-hover",
                    )}
                  >
                    {date.getDate()}
                  </button>
                );
              })}
            </div>
          </div>
        ) : null}
      </div>
    </FormField>
  );
}
