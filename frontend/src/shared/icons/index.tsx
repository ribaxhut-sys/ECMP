import type { SVGProps } from "react";
import { cn } from "@/shared/utils";

export type IconProps = SVGProps<SVGSVGElement> & {
  title?: string;
};

function IconBase({
  className,
  title,
  children,
  ...props
}: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={title ? undefined : true}
      role={title ? "img" : undefined}
      className={cn("size-5 shrink-0", className)}
      {...props}
    >
      {title ? <title>{title}</title> : null}
      {children}
    </svg>
  );
}

export function IconMenu(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M4 6h16M4 12h16M4 18h16" />
    </IconBase>
  );
}

export function IconClose(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M6 6l12 12M18 6L6 18" />
    </IconBase>
  );
}

export function IconSearch(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </IconBase>
  );
}

export function IconBell(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
      <path d="M10 21a2 2 0 0 0 4 0" />
    </IconBase>
  );
}

export function IconUser(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20c0-4 4-6 8-6s8 2 8 6" />
    </IconBase>
  );
}

export function IconLogout(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <path d="M16 17l5-5-5-5" />
      <path d="M21 12H9" />
    </IconBase>
  );
}

export function IconDashboard(props: IconProps) {
  return (
    <IconBase {...props}>
      <rect x="3" y="3" width="8" height="8" rx="1.5" />
      <rect x="13" y="3" width="8" height="5" rx="1.5" />
      <rect x="13" y="10" width="8" height="11" rx="1.5" />
      <rect x="3" y="13" width="8" height="8" rx="1.5" />
    </IconBase>
  );
}

export function IconComplaints(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M7 8h10M7 12h6" />
      <path d="M5 4h14a2 2 0 0 1 2 2v14l-4-3H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z" />
    </IconBase>
  );
}

export function IconQueue(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M4 6h16" />
      <path d="M4 12h16" />
      <path d="M4 18h10" />
      <path d="M18 16v4" />
      <path d="M16 18h4" />
    </IconBase>
  );
}

export function IconAssignments(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="9" cy="8" r="3" />
      <path d="M3 19c0-3 2.5-5 6-5" />
      <path d="M15 11h6" />
      <path d="M18 8v6" />
    </IconBase>
  );
}

export function IconResolutions(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M9 11l3 3L22 4" />
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </IconBase>
  );
}

export function IconReports(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M4 19V5" />
      <path d="M4 19h16" />
      <path d="M8 15v-4" />
      <path d="M12 15V8" />
      <path d="M16 15v-6" />
    </IconBase>
  );
}

export function IconUsers(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="9" cy="8" r="3.5" />
      <path d="M2.5 19c0-3 3-5 6.5-5s6.5 2 6.5 5" />
      <circle cx="17" cy="9" r="2.5" />
      <path d="M21.5 19c0-2.2-1.8-4-4.5-4" />
    </IconBase>
  );
}

export function IconSettings(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </IconBase>
  );
}

export function IconTheme(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </IconBase>
  );
}

export function IconChevronRight(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M9 6l6 6-6 6" />
    </IconBase>
  );
}

export function IconAlert(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
      <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
    </IconBase>
  );
}

export function IconCheck(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M20 6 9 17l-5-5" />
    </IconBase>
  );
}

export function IconEmpty(props: IconProps) {
  return (
    <IconBase {...props}>
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <path d="M8 10h8M8 14h5" />
    </IconBase>
  );
}

export function IconSpinner({ className, ...props }: IconProps) {
  return (
    <IconBase className={cn("animate-spin", className)} {...props}>
      <path d="M12 3a9 9 0 1 0 9 9" />
    </IconBase>
  );
}

export function IconDownload(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M12 3v12" />
      <path d="M7 10l5 5 5-5" />
      <path d="M5 21h14" />
    </IconBase>
  );
}

export function IconExternalLink(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M14 4h6v6" />
      <path d="M10 14 20 4" />
      <path d="M20 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h5" />
    </IconBase>
  );
}

export function IconEye(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
      <circle cx="12" cy="12" r="3" />
    </IconBase>
  );
}

export function IconFile(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9z" />
      <path d="M14 3v6h6" />
    </IconBase>
  );
}

export function IconImage(props: IconProps) {
  return (
    <IconBase {...props}>
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <circle cx="9" cy="10" r="1.5" />
      <path d="m21 15-4.5-4.5L8 19" />
    </IconBase>
  );
}

export function IconZoomIn(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="11" cy="11" r="6" />
      <path d="M11 8v6M8 11h6" />
      <path d="m20 20-3.5-3.5" />
    </IconBase>
  );
}

export function IconZoomOut(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="11" cy="11" r="6" />
      <path d="M8 11h6" />
      <path d="m20 20-3.5-3.5" />
    </IconBase>
  );
}

export function IconPaperclip(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M21.4 11.6 12 21a5 5 0 0 1-7-7l9.9-9.9a3.2 3.2 0 0 1 4.5 4.5L9.7 18.3a1.4 1.4 0 0 1-2-2l8.5-8.5" />
    </IconBase>
  );
}
