import type { Metadata } from "next";
import { AuthProvider } from "@/auth/AuthProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "ECMP Dashboard",
  description: "Enterprise Complaint Management Platform — Dashboard v1.0.0",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
