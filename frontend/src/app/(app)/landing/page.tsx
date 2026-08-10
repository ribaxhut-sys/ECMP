import { ComplaintsLandingView } from "@/features/landing";

/**
 * Landing Page Pengaduan — explicit destination for "membuka Pengaduan",
 * reached via the sidebar Brand/logo (see Sidebar.tsx useShellNav homeHref).
 * Not the app's default home — that's Dashboard; see the "/" entry-point
 * gate (post-login unread-announcement redirect milestone).
 */
export default function LandingPage() {
  return <ComplaintsLandingView />;
}
