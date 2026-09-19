/**
 * Contenteditable helpers for Option A `@` mentions:
 * visible chips (title only) ↔ stored `@[title](<kind>:id)` markers.
 * Shared by all three mention kinds (knowledge / announcement / attachment).
 */

import {
  buildMentionMarker,
  parseKnowledgeReferenceSegments,
  type MentionKind,
} from "./knowledgeReferenceMarker";

export const MENTION_CHIP_ATTR_KIND = "data-mention-kind";
export const MENTION_CHIP_ATTR_ID = "data-mention-id";
export const MENTION_CHIP_ATTR_TITLE = "data-mention-title";
export const MENTION_CHIP_ATTR_TYPE = "data-mention-type-label";

/** Shared chip look: blue italic, underline on hover only, no background.
 * `!` beats the global ``button { font: inherit; color: inherit }`` reset. */
export const knowledgeReferenceChipClassName =
  "inline cursor-pointer border-0 bg-transparent p-0 align-baseline !font-medium !italic !text-ecmp-primary underline-offset-2 hover:underline";

/** Inactive / expired / archived / deleted reference — red so it differs
 * from an active one. */
export const knowledgeReferenceChipInactiveClassName =
  "inline cursor-pointer border-0 bg-transparent p-0 align-baseline !font-medium !italic !text-ecmp-danger underline-offset-2 hover:underline";

export function knowledgeReferenceChipClass(active: boolean): string {
  return active
    ? knowledgeReferenceChipClassName
    : knowledgeReferenceChipInactiveClassName;
}

export function isMentionChip(node: Node | null): node is HTMLElement {
  return (
    node instanceof HTMLElement &&
    node.hasAttribute(MENTION_CHIP_ATTR_KIND) &&
    node.hasAttribute(MENTION_CHIP_ATTR_ID) &&
    node.hasAttribute(MENTION_CHIP_ATTR_TITLE)
  );
}

export function createMentionChip(
  doc: Document,
  kind: MentionKind,
  title: string,
  id: string,
  typeLabel?: string | null,
): HTMLSpanElement {
  const chip = doc.createElement("span");
  chip.setAttribute(MENTION_CHIP_ATTR_KIND, kind);
  chip.setAttribute(MENTION_CHIP_ATTR_ID, id);
  chip.setAttribute(MENTION_CHIP_ATTR_TITLE, title);
  chip.contentEditable = "false";
  chip.className = knowledgeReferenceChipClassName;
  chip.setAttribute("role", "link");
  chip.tabIndex = -1;
  fillMentionChipContents(chip, title, typeLabel);
  return chip;
}

/** Add/replace the type tag inside a chip without changing the stored title. */
export function setMentionChipTypeLabel(
  chip: HTMLElement,
  typeLabel: string,
): void {
  const title = chip.getAttribute(MENTION_CHIP_ATTR_TITLE) ?? "";
  fillMentionChipContents(chip, title, typeLabel);
}

function fillMentionChipContents(
  chip: HTMLElement,
  title: string,
  typeLabel?: string | null,
): void {
  const doc = chip.ownerDocument;
  chip.replaceChildren();
  const label = typeLabel?.trim() ?? "";
  if (label) {
    chip.setAttribute(MENTION_CHIP_ATTR_TYPE, label);
    const badge = doc.createElement("span");
    badge.setAttribute("aria-hidden", "true");
    badge.className =
      "mr-1 inline-flex items-center rounded-[var(--ecmp-radius-badge)] bg-ecmp-info-bg px-1.5 py-0 align-baseline text-[length:var(--ecmp-font-caption-size)] font-medium not-italic tracking-wide text-ecmp-info-text";
    badge.textContent = label;
    chip.appendChild(badge);
  } else {
    chip.removeAttribute(MENTION_CHIP_ATTR_TYPE);
  }
  chip.appendChild(doc.createTextNode(label ? ` ${title || "—"}` : title || "—"));
  chip.setAttribute(
    "aria-label",
    label ? `${label} ${title || "—"}`.trim() : title || "—",
  );
}

/** Walk the editor DOM → storage string with markers. */
export function serializeMentionEditor(root: HTMLElement): string {
  let out = "";
  const walk = (node: Node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      out += node.textContent ?? "";
      return;
    }
    if (isMentionChip(node)) {
      const kind = node.getAttribute(MENTION_CHIP_ATTR_KIND) as MentionKind;
      const id = node.getAttribute(MENTION_CHIP_ATTR_ID) ?? "";
      const title = node.getAttribute(MENTION_CHIP_ATTR_TITLE) ?? "";
      out += buildMentionMarker(kind, title, id);
      return;
    }
    if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node as HTMLElement;
      if (el.tagName === "BR") {
        out += "\n";
        return;
      }
      for (const child of Array.from(el.childNodes)) {
        walk(child);
      }
      // Block-ish ends: treat DIV/P as newline when not last empty
      if (
        (el.tagName === "DIV" || el.tagName === "P") &&
        el.parentElement === root &&
        el.nextSibling
      ) {
        if (!out.endsWith("\n")) out += "\n";
      }
    }
  };
  for (const child of Array.from(root.childNodes)) {
    walk(child);
  }
  return out;
}

/** Replace editor contents from a storage value (markers → chips). */
export function renderMentionEditor(
  root: HTMLElement,
  storageValue: string,
): void {
  const doc = root.ownerDocument;
  root.replaceChildren();
  const segments = parseKnowledgeReferenceSegments(storageValue);
  if (segments.length === 0) {
    // Keep a trailing text node so the caret has somewhere to go.
    root.appendChild(doc.createTextNode(""));
    return;
  }
  for (const segment of segments) {
    if (segment.type === "text") {
      // Preserve newlines as <br> + text splits for contenteditable.
      const parts = segment.value.split("\n");
      parts.forEach((part, index) => {
        if (part) root.appendChild(doc.createTextNode(part));
        if (index < parts.length - 1) {
          root.appendChild(doc.createElement("br"));
        }
      });
    } else {
      root.appendChild(
        createMentionChip(doc, segment.kind, segment.title, segment.id),
      );
    }
  }
}

/**
 * Visible plain text (chips contribute title only) + caret index in that text.
 * Used for `@` trigger detection so stored marker length never leaks into UX.
 */
export function getVisibleTextAndCaret(root: HTMLElement): {
  text: string;
  caret: number;
} {
  const sel = root.ownerDocument.defaultView?.getSelection();
  if (!sel || sel.rangeCount === 0) {
    return { text: visibleTextOf(root), caret: visibleTextOf(root).length };
  }
  const range = sel.getRangeAt(0);
  if (!root.contains(range.startContainer)) {
    const text = visibleTextOf(root);
    return { text, caret: text.length };
  }
  const pre = range.cloneRange();
  pre.selectNodeContents(root);
  pre.setEnd(range.startContainer, range.startOffset);
  const caretFragment = pre.cloneContents();
  const caret = visibleTextOfFragment(caretFragment).length;
  return { text: visibleTextOf(root), caret };
}

function visibleTextOf(root: HTMLElement): string {
  return visibleTextOfFragment(root);
}

function visibleTextOfFragment(root: Node): string {
  let out = "";
  const walk = (node: Node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      out += node.textContent ?? "";
      return;
    }
    if (isMentionChip(node)) {
      out += node.getAttribute(MENTION_CHIP_ATTR_TITLE) ?? node.textContent ?? "";
      return;
    }
    if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node as HTMLElement;
      if (el.tagName === "BR") {
        out += "\n";
        return;
      }
      for (const child of Array.from(el.childNodes)) walk(child);
    }
  };
  if (root instanceof DocumentFragment || root instanceof HTMLElement) {
    for (const child of Array.from(root.childNodes)) walk(child);
  } else {
    walk(root);
  }
  return out;
}

/** Delete the in-progress `@query` (visible) and insert a chip at the caret. */
export function insertChipAtMention(
  root: HTMLElement,
  mentionStart: number,
  caretVisible: number,
  kind: MentionKind,
  title: string,
  id: string,
  typeLabel?: string | null,
): void {
  // Rebuild from visible text with mention replaced by a placeholder, then
  // swap placeholder for a chip — keeps mapping simple and reliable.
  const { text } = getVisibleTextAndCaret(root);
  const before = text.slice(0, mentionStart);
  const after = text.slice(caretVisible);
  const needsSpace = after.length === 0 || !/^\s/.test(after);
  const placeholder = String.fromCharCode(0xfff0); // private-use sentinel
  const nextVisible = before + placeholder + (needsSpace ? " " : "") + after;

  // Map current chips by title+id order from existing DOM, then re-apply
  // storage rebuild: serialize after mutating DOM directly instead.
  const sel = root.ownerDocument.defaultView?.getSelection();
  if (!sel) return;

  // Walk visible offsets to find text node range covering [@query]
  const absStart = mentionStart;
  const absEnd = caretVisible;
  const startPoint = locateVisibleOffset(root, absStart);
  const endPoint = locateVisibleOffset(root, absEnd);
  if (!startPoint || !endPoint) return;

  const range = root.ownerDocument.createRange();
  range.setStart(startPoint.node, startPoint.offset);
  range.setEnd(endPoint.node, endPoint.offset);
  range.deleteContents();

  const chip = createMentionChip(root.ownerDocument, kind, title, id, typeLabel);
  range.insertNode(chip);

  // Trailing space after chip when needed
  if (needsSpace) {
    const space = root.ownerDocument.createTextNode(" ");
    chip.after(space);
    placeCaret(space, 1);
  } else {
    placeCaretAfter(chip);
  }

  void nextVisible; // documentation of intended visible shape
}

function placeCaret(node: Node, offset: number) {
  const sel = node.ownerDocument?.defaultView?.getSelection();
  if (!sel) return;
  const range = node.ownerDocument!.createRange();
  range.setStart(node, offset);
  range.collapse(true);
  sel.removeAllRanges();
  sel.addRange(range);
}

function placeCaretAfter(node: Node) {
  const sel = node.ownerDocument?.defaultView?.getSelection();
  if (!sel) return;
  const range = node.ownerDocument!.createRange();
  range.setStartAfter(node);
  range.collapse(true);
  sel.removeAllRanges();
  sel.addRange(range);
}

/** Delete a visible-text range (e.g. bare `@` on Escape). */
export function deleteVisibleRange(
  root: HTMLElement,
  start: number,
  end: number,
): void {
  if (end <= start) return;
  const startPoint = locateVisibleOffset(root, start);
  const endPoint = locateVisibleOffset(root, end);
  if (!startPoint || !endPoint) return;
  const range = root.ownerDocument.createRange();
  range.setStart(startPoint.node, startPoint.offset);
  range.setEnd(endPoint.node, endPoint.offset);
  range.deleteContents();
  range.collapse(true);
  const sel = root.ownerDocument.defaultView?.getSelection();
  if (!sel) return;
  sel.removeAllRanges();
  sel.addRange(range);
}

/**
 * Client rect for a visible-text offset (e.g. the `@` that opened the menu).
 * Used to anchor the mention search popover beside the trigger.
 */
export function getVisibleOffsetRect(
  root: HTMLElement,
  offset: number,
): DOMRect | null {
  const point = locateVisibleOffset(root, offset);
  if (!point) return null;
  const range = root.ownerDocument.createRange();
  try {
    if (point.node.nodeType === Node.TEXT_NODE) {
      const len = point.node.textContent?.length ?? 0;
      const start = Math.min(Math.max(point.offset, 0), len);
      const end = Math.min(start + 1, len);
      range.setStart(point.node, start);
      range.setEnd(point.node, end > start ? end : start);
    } else {
      range.setStart(point.node, point.offset);
      range.collapse(true);
    }
  } catch {
    return null;
  }
  const rect =
    typeof range.getBoundingClientRect === "function"
      ? range.getBoundingClientRect()
      : null;
  if (
    !rect ||
    (rect.width === 0 && rect.height === 0 && rect.top === 0 && rect.left === 0)
  ) {
    // Collapsed/empty range or jsdom — fall back to editor box.
    return root.getBoundingClientRect();
  }
  return rect;
}

function locateVisibleOffset(
  root: HTMLElement,
  target: number,
): { node: Node; offset: number } | null {
  let seen = 0;
  let result: { node: Node; offset: number } | null = null;

  const visit = (node: Node): boolean => {
    if (result) return true;
    if (node.nodeType === Node.TEXT_NODE) {
      const len = node.textContent?.length ?? 0;
      if (seen + len >= target) {
        result = { node, offset: target - seen };
        return true;
      }
      seen += len;
      return false;
    }
    if (isMentionChip(node)) {
      const title =
        node.getAttribute(MENTION_CHIP_ATTR_TITLE) ?? node.textContent ?? "";
      const len = title.length;
      if (seen + len >= target) {
        // Caret lands on chip boundary — place after chip when target is end
        if (target === seen) {
          result = { node: node.parentNode!, offset: indexOf(node) };
        } else {
          result = { node: node.parentNode!, offset: indexOf(node) + 1 };
        }
        return true;
      }
      seen += len;
      return false;
    }
    if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node as HTMLElement;
      if (el.tagName === "BR") {
        if (seen + 1 >= target) {
          result = { node: el.parentNode!, offset: indexOf(el) + 1 };
          return true;
        }
        seen += 1;
        return false;
      }
      for (const child of Array.from(el.childNodes)) {
        if (visit(child)) return true;
      }
    }
    return false;
  };

  for (const child of Array.from(root.childNodes)) {
    if (visit(child)) break;
  }
  if (!result && target <= seen) {
    // End of content
    result = { node: root, offset: root.childNodes.length };
  }
  return result;
}

function indexOf(node: Node): number {
  const parent = node.parentNode;
  if (!parent) return 0;
  return Array.from(parent.childNodes).indexOf(node as ChildNode);
}
