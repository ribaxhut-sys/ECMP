"use client";

import {
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
  type MouseEvent as ReactMouseEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { searchKnowledge } from "@/lib/api";
import type { Knowledge } from "@/lib/api/types";
import {
  FormField,
  controlSurfaceClass,
  formFieldDescribedBy,
} from "@/shared/ui";
import { IconFile, IconSpinner } from "@/shared/icons";
import { cn } from "@/shared/utils";
import { detectMentionQuery, type MentionQuery } from "./knowledgeReferenceMarker";
import {
  getVisibleTextAndCaret,
  insertChipAtMention,
  renderMentionEditor,
  serializeMentionEditor,
} from "./knowledgeMentionEditor";

const DEBOUNCE_MS = 250;
/** Must stay aligned with backend KnowledgeService.REFERENCE_SEARCH_DEFAULT_LIMIT. */
const REFERENCE_SEARCH_LIMIT = 10;

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
  const router = useRouter();
  const t = useTranslations("knowledgeMention");
  const tKnowledge = useTranslations("knowledge");
  const listboxId = useId();
  const inputId = id ?? name ?? "knowledge-mention";

  const editorRef = useRef<HTMLDivElement | null>(null);
  const skipRenderFromValueRef = useRef(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const requestSeqRef = useRef(0);
  const mentionRef = useRef<MentionQuery | null>(null);
  /** After Escape, don't reopen from keyup until the user types again. */
  const suppressMentionUntilInputRef = useRef(false);

  const [mention, setMention] = useState<MentionQuery | null>(null);
  const [results, setResults] = useState<Knowledge[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [highlighted, setHighlighted] = useState(0);

  const open = mention !== null;
  mentionRef.current = mention;

  const describedBy = formFieldDescribedBy(inputId, { hint, error });

  // Keep contenteditable chips in sync with the controlled storage value.
  useLayoutEffect(() => {
    const root = editorRef.current;
    if (!root) return;
    if (skipRenderFromValueRef.current) {
      skipRenderFromValueRef.current = false;
      return;
    }
    if (serializeMentionEditor(root) === value) return;
    renderMentionEditor(root, value);
  }, [value]);

  const runSearch = useCallback(
    (query: string) => {
      const seq = ++requestSeqRef.current;
      setLoading(true);
      setSearchError(null);
      searchKnowledge({
        q: query,
        status: "ACTIVE",
        referenceOnly: true,
        limit: REFERENCE_SEARCH_LIMIT,
      })
        .then((res) => {
          if (seq !== requestSeqRef.current) return;
          setResults(res.data.slice(0, REFERENCE_SEARCH_LIMIT));
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

  function emitFromEditor() {
    const root = editorRef.current;
    if (!root) return;
    const next = serializeMentionEditor(root);
    if (maxLength != null && next.length > maxLength) {
      // Soft guard: re-render last accepted value.
      renderMentionEditor(root, value);
      return;
    }
    skipRenderFromValueRef.current = true;
    suppressMentionUntilInputRef.current = false;
    onChange(next);

    const { text, caret } = getVisibleTextAndCaret(root);
    const nextMention = detectMentionQuery(text, caret);
    setMention(nextMention);
    if (nextMention) {
      scheduleSearch(nextMention.query);
    } else {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      setResults([]);
    }
  }

  function selectResult(item: Knowledge) {
    const root = editorRef.current;
    const current = mentionRef.current;
    if (!root || !current) return;

    const { caret } = getVisibleTextAndCaret(root);
    const displayTitle = item.versionLabel
      ? `${item.title} v${item.versionLabel}`
      : item.title;

    insertChipAtMention(root, current.start, caret, displayTitle, item.id);
    closeDropdown();
    emitFromEditor();
    root.focus();
  }

  function onEditorKeyDown(event: ReactKeyboardEvent<HTMLDivElement>) {
    if (!open) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setHighlighted((i) => (results.length === 0 ? 0 : (i + 1) % results.length));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setHighlighted((i) =>
        results.length === 0 ? 0 : (i - 1 + results.length) % results.length,
      );
    } else if (event.key === "Enter" || event.key === "Tab") {
      if (results[highlighted]) {
        event.preventDefault();
        selectResult(results[highlighted]);
      }
    } else if (event.key === "Escape") {
      event.preventDefault();
      suppressMentionUntilInputRef.current = true;
      closeDropdown();
    }
  }

  function onEditorClick(event: ReactMouseEvent<HTMLDivElement>) {
    const target = event.target;
    if (!(target instanceof Element)) return;
    const chip = target.closest(`[data-knowledge-id]`);
    if (!chip || !editorRef.current?.contains(chip)) return;
    const knowledgeId = chip.getAttribute("data-knowledge-id");
    if (!knowledgeId) return;
    event.preventDefault();
    router.push(`/knowledge/${knowledgeId}`);
  }

  const activeOptionId =
    open && results[highlighted] ? `${listboxId}-option-${highlighted}` : undefined;

  useEffect(() => {
    if (!open || results.length === 0) return;
    const el = document.getElementById(`${listboxId}-option-${highlighted}`);
    if (el && typeof el.scrollIntoView === "function") {
      el.scrollIntoView({ block: "nearest" });
    }
  }, [highlighted, listboxId, open, results.length]);

  // Prevent contenteditable from inserting raw HTML on paste.
  useEffect(() => {
    const root = editorRef.current;
    if (!root) return;
    const onPaste = (event: ClipboardEvent) => {
      event.preventDefault();
      const text = event.clipboardData?.getData("text/plain") ?? "";
      root.ownerDocument.execCommand("insertText", false, text);
    };
    root.addEventListener("paste", onPaste);
    return () => root.removeEventListener("paste", onPaste);
  }, []);

  return (
    <div className="relative">
      <FormField
        id={inputId}
        label={label}
        hint={hint}
        error={error}
        required={required}
        disabled={disabled}
      >
        {name ? <input type="hidden" name={name} value={value} /> : null}
        <div
          ref={editorRef}
          id={inputId}
          role="combobox"
          aria-expanded={open}
          aria-controls={open ? listboxId : undefined}
          aria-activedescendant={activeOptionId}
          aria-autocomplete="list"
          aria-required={required || undefined}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          aria-disabled={disabled || undefined}
          contentEditable={disabled ? false : true}
          suppressContentEditableWarning
          className={cn(
            "min-h-[88px] whitespace-pre-wrap break-words rounded-[var(--ecmp-radius-textarea)] px-3 py-3 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary outline-none",
            controlSurfaceClass(error),
            disabled && "cursor-not-allowed opacity-70",
          )}
          style={{ minHeight: `${Math.max(rows, 3) * 1.5}rem` }}
          onInput={() => emitFromEditor()}
          onKeyUp={() => {
            // Caret moves without input (arrows) — refresh @ detection.
            if (!open && !suppressMentionUntilInputRef.current) {
              const root = editorRef.current;
              if (!root) return;
              const { text, caret } = getVisibleTextAndCaret(root);
              const nextMention = detectMentionQuery(text, caret);
              if (nextMention) {
                setMention(nextMention);
                scheduleSearch(nextMention.query);
              }
            }
          }}
          onKeyDown={onEditorKeyDown}
          onClick={onEditorClick}
          onBlur={() => {
            window.setTimeout(() => {
              const active = document.activeElement;
              if (
                active &&
                editorRef.current &&
                (editorRef.current === active ||
                  editorRef.current.contains(active))
              ) {
                return;
              }
              closeDropdown();
            }, 150);
          }}
        />
      </FormField>
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
