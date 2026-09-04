"use client";

import {
  useCallback,
  useEffect,
  useId,
  useImperativeHandle,
  useLayoutEffect,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
  type MouseEvent as ReactMouseEvent,
  type Ref,
} from "react";
import { useTranslations } from "next-intl";
import {
  fetchActiveAnnouncements,
  fetchAnnouncementAttachmentLibrary,
  fetchKnowledgeTypeCounts,
  searchKnowledge,
} from "@/lib/api";
import type { KnowledgeType, KnowledgeTypeCounts } from "@/lib/api/types";
import {
  FormField,
  Badge,
  controlSurfaceClass,
  formFieldDescribedBy,
} from "@/shared/ui";
import {
  IconBell,
  IconChevronRight,
  IconFile,
  IconPaperclip,
  IconSpinner,
} from "@/shared/icons";
import { cn } from "@/shared/utils";
import { knowledgeTypeKey } from "@/features/knowledge/KnowledgeBadges";
import { KnowledgePreviewModal } from "@/features/knowledge/KnowledgePreviewModal";
import {
  detectMentionQuery,
  type MentionKind,
  type MentionQuery,
} from "./knowledgeReferenceMarker";
import { resolveMentionReferenceMeta } from "./knowledgeReferenceActivity";
import {
  MENTION_CHIP_ATTR_ID,
  MENTION_CHIP_ATTR_KIND,
  deleteVisibleRange,
  getVisibleOffsetRect,
  getVisibleTextAndCaret,
  insertChipAtMention,
  knowledgeReferenceChipClass,
  renderMentionEditor,
  serializeMentionEditor,
  setMentionChipTypeLabel,
} from "./knowledgeMentionEditor";

const DEBOUNCE_MS = 250;
/** Must stay aligned with backend KnowledgeService.REFERENCE_SEARCH_DEFAULT_LIMIT
 * for the knowledge source; reused client-side as a display cap for the
 * announcement/attachment sources, which have no server-side limit param. */
const REFERENCE_SEARCH_LIMIT = 10;
const MENU_WIDTH_PX = 360;
const MENU_GAP_PX = 4;
const MENU_VIEWPORT_PAD_PX = 8;

/** Catalog order for the `@` empty-query type picker (Knowledge sub-flow). */
export const KNOWLEDGE_MENTION_TYPES: readonly KnowledgeType[] = [
  "SOP",
  "PERATURAN",
  "SURAT_EDARAN",
  "KEPUTUSAN",
  "PANDUAN",
] as const;

/** Outermost `@` picker — which record kind to search. */
const MENTION_SOURCES: readonly MentionKind[] = [
  "knowledge",
  "announcement",
  "attachment",
] as const;

/** One normalized row for the results list, regardless of source. */
type MentionResult = {
  kind: MentionKind;
  id: string;
  /** Stored as the chip title / marker snapshot. */
  title: string;
  /** Badge shown in front of the title (Knowledge sub-type, or a fixed label). */
  typeLabel: string;
};

/** Imperative escape hatch for callers that change `value` from outside the
 * editor (quick-fill preset tags) and need the caret back in the text. */
export type KnowledgeMentionTextareaHandle = {
  /**
   * Focus the editor and put the caret after the last character.
   * `afterValueSync` defers the placement until the contenteditable DOM has
   * been rebuilt from the new `value` — pass it whenever the same click also
   * changed `value`, otherwise the caret lands in the pre-update DOM and is
   * wiped by the rebuild.
   */
  focusEnd: (options?: { afterValueSync?: boolean }) => void;
};

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
  ref,
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
  ref?: Ref<KnowledgeMentionTextareaHandle>;
}) {
  const t = useTranslations("knowledgeMention");
  const tKnowledge = useTranslations("knowledge");
  const listboxId = useId();
  const inputId = id ?? name ?? "knowledge-mention";

  const editorRef = useRef<HTMLDivElement | null>(null);
  const skipRenderFromValueRef = useRef(false);
  /** Set by `focusEnd({ afterValueSync: true })`, consumed by the value sync. */
  const focusEndPendingRef = useRef(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const requestSeqRef = useRef(0);
  const mentionRef = useRef<MentionQuery | null>(null);
  const sourceRef = useRef<MentionKind | null>(null);
  const selectedTypeRef = useRef<KnowledgeType | null>(null);
  /** After Escape, don't reopen from keyup until the user types again. */
  const suppressMentionUntilInputRef = useRef(false);

  const [mention, setMention] = useState<MentionQuery | null>(null);
  const [source, setSource] = useState<MentionKind | null>(null);
  const [selectedType, setSelectedType] = useState<KnowledgeType | null>(null);
  const [results, setResults] = useState<MentionResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [highlighted, setHighlighted] = useState(0);
  const [menuPos, setMenuPos] = useState<{ top: number; left: number } | null>(
    null,
  );
  const [previewKnowledgeId, setPreviewKnowledgeId] = useState<string | null>(null);
  const [typeCounts, setTypeCounts] = useState<KnowledgeTypeCounts | null>(null);
  const [sourceCounts, setSourceCounts] = useState<Partial<
    Record<MentionKind, number>
  > | null>(null);

  const open = mention !== null;
  mentionRef.current = mention;
  sourceRef.current = source;
  selectedTypeRef.current = selectedType;

  /** Outermost level: which source to search. Free-text typed before a
   * source is chosen does not fall through to a search — there is no
   * single meaningful query across three disjoint domains, unlike the
   * Knowledge type sub-picker below. */
  const showSourcePicker = open && source === null;
  /** Empty `@` with Pengetahuan chosen but no type yet → show SOP / Peraturan / … */
  const showTypePicker =
    open &&
    source === "knowledge" &&
    selectedType === null &&
    (mention?.query ?? "") === "";

  const describedBy = formFieldDescribedBy(inputId, { hint, error });

  const sourceLabel = useCallback(
    (kind: MentionKind): string => {
      if (kind === "knowledge") return t("sourceKnowledge");
      if (kind === "announcement") return t("sourceAnnouncement");
      return t("sourceAttachment");
    },
    [t],
  );

  const placeCaretAtEnd = useCallback(() => {
    const root = editorRef.current;
    if (!root) return;
    root.focus();
    const range = document.createRange();
    range.selectNodeContents(root);
    range.collapse(false);
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
  }, []);

  useImperativeHandle(
    ref,
    () => ({
      focusEnd(options) {
        if (options?.afterValueSync) focusEndPendingRef.current = true;
        placeCaretAtEnd();
      },
    }),
    [placeCaretAtEnd],
  );

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
      // The change came from the editor itself; the caret is already where the
      // user put it, so drop any pending external focus request.
      focusEndPendingRef.current = false;
      return;
    }
    if (serializeMentionEditor(root) !== value) renderMentionEditor(root, value);
    if (focusEndPendingRef.current) {
      focusEndPendingRef.current = false;
      placeCaretAtEnd();
    }
  }, [value, placeCaretAtEnd]);

  // Mark inline chips red when the referenced record is no longer active
  // (deleted / archived / expired / access revoked) — any of the 3 kinds.
  useEffect(() => {
    const root = editorRef.current;
    if (!root) return;
    if (!MENTION_SOURCES.some((kind) => value.includes(`${kind}:`))) return;
    let cancelled = false;
    const chips = Array.from(
      root.querySelectorAll<HTMLElement>(`[${MENTION_CHIP_ATTR_ID}]`),
    );
    for (const chip of chips) {
      const kind = chip.getAttribute(MENTION_CHIP_ATTR_KIND) as MentionKind | null;
      const chipId = chip.getAttribute(MENTION_CHIP_ATTR_ID);
      if (!kind || !chipId) continue;
      resolveMentionReferenceMeta(kind, chipId, {
        knowledgeType: (knowledgeType) => tKnowledge(knowledgeTypeKey(knowledgeType)),
        announcement: t("sourceAnnouncement"),
        attachment: t("sourceAttachment"),
      })
        .then(({ active, typeLabel }) => {
          if (cancelled) return;
          chip.className = knowledgeReferenceChipClass(active);
          setMentionChipTypeLabel(chip, typeLabel);
        })
        .catch(() => {
          if (cancelled) return;
          chip.className = knowledgeReferenceChipClass(false);
        });
    }
    return () => {
      cancelled = true;
    };
  }, [value, t, tKnowledge]);

  // Anchor the picker beside the typed `@`.
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
    showSourcePicker,
    showTypePicker,
    source,
    selectedType,
    updateMenuPosition,
  ]);

  const runSearch = useCallback(
    (activeSource: MentionKind, query: string, knowledgeType: KnowledgeType | null) => {
      const seq = ++requestSeqRef.current;
      setLoading(true);
      setSearchError(null);

      const rows: Promise<MentionResult[]> =
        activeSource === "knowledge"
          ? searchKnowledge({
              q: query,
              type: knowledgeType ?? undefined,
              status: "ACTIVE",
              referenceOnly: true,
              limit: REFERENCE_SEARCH_LIMIT,
            }).then((res) =>
              res.data.slice(0, REFERENCE_SEARCH_LIMIT).map((item) => ({
                kind: "knowledge" as const,
                id: item.id,
                title: item.versionLabel
                  ? `${item.title} v${item.versionLabel}`
                  : item.title,
                typeLabel: tKnowledge(knowledgeTypeKey(item.knowledgeType)),
              })),
            )
          : activeSource === "announcement"
            ? fetchActiveAnnouncements().then((res) => {
                const q = query.trim().toLowerCase();
                const filtered = q
                  ? res.data.filter(
                      (a) =>
                        a.title.toLowerCase().includes(q) ||
                        a.referenceNumber.toLowerCase().includes(q),
                    )
                  : res.data;
                return filtered.slice(0, REFERENCE_SEARCH_LIMIT).map((item) => ({
                  kind: "announcement" as const,
                  id: item.id,
                  title: item.title,
                  typeLabel: t("sourceAnnouncement"),
                }));
              })
            : fetchAnnouncementAttachmentLibrary({ q: query || undefined }).then(
                (res) =>
                  res.data
                    .filter((item) => item.accessLevel === "PUBLIC")
                    .slice(0, REFERENCE_SEARCH_LIMIT)
                    .map((item) => ({
                      kind: "attachment" as const,
                      id: item.id,
                      title: item.fileName,
                      typeLabel: t("sourceAttachment"),
                    })),
              );

      rows
        .then((mapped) => {
          if (seq !== requestSeqRef.current) return;
          setResults(mapped);
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
    [t, tKnowledge],
  );

  function scheduleSearch(
    activeSource: MentionKind,
    query: string,
    knowledgeType: KnowledgeType | null,
  ) {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(
      () => runSearch(activeSource, query, knowledgeType),
      DEBOUNCE_MS,
    );
  }

  function enterSourcePicker() {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    requestSeqRef.current += 1;
    setSource(null);
    setSelectedType(null);
    setResults([]);
    setSearchError(null);
    setLoading(false);
    setHighlighted(0);
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
    setSource(null);
    setSelectedType(null);
    setResults([]);
    setSearchError(null);
    setLoading(false);
    if (debounceRef.current) clearTimeout(debounceRef.current);
  }

  function syncMentionUi(nextMention: MentionQuery | null) {
    setMention(nextMention);
    if (!nextMention) {
      enterSourcePicker();
      return;
    }
    const query = nextMention.query;
    const activeSource = sourceRef.current;
    if (activeSource === null) {
      // Outermost picker — always the 3-source list; typed text is not a
      // cross-source query (no single search spans Knowledge/Pengumuman/
      // Lampiran), so just keep results/loading state clean.
      enterSourcePicker();
      return;
    }
    if (activeSource === "knowledge") {
      const type = selectedTypeRef.current;
      if (query === "" && type === null) {
        enterTypePicker();
        return;
      }
      scheduleSearch("knowledge", query, type);
      return;
    }
    scheduleSearch(activeSource, query, null);
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

  function selectSource(kind: MentionKind) {
    setSource(kind);
    setHighlighted(0);
    const query = mentionRef.current?.query ?? "";
    if (kind === "knowledge") {
      // A query may already be typed (the source picker ignores it, but
      // still tracks it) — carry it over exactly like the type picker's own
      // "typing bypasses the picker" behavior, instead of showing an empty
      // type picker.
      if (query === "") {
        enterTypePicker();
      } else {
        setSelectedType(null);
        runSearch("knowledge", query, null);
      }
      return;
    }
    setSelectedType(null);
    runSearch(kind, query, null);
  }

  function selectType(type: KnowledgeType) {
    setSelectedType(type);
    setHighlighted(0);
    runSearch("knowledge", mentionRef.current?.query ?? "", type);
  }

  function selectResult(item: MentionResult) {
    const root = editorRef.current;
    const current = mentionRef.current;
    if (!root || !current) return;

    const { caret } = getVisibleTextAndCaret(root);

    insertChipAtMention(
      root,
      current.start,
      caret,
      item.kind,
      item.title,
      item.id,
      item.typeLabel,
    );
    closeDropdown();
    emitFromEditor();
    root.focus();
  }

  /** Esc on bare `@` — close the menu and remove the trigger from the text. */
  function dismissEmptyMentionTrigger() {
    const root = editorRef.current;
    const current = mentionRef.current;
    if (!root || !current || current.query !== "") {
      suppressMentionUntilInputRef.current = true;
      closeDropdown();
      return;
    }
    deleteVisibleRange(root, current.start, current.start + 1);
    suppressMentionUntilInputRef.current = true;
    skipRenderFromValueRef.current = true;
    closeDropdown();
    onChange(serializeMentionEditor(root));
    root.focus();
  }

  function onEditorKeyDown(event: ReactKeyboardEvent<HTMLDivElement>) {
    if (!open) return;

    if (showSourcePicker) {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setHighlighted((i) => (i + 1) % MENTION_SOURCES.length);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setHighlighted(
          (i) => (i - 1 + MENTION_SOURCES.length) % MENTION_SOURCES.length,
        );
      } else if (event.key === "Enter" || event.key === "Tab") {
        event.preventDefault();
        const kind = MENTION_SOURCES[highlighted];
        if (kind) selectSource(kind);
      } else if (event.key === "Escape") {
        event.preventDefault();
        dismissEmptyMentionTrigger();
      }
      return;
    }

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
        enterSourcePicker();
      } else if (event.key === "Backspace") {
        event.preventDefault();
        enterSourcePicker();
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
      const query = mention?.query ?? "";
      if (query === "" && source === "knowledge" && selectedType) {
        enterTypePicker();
      } else if (query === "") {
        enterSourcePicker();
      } else {
        suppressMentionUntilInputRef.current = true;
        closeDropdown();
      }
    } else if (event.key === "Backspace" && (mention?.query ?? "") === "") {
      // Empty query in the results view — Backspace steps back one level
      // (Does not delete the `@`; browser still handles that on a later press.)
      event.preventDefault();
      if (source === "knowledge" && selectedType) {
        enterTypePicker();
      } else {
        enterSourcePicker();
      }
    }
  }

  function onEditorClick(event: ReactMouseEvent<HTMLDivElement>) {
    const target = event.target;
    if (!(target instanceof Element)) return;
    const chip = target.closest(`[${MENTION_CHIP_ATTR_KIND}]`);
    if (!chip || !editorRef.current?.contains(chip)) return;
    // Only Knowledge chips preview in place while composing; Pengumuman and
    // Lampiran are read on save (KnowledgeReferenceText) — no in-editor
    // preview surface for those two exists yet (Future Work).
    if (chip.getAttribute(MENTION_CHIP_ATTR_KIND) !== "knowledge") return;
    const knowledgeId = chip.getAttribute(MENTION_CHIP_ATTR_ID);
    if (!knowledgeId) return;
    event.preventDefault();
    setPreviewKnowledgeId(knowledgeId);
  }

  const activeOptionId = !open
    ? undefined
    : showSourcePicker
      ? `${listboxId}-source-${highlighted}`
      : showTypePicker
        ? `${listboxId}-type-${highlighted}`
        : results[highlighted]
          ? `${listboxId}-option-${highlighted}`
          : undefined;

  useEffect(() => {
    if (!open) return;
    const idFor = showSourcePicker
      ? `${listboxId}-source-${highlighted}`
      : showTypePicker
        ? `${listboxId}-type-${highlighted}`
        : `${listboxId}-option-${highlighted}`;
    const el = document.getElementById(idFor);
    if (el && typeof el.scrollIntoView === "function") {
      el.scrollIntoView({ block: "nearest" });
    }
  }, [highlighted, listboxId, open, results.length, showSourcePicker, showTypePicker]);

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

  useEffect(() => {
    if (!showTypePicker) return;
    let cancelled = false;
    fetchKnowledgeTypeCounts()
      .then((res) => {
        if (!cancelled) setTypeCounts(res.data);
      })
      .catch(() => {
        if (!cancelled) setTypeCounts(null);
      });
    return () => {
      cancelled = true;
    };
  }, [showTypePicker]);

  // Counts shown next to each source in the outermost `@` picker.
  useEffect(() => {
    if (!showSourcePicker) return;
    let cancelled = false;
    Promise.all([
      fetchKnowledgeTypeCounts().then((res) =>
        Object.values(res.data).reduce((sum, n) => sum + n, 0),
      ),
      fetchActiveAnnouncements().then((res) => res.data.length),
      fetchAnnouncementAttachmentLibrary({}).then(
        (res) => res.data.filter((item) => item.accessLevel === "PUBLIC").length,
      ),
    ])
      .then(([knowledge, announcement, attachment]) => {
        if (!cancelled) setSourceCounts({ knowledge, announcement, attachment });
      })
      .catch(() => {
        if (!cancelled) setSourceCounts(null);
      });
    return () => {
      cancelled = true;
    };
  }, [showSourcePicker]);

  const headerLabel = showSourcePicker
    ? t("chooseSource")
    : source === "knowledge"
      ? selectedType
        ? tKnowledge(knowledgeTypeKey(selectedType))
        : showTypePicker
          ? t("chooseType")
          : t("searchTitle")
      : source
        ? sourceLabel(source)
        : t("searchTitle");

  function goBackOneLevel() {
    if (source === "knowledge" && selectedType) {
      enterTypePicker();
    } else {
      enterSourcePicker();
    }
  }

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
            {!showSourcePicker ? (
              <button
                type="button"
                className="min-w-0 truncate text-left hover:text-ecmp-primary hover:underline"
                onMouseDown={(event) => {
                  event.preventDefault();
                  goBackOneLevel();
                }}
                title={t("backWithEsc")}
              >
                {headerLabel}
              </button>
            ) : (
              <span className="min-w-0 truncate">{headerLabel}</span>
            )}
          </div>
          {showSourcePicker ? (
            <p className="border-b border-ecmp-border px-3 py-1.5 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {t("sourcePickerHint")}
            </p>
          ) : showTypePicker ? (
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
            {showSourcePicker ? (
              MENTION_SOURCES.map((kind, index) => {
                const count = sourceCounts?.[kind];
                const optionLabel =
                  count == null
                    ? sourceLabel(kind)
                    : t("typeWithCount", { type: sourceLabel(kind), count });
                return (
                <li key={kind} role="none">
                  <div
                    id={`${listboxId}-source-${index}`}
                    role="option"
                    aria-selected={index === highlighted}
                    aria-label={optionLabel}
                    className={cn(
                      "flex cursor-pointer items-center gap-2 px-3 py-2 text-[length:var(--ecmp-font-body-small-size)]",
                      index === highlighted
                        ? "bg-ecmp-primary-muted"
                        : "hover:bg-ecmp-hover",
                    )}
                    onMouseDown={(event) => {
                      event.preventDefault();
                      selectSource(kind);
                    }}
                    onMouseEnter={() => setHighlighted(index)}
                  >
                    {kind === "knowledge" ? (
                      <IconFile
                        className="size-4 shrink-0 text-ecmp-text-secondary"
                        aria-hidden
                      />
                    ) : kind === "announcement" ? (
                      <IconBell
                        className="size-4 shrink-0 text-ecmp-text-secondary"
                        aria-hidden
                      />
                    ) : (
                      <IconPaperclip
                        className="size-4 shrink-0 text-ecmp-text-secondary"
                        aria-hidden
                      />
                    )}
                    <span className="min-w-0 flex-1 truncate">
                      {optionLabel}
                    </span>
                    <IconChevronRight
                      className="size-4 shrink-0 text-ecmp-text-secondary"
                      aria-hidden
                    />
                  </div>
                </li>
                );
              })
            ) : showTypePicker ? (
              KNOWLEDGE_MENTION_TYPES.map((type, index) => {
                const typeLabel = tKnowledge(knowledgeTypeKey(type));
                const count = typeCounts?.[type];
                const optionLabel =
                  count == null
                    ? typeLabel
                    : t("typeWithCount", { type: typeLabel, count });
                return (
                <li key={type} role="none">
                  <div
                    id={`${listboxId}-type-${index}`}
                    role="option"
                    aria-selected={index === highlighted}
                    aria-label={optionLabel}
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
                    <Badge tone="info" className="min-w-0 flex-1 px-1.5 py-0">
                      {optionLabel}
                    </Badge>
                    <IconChevronRight
                      className="size-4 shrink-0 text-ecmp-text-secondary"
                      aria-hidden
                    />
                  </div>
                </li>
                );
              })
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
                {source === "announcement"
                  ? t("emptyAnnouncement")
                  : source === "attachment"
                    ? t("emptyAttachment")
                    : t("empty")}
              </li>
            ) : (
              results.map((item, index) => (
                <li key={`${item.kind}:${item.id}`} role="none">
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
                        {item.typeLabel}
                      </Badge>
                      <p className="truncate font-medium text-ecmp-text-primary">
                        {item.title}
                      </p>
                    </div>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      ) : null}
      <KnowledgePreviewModal
        open={previewKnowledgeId !== null}
        knowledgeId={previewKnowledgeId}
        onClose={() => setPreviewKnowledgeId(null)}
      />
    </div>
  );
}
