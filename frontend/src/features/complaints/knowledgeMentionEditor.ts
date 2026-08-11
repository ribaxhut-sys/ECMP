/**
 * Contenteditable helpers for Option A Knowledge mentions:
 * visible chips (title only) ↔ stored `@[title](knowledge:id)` markers.
 */

import {
  buildKnowledgeMarker,
  parseKnowledgeReferenceSegments,
} from "./knowledgeReferenceMarker";

export const KNOWLEDGE_CHIP_ATTR_ID = "data-knowledge-id";
export const KNOWLEDGE_CHIP_ATTR_TITLE = "data-knowledge-title";

/** Shared chip look: blue italic, underline on hover only, no background. */
export const knowledgeReferenceChipClassName =
  "inline cursor-pointer border-0 bg-transparent p-0 align-baseline font-medium italic text-ecmp-primary underline-offset-2 hover:underline";

export function isKnowledgeChip(node: Node | null): node is HTMLElement {
  return (
    node instanceof HTMLElement &&
    node.hasAttribute(KNOWLEDGE_CHIP_ATTR_ID) &&
    node.hasAttribute(KNOWLEDGE_CHIP_ATTR_TITLE)
  );
}

export function createKnowledgeChip(
  doc: Document,
  title: string,
  knowledgeId: string,
): HTMLSpanElement {
  const chip = doc.createElement("span");
  chip.setAttribute(KNOWLEDGE_CHIP_ATTR_ID, knowledgeId);
  chip.setAttribute(KNOWLEDGE_CHIP_ATTR_TITLE, title);
  chip.contentEditable = "false";
  chip.className = knowledgeReferenceChipClassName;
  chip.textContent = title || "—";
  chip.setAttribute("role", "link");
  chip.tabIndex = -1;
  return chip;
}

/** Walk the editor DOM → storage string with markers. */
export function serializeMentionEditor(root: HTMLElement): string {
  let out = "";
  const walk = (node: Node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      out += node.textContent ?? "";
      return;
    }
    if (isKnowledgeChip(node)) {
      const id = node.getAttribute(KNOWLEDGE_CHIP_ATTR_ID) ?? "";
      const title = node.getAttribute(KNOWLEDGE_CHIP_ATTR_TITLE) ?? "";
      out += buildKnowledgeMarker(title, id);
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
        createKnowledgeChip(doc, segment.title, segment.knowledgeId),
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
    if (isKnowledgeChip(node)) {
      out += node.getAttribute(KNOWLEDGE_CHIP_ATTR_TITLE) ?? node.textContent ?? "";
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
  title: string,
  knowledgeId: string,
): void {
  // Rebuild from visible text with mention replaced by a placeholder, then
  // swap placeholder for a chip — keeps mapping simple and reliable.
  const { text } = getVisibleTextAndCaret(root);
  const before = text.slice(0, mentionStart);
  const after = text.slice(caretVisible);
  const needsSpace = after.length === 0 || !/^\s/.test(after);
  const placeholder = "\uFFF0"; // private-use sentinel
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

  const chip = createKnowledgeChip(root.ownerDocument, title, knowledgeId);
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
    if (isKnowledgeChip(node)) {
      const title =
        node.getAttribute(KNOWLEDGE_CHIP_ATTR_TITLE) ?? node.textContent ?? "";
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
