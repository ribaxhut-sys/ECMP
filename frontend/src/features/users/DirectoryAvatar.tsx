import { cn } from "@/shared/utils";
import { userInitials } from "./directoryHelpers";

type DirectoryAvatarProps = {
  fullName: string;
  username: string;
  /** Kode yang sudah dibedakan bila ada pengguna lain berinisial sama. */
  initials?: string | null;
  size?: "sm" | "md" | "lg";
  className?: string;
};

const sizeClass = {
  sm: "size-9 text-[length:var(--ecmp-font-caption-size)]",
  md: "size-11 text-[length:var(--ecmp-font-helper-size)]",
  lg: "size-16 text-[length:var(--ecmp-font-section-title-size)]",
} as const;

export function DirectoryAvatar({
  fullName,
  username,
  initials: resolvedInitials,
  size = "md",
  className,
}: DirectoryAvatarProps) {
  const initials = resolvedInitials || userInitials({ fullName, username });

  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-full",
        "bg-ecmp-primary-muted font-semibold tracking-wide text-ecmp-primary",
        "ring-1 ring-inset ring-ecmp-primary/15",
        sizeClass[size],
        className,
      )}
      aria-hidden
    >
      {initials}
    </span>
  );
}
