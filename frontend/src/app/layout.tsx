import type { Metadata } from "next";
import { Source_Sans_3 } from "next/font/google";
import { AuthProvider } from "@/auth/AuthProvider";
import "./globals.css";

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-ecmp-sans",
});

export const metadata: Metadata = {
  title: "ECMP",
  description: "Enterprise Complaint Management Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={sourceSans.variable}>
      <body className={sourceSans.className}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
