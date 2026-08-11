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
import { searchKnowledge, fetchKnowledge } from "@/lib/api";
import type { Knowledge, KnowledgeType } from "@/lib/api/types";
import {
  FormField,
  Badge,
  controlSurfaceClass,
  formFieldDescribedBy,
} from "@/shared/ui";
import { IconChevronRight, IconFile, IconSpinner } from "@/shared/icons";
import { cn } from "@/shared/utils";
import { knowledgeTypeKey } from "@/features/knowledge/KnowledgeBadges";
import { detectMentionQuery, type MentionQuery } from "./knowledgeReferenceMarker";
import { isKnowledgeReferenceActive } from "./knowledgeReferenceActivity";
import {
  KNOWLEDGE_CHIP_ATTR_ID,
  getVisibleOffsetRect,
  getVisibleTextAndCaret,
  insertChipAtMention,
  knowledgeReferenceChipClass,
  renderMentionEditor,
  serializeMentionEditor,
} from "./knowledgeMentionEditor";

const DEBOUNCE_MS = 250;
/** Must stay aligned with backend KnowledgeService.REFERENCE_SEARCH_DEFAULT_LIMIT. */
const REFERENCE_SEARCH_LIMIT = 10;
const MENU_WIDTH_PX = 360;
const MENU_GAP_PX = 4;
const MENU_VIEWPORT_PAD_PX = 8;

/** Catalog order for the `@` empty-query type picker (Option A). */
export const KNOWLEDGE_MENTION_TYPES: readonly KnowledgeType[] = [
  "SOP",
  "PERATURAN",
  "SURAT_EDARAN",
  "KEPUTUSAN",
  "PANDUAN",
] as const;

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
  const selectedTypeRef = useRef<KnowledgeType | null>(null);
  /** After Escape, don't reopen from keyup until the user types again. */
  const suppressMentionUntilInputRef = useRef(false);

  const [mention, setMention] = useState<MentionQuery | null>(null);
  const [selectedType, setSelectedType] = useState<KnowledgeType | null>(null);
  const [results, setResults] = useState<Knowledge[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [highlighted, setHighlighted] = useState(0);
  const [menuPos, setMenuPos] = useState<{ top: number; left: number } | null>(
    null,
  );

  const open = mention !== null;
  mentionRef.current = mention;
  selectedTypeRef.current = selectedType;

  /** Empty `@` with no type chosen → show SOP / Peraturan / … first. */
  const showTypePicker =
    open && (mention?.query ?? "") === "" && selectedType === null;

  const describedBy = formFieldDescribedBy(inputId, { hint, error });

  const updateMenuPosition = useCallback(() => {
    const root = editorRef.current;
    const current = mentionRef.current;
    if (!root || !current) {
      setMenuPos(null);
      return;
    }
    const anchor = getVisibleOffsetRect(root, current.start);
    if (!anchor) {
      setMenuPos(null);
      return;
    }
    const viewportW = window.innerWidth;
    const viewportH = window.innerHeight;
    let left = anchor.left;
    left = Math.min(
      left,
      viewportW - MENU_WIDTH_PX - MENU_VIEWPORT_PAD_PX,
    );
    left = Math.max(MENU_VIEWPORT_PAD_PX, left);

    const preferredTop = anchor.bottom + MENU_GAP_PX;
    const estimatedMenuH = 280;
    const flipAbove =
      preferredTop + estimatedMenuH > viewportH - MENU_VIEWPORT_PAD_PX &&
      anchor.top > estimatedMenuH;
    const top = flipAbove
      ? Math.max(MENU_VIEWPORT_PAD_PX, anchor.top - estimatedMenuH - MENU_GAP_PX)
      : preferredTop;

    setMenuPos({ top, left });
  }, []);

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

  // Mark inline chips red when the referenced Knowledge is no longer active.
  useEffect(() => {
    const root = editorRef.current;
    if (!root || !value.includes("knowledge:")) return;
    let cancelled = false;
    const chips = Array.from(
      root.querySelectorAll<HTMLElement>(`[${KNOWLEDGE_CHIP_ATTR_ID}]`),
    );
    for (const chip of chips) {
      const id = chip.getAttribute(KNOWLEDGE_CHIP_ATTR_ID);
      if (!id) continue;
      fetchKnowledge(id)
        .then((res) => {
          if (cancelled) return;
          chip.className = knowledgeReferenceChipClass(
            isKnowledgeReferenceActive(res.data),
          );
        })
        .catch(() => {
          if (cancelled) return;
          chip.className = knowledgeReferenceChipClass(false);
        });
    }
    return () => {
      cancelled = true;
    };
  }, [value]);

  // Anchor "Cari Pengetahuan" beside the typed `@`.
  useLayoutEffect(() => {
    if (!open) {
      setMenuPos(null);
      return;
    }
    updateMenuPosition();
    const onReposition = () => updateMenuPosition();
    window.addEventListener("resize", onReposition);
    window.addEventListener("scroll", onReposition, true);
    return () => {
      window.removeEventListener("resize", onReposition);
      window.removeEventListener("scroll", onReposition, true);
    };
  }, [
    open,
    mention?.start,
    mention?.query,
    results.length,
    loading,
    showTypePicker,
    selectedType,
    updateMenuPosition,
  ]);

  const runSearch = useCallback(
    (query: string, type: KnowledgeType | null) => {
      const seq = ++requestSeqRef.current;
      setLoading(true);
      setSearchError(null);
      searchKnowledge({
        q: query,
        type: type ?? undefined,
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

  function scheduleSearch(query: string, type: KnowledgeType | null) {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => runSearch(query, type), DEBOUNCE_MS);
  }

  function enterTypePicker() {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    requestSeqRef.current += 1;
    setSelectedType(null);
    setResults([]);
    setSearchError(null);
    setLoading(false);
    setHighlighted(0);
  }

  function closeDropdown() {
    setMention(null);
    setSelectedType(null);
    setResults([]);
    setSearchError(null);
    setLoading(false);
    if (debounceRef.current) clearTimeout(debounceRef.current);
  }

  function syncMentionUi(nextMention: MentionQuery | null) {
    setMention(nextMention);
    if (!nextMention) {
      enterTypePicker();
      return;
    }
    const query = nextMention.query;
    const type = selectedTypeRef.current;
    if (query === "" && type === null) {
      enterTypePicker();
      return;
    }
    scheduleSearch(query, type);
  }

  function emitFromEditor() {
    const root = editorRef.current;
    if (!root) return;
    const next = serializeMentionEditor(root);
    if (maxLength != null && next.length > maxLength) {
      renderMentionEditor(root, value);
      return;
    }
    skipRenderFromValueRef.current = true;
    suppressMentionUntilInputRef.current = false;
    onChange(next);

    const { text, caret } = getVisibleTextAndCaret(root);
    syncMentionUi(detectMentionQuery(text, caret));
  }

  function selectType(type: KnowledgeType) {
    setSelectedType(type);
    setHighlighted(0);
    runSearch(mentionRef.current?.query ?? "", type);
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

    if (showTypePicker) {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setHighlighted((i) => (i + 1) % KNOWLEDGE_MENTION_TYPES.length);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setHighlighted(
          (i) =>
            (i - 1 + KNOWLEDGE_MENTION_TYPES.length) %
            KNOWLEDGE_MENTION_TYPES.length,
        );
      } else if (event.key === "Enter" || event.key === "Tab") {
        event.preventDefault();
        const type = KNOWLEDGE_MENTION_TYPES[highlighted];
        if (type) selectType(type);
      } else if (event.key === "Escape") {
        event.preventDefault();
        suppressMentionUntilInputRef.current = true;
        closeDropdown();
      }
      return;
    }

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
      if (selectedType && (mention?.query ?? "") === "") {
        enterTypePicker();
      } else {
        suppressMentionUntilInputRef.current = true;
        closeDropdown();
      }
    } else if (event.key === "Backspace" && selectedType && (mention?.query ?? "") === "") {
      // Empty query after a type was chosen — Backspace returns to type list.
      // (Does not delete the `@`; browser still handles that on a later press.)
      event.preventDefault();
      enterTypePicker();
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

  const activeOptionId = !open
    ? undefined
    : showTypePicker
      ? `${listboxId}-type-${highlighted}`
      : results[highlighted]
        ? `${listboxId}-option-${highlighted}`
        : undefined;

  useEffect(() => {
    if (!open) return;
    const id = showTypePicker
      ? `${listboxId}-type-${highlighted}`
      : `${listboxId}-option-${highlighted}`;
    const el = document.getElementById(id);
    if (el && typeof el.scrollIntoView === "function") {
      el.scrollIntoView({ block: "nearest" });
    }
  }, [highlighted, listboxId, open, results.length, showTypePicker]);

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

  const headerLabel = selectedType
    ? tKnowledge(knowledgeTypeKey(selectedType))
    : showTypePicker
      ? t("chooseType")
      : t("searchTitle");

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
            if (!open && !suppressMentionUntilInputRef.current) {
              const root = editorRef.current;
              if (!root) return;
              const { text, caret } = getVisibleTextAndCaret(root);
              const nextMention = detectMentionQuery(text, caret);
              if (nextMention) {
                syncMentionUi(nextMention);
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
      {open && menuPos ? (
        <div
          className="fixed z-50 w-[min(100vw-1rem,22.5rem)] rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface shadow-ecmp-raised"
          style={{ top: menuPos.top, left: menuPos.left }}
        >
          <div className="flex items-center gap-1.5 border-b border-ecmp-border px-3 py-2 text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-text-secondary">
            <span
              className="inline-flex size-5 shrink-0 items-center justify-center rounded bg-ecmp-primary-muted text-[length:var(--ecmp-font-body-small-size)] font-semibold text-ecmp-primary"
              aria-hidden
            >
              @
            </span>
            {selectedType ? (
              <button
                type="button"
                className="min-w-0 truncate text-left hover:text-ecmp-primary hover:underline"
                onMouseDown={(event) => {
                  event.preventDefault();
                  enterTypePicker();
                }}
              >
                {headerLabel}
              </button>
            ) : (
              <span className="min-w-0 truncate">{headerLabel}</span>
            )}
          </div>
          {showTypePicker ? (
            <p className="border-b border-ecmp-border px-3 py-1.5 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {t("typePickerHint")}
            </p>
          ) : null}
          <ul
            id={listboxId}
            role="listbox"
            aria-label={headerLabel}
            className="max-h-64 overflow-y-auto py-1"
          >
            {showTypePicker ? (
              KNOWLEDGE_MENTION_TYPES.map((type, index) => (
                <li key={type} role="none">
                  <div
                    id={`${listboxId}-type-${index}`}
                    role="option"
                    aria-selected={index === highlighted}
                    className={cn(
                      "flex cursor-pointer items-center gap-2 px-3 py-2 text-[length:var(--ecmp-font-body-small-size)]",
                      index === highlighted
                        ? "bg-ecmp-primary-muted"
                        : "hover:bg-ecmp-hover",
                    )}
                    onMouseDown={(event) => {
                      event.preventDefault();
                      selectType(type);
                    }}
                    onMouseEnter={() => setHighlighted(index)}
                  >
                    <Badge tone="info" className="shrink-0 px-1.5 py-0">
                      {tKnowledge(knowledgeTypeKey(type))}
                    </Badge>
                    <span className="min-w-0 flex-1 truncate text-ecmp-text-secondary">
                      {t("browseType", {
                        type: tKnowledge(knowledgeTypeKey(type)),
                      })}
                    </span>
                    <IconChevronRight
                      className="size-4 shrink-0 text-ecmp-text-secondary"
                      aria-hidden
                    />
                  </div>
                </li>
              ))
            ) : loading ? (
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
                    <div className="flex min-w-0 items-center gap-2">
                      <Badge tone="info" className="shrink-0 px-1.5 py-0">
                        {tKnowledge(knowledgeTypeKey(item.knowledgeType))}
                      </Badge>
                      <p className="truncate font-medium text-ecmp-text-primary">
                        {item.versionLabel
                          ? `${item.title} v${item.versionLabel}`
                          : item.title}
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
