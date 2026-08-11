"use client";

import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type ChangeEvent,
  type KeyboardEvent,
} from "react";
import { useTranslations } from "next-intl";
import { searchKnowledge } from "@/lib/api";
import type { Knowledge } from "@/lib/api/types";
import { Textarea } from "@/shared/ui";
import { IconFile, IconSpinner } from "@/shared/icons";
import { cn } from "@/shared/utils";
import {
  detectMentionQuery,
  insertKnowledgeMarker,
  type MentionQuery,
} from "./knowledgeReferenceMarker";

const DEBOUNCE_MS = 250;

function resultSubtitle(item: Knowledge, statusLabel: string): string {
  const typeOrDocNumber = item.documentNumber || item.knowledgeType;
  const version = item.versionLabel ? `v${item.versionLabel}` : null;
  return [typeOrDocNumber, version, statusLabel].filter(Boolean).join(" · ");
}

export function KnowledgeMentionTextarea({
  id,
  label,
  name,
  required,
  rows = 4,
  value,
  onChange,
  error,
  hint,
  maxLength,
  disabled,
}: {
  id?: string;
  label: string;
  name?: string;
  required?: boolean;
  rows?: number;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  hint?: string;
  maxLength?: number;
  disabled?: boolean;
}) {
  const t = useTranslations("knowledgeMention");
  const tKnowledge = useTranslations("knowledge");
  const listboxId = useId();

  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const pendingCaretRef = useRef<number | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const requestSeqRef = useRef(0);

  const [mention, setMention] = useState<MentionQuery | null>(null);
  const [results, setResults] = useState<Knowledge[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [highlighted, setHighlighted] = useState(0);

  const open = mention !== null;

  useEffect(() => {
    if (pendingCaretRef.current === null) return;
    const caret = pendingCaretRef.current;
    pendingCaretRef.current = null;
    const el = textareaRef.current;
    if (!el) return;
    el.focus();
    el.setSelectionRange(caret, caret);
  }, [value]);

  const runSearch = useCallback(
    (query: string) => {
      const seq = ++requestSeqRef.current;
      setLoading(true);
      setSearchError(null);
      searchKnowledge({ q: query, status: "ACTIVE", referenceOnly: true })
        .then((res) => {
          if (seq !== requestSeqRef.current) return;
          setResults(res.data);
          setHighlighted(0);
        })
        .catch(() => {
          if (seq !== requestSeqRef.current) return;
          setResults([]);
          setSearchError(t("error"));
        })
        .finally(() => {
          if (seq !== requestSeqRef.current) return;
          setLoading(false);
        });
    },
    [t],
  );

  function scheduleSearch(query: string) {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => runSearch(query), DEBOUNCE_MS);
  }

  function closeDropdown() {
    setMention(null);
    setResults([]);
    setSearchError(null);
    if (debounceRef.current) clearTimeout(debounceRef.current);
  }

  function onTextareaChange(event: ChangeEvent<HTMLTextAreaElement>) {
    const nextValue = event.target.value;
    const caret = event.target.selectionStart ?? nextValue.length;
    onChange(nextValue);

    const next = detectMentionQuery(nextValue, caret);
    setMention(next);
    if (next) {
      scheduleSearch(next.query);
    } else {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      setResults([]);
    }
  }

  function selectResult(item: Knowledge) {
    if (!mention) return;
    const el = textareaRef.current;
    const caret = el?.selectionStart ?? value.length;
    const displayTitle = item.versionLabel
      ? `${item.title} v${item.versionLabel}`
      : item.title;
    const { text: nextText, caret: nextCaret } = insertKnowledgeMarker(
      value,
      mention,
      caret,
      displayTitle,
      item.id,
    );
    pendingCaretRef.current = nextCaret;
    onChange(nextText);
    closeDropdown();
  }

  function onTextareaKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (!open) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setHighlighted((i) => (results.length === 0 ? 0 : (i + 1) % results.length));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setHighlighted((i) =>
        results.length === 0 ? 0 : (i - 1 + results.length) % results.length,
      );
    } else if (event.key === "Enter") {
      if (results[highlighted]) {
        event.preventDefault();
        selectResult(results[highlighted]);
      }
    } else if (event.key === "Escape") {
      event.preventDefault();
      closeDropdown();
    }
  }

  const activeOptionId =
    open && results[highlighted] ? `${listboxId}-option-${highlighted}` : undefined;

  return (
    <div className="relative">
      <Textarea
        ref={textareaRef}
        id={id}
        label={label}
        name={name}
        required={required}
        rows={rows}
        value={value}
        error={error}
        hint={hint}
        maxLength={maxLength}
        disabled={disabled}
        onChange={onTextareaChange}
        onKeyDown={onTextareaKeyDown}
        onBlur={() => {
          // Defer so a click on a dropdown option still registers.
          window.setTimeout(() => closeDropdown(), 150);
        }}
        role="combobox"
        aria-expanded={open}
        aria-controls={open ? listboxId : undefined}
        aria-activedescendant={activeOptionId}
        aria-autocomplete="list"
      />
      {open ? (
        <div className="absolute z-10 mt-1 w-full max-w-md rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface shadow-ecmp-raised">
          <p className="border-b border-ecmp-border px-3 py-2 text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-text-secondary">
            {t("searchTitle")}
          </p>
          <ul
            id={listboxId}
            role="listbox"
            aria-label={t("searchTitle")}
            className="max-h-64 overflow-y-auto py-1"
          >
            {loading ? (
              <li className="flex items-center gap-2 px-3 py-3 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                <IconSpinner className="size-4" aria-hidden />
                {t("loading")}
              </li>
            ) : searchError ? (
              <li className="px-3 py-3 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-danger">
                {searchError}
              </li>
            ) : results.length === 0 ? (
              <li className="px-3 py-3 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {t("empty")}
              </li>
            ) : (
              results.map((item, index) => (
                <li key={item.id} role="none">
                  <div
                    id={`${listboxId}-option-${index}`}
                    role="option"
                    aria-selected={index === highlighted}
                    className={cn(
                      "flex cursor-pointer items-start gap-2 px-3 py-2 text-[length:var(--ecmp-font-body-small-size)]",
                      index === highlighted
                        ? "bg-ecmp-primary-muted"
                        : "hover:bg-ecmp-hover",
                    )}
                    onMouseDown={(event) => {
                      // mousedown (not click) fires before the textarea blur.
                      event.preventDefault();
                      selectResult(item);
                    }}
                    onMouseEnter={() => setHighlighted(index)}
                  >
                    <IconFile
                      className="mt-0.5 size-4 shrink-0 text-ecmp-text-secondary"
                      aria-hidden
                    />
                    <div className="min-w-0">
                      <p className="truncate font-medium text-ecmp-text-primary">
                        {item.title}
                      </p>
                      <p className="truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                        {resultSubtitle(item, tKnowledge("statusActive"))}
                      </p>
                    </div>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
