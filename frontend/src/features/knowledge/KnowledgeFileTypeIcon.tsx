"use client";

import { IconFile, IconImage } from "@/shared/icons";
import { Badge, type BadgeTone } from "@/shared/ui";
import { fileTypeLabel, getPreviewKind } from "@/features/attachments/fileTypes";
import type { KnowledgeFile } from "@/lib/api/types";
import { cn } from "@/shared/utils";

/** Extension label (from ``fileTypeLabel``) → badge color, so the same
 * extension always reads the same at a glance across the Knowledge catalog,
 * file manager, and upload staging list. Anything not listed here (and any
 * future accepted extension) falls back to a neutral badge. */
const EXTENSION_TONE: Record<string, BadgeTone> = {
  PDF: "danger",
  DOC: "info",
  DOCX: "info",
  XLS: "success",
  XLSX: "success",
  ZIP: "warning",
};

/** Per-extension file-type cue for Knowledge list / file rows. Images get a
 * picture glyph; every other accepted type (PDF, Word, Excel, ZIP, text, …)
 * gets a small colored badge with its extension, so the type is legible
 * without relying on color alone. */
export function KnowledgeFileTypeIcon({
  file,
  className,
  size = "md",
}: {
  file: Pick<KnowledgeFile, "mimeType" | "fileName"> | null;
  className?: string;
  size?: "sm" | "md";
}) {
  const box = size === "sm" ? "size-4" : "size-5";
  if (!file) {
    return (
      <IconFile
        className={cn(box, "shrink-0 text-ecmp-text-secondary opacity-50", className)}
        aria-hidden
      />
    );
  }
  const kind = getPreviewKind(file.mimeType, null, file.fileName);
  if (kind === "image") {
    return (
      <IconImage className={cn(box, "shrink-0 text-ecmp-primary", className)} aria-hidden />
    );
  }
  const label = fileTypeLabel(file.mimeType, null, file.fileName);
  const tone = EXTENSION_TONE[label] ?? "neutral";
  return (
    <Badge
      tone={tone}
      aria-hidden
      className={cn(
        "shrink-0 !px-1.5 !py-0 font-semibold",
        size === "sm" &&
          "!text-[length:var(--ecmp-font-overline-size)] leading-4",
        className,
      )}
    >
      {label}
    </Badge>
  );
}
