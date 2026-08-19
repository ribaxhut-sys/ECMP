"use client";

import { IconFile, IconImage } from "@/shared/icons";
import { getPreviewKind } from "@/features/attachments/fileTypes";
import type { KnowledgeFile } from "@/lib/api/types";
import { cn } from "@/shared/utils";

/** Compact file-type cue for Knowledge list / file rows (PDF, image, other). */
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
  if (kind === "pdf") {
    return (
      <IconFile className={cn(box, "shrink-0 text-ecmp-danger", className)} aria-hidden />
    );
  }
  if (kind === "docx") {
    return (
      <IconFile className={cn(box, "shrink-0 text-ecmp-info", className)} aria-hidden />
    );
  }
  return (
    <IconFile className={cn(box, "shrink-0 text-ecmp-text-secondary", className)} aria-hidden />
  );
}
