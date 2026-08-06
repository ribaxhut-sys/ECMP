/**
 * L10-08 runtime language UAT — Playwright against running stack.
 * Scans visible text, placeholders, aria-labels, titles for English leftovers.
 */
import { chromium } from "playwright";
import fs from "node:fs";

const BASE = process.env.ECMP_UAT_BASE || "http://127.0.0.1:3000";
const API = process.env.ECMP_UAT_API || "http://127.0.0.1:8000";
const OUT = process.env.ECMP_UAT_OUT || "/tmp/ecmp-l10-08-uat.json";

const GLS_OK = new Set([
  "ECMP",
  "SLA",
  "KPI",
  "Case",
  "Inquiry",
  "Email",
  "Filter",
  "Severity",
  "Status",
  "ID",
  "UUID",
  "PDF",
  "JPEG",
  "PNG",
  "WebP",
  "MP4",
  "HTTP",
  "API",
  "Web",
  "OK",
  "NEW",
  "ASSIGNED",
  "IN_PROGRESS",
  "PENDING",
  "ESCALATED",
  "RESOLVED",
  "CLOSED",
  "REQUESTED",
  "APPROVED",
  "REJECTED",
  "BOOKED",
  "CHECKED_IN",
  "COMPLETED",
  "ON_TIME",
  "BREACHED",
  "REGISTERED",
  "OPEN",
  "STAGED",
  "CREATED",
  "Batch-1",
  "Batch 1",
  "Batch-2",
  "Batch 2",
  "Mode A",
  "Mode B",
  "Aggregate",
  "SoT",
]);

const EN_PHRASES = [
  "Sign in",
  "Sign out",
  "Log out",
  "Logout",
  "Login",
  "Dashboard",
  "Complaints",
  "Create Complaint",
  "Search",
  "Apply Filters",
  "Reset",
  "Page Size",
  "All Statuses",
  "All Priorities",
  "All Branches",
  "Descending",
  "Ascending",
  "Loading",
  "Retry",
  "No Records",
  "No data",
  "Access restricted",
  "Unable to load",
  "Something went wrong",
  "Try again",
  "Settings",
  "Users",
  "Reports",
  "Attachments",
  "Assignments",
  "Resolutions",
  "Queue",
  "Home",
  "Cancel",
  "Save",
  "Submit",
  "Confirm",
  "Delete",
  "Edit",
  "Create",
  "Back",
  "Next",
  "Previous",
  "Actions",
  "Priority",
  "Category",
  "Sort by",
  "Created At",
  "Check In",
  "Void",
  "Forgot Password",
  "Reset Password",
  "Supervisor Queue",
  "This page could not be found",
  "keluhan",
  "Kasus",
  "Komplain",
  "Hak Akses",
];

function mintRefresh() {
  if (process.env.ECMP_UAT_REFRESH) return process.env.ECMP_UAT_REFRESH.trim();
  throw new Error("ECMP_UAT_REFRESH is required");
}

function looksEnglish(text) {
  const t = text.replace(/\s+/g, " ").trim();
  if (t.length < 2) return false;
  if (GLS_OK.has(t)) return false;
  // strip known technical tokens
  let cleaned = t;
  for (const ok of GLS_OK) {
    cleaned = cleaned.replaceAll(ok, " ");
  }
  cleaned = cleaned
    .replace(/\b[a-z_]+:[a-z_*]+\b/g, " ")
    .replace(/\/api\/v1\/[a-z0-9/{}_-]+/gi, " ")
    .replace(/\b(?:FR|BR|API|BQ|CAP|SCR|D)-\d+[A-Z0-9-]*/g, " ")
    .replace(/\bUUID\b/g, " ")
    .replace(/[0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!cleaned) return false;
  // Indonesian markers
  if (
    /\b(yang|dan|atau|untuk|dari|dengan|pada|tidak|belum|sudah|akan|pengaduan|antrian|dasbor|pengaturan|pengguna|lampiran|penugasan|resolusi|masuk|keluar|cari|simpan|batal|hapus|ubah|buat|muat|coba|tutup|konfirmasi|kembali|tindakan|prioritas|wajib|aktif|kata|sandi|izin|peran|cabang|laporan|atur|ulang|beranda|gagal|berhasil|memuat|menyimpan|mengirim|lihat|deskripsi|kategori|subjek|pelanggan|eskalasi|janji|temu|halaman|baris|tampilkan|kosongkan|terapkan|navigasi|dialog|notifikasi|profil|silakan|masukkan|pilih|unggah|unduh|tambah|kesalahan|terjadi|diperlukan|memerlukan|akun|sesi|tautan|format|minimal|karakter|ringkasan|status|filter|email|case|total|detail|metadata|diagnosis|unit|severity|menit|jam|hari|ini|itu|ke|di|ada|semua|ya|tidak|berikutnya|sebelumnya|menurun|menaik|urutkan|ukuran|berdasarkan|segera|hadir|tandai|kehadiran|berlaku|alasan)\b/i.test(
      cleaned,
    )
  ) {
    return false;
  }
  for (const p of EN_PHRASES) {
    if (new RegExp(`\\b${p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(t)) {
      return true;
    }
  }
  // Title Case multi-word English-looking
  if (/^[A-Z][a-z]+(?:\s+[A-Za-z]+){1,6}$/.test(cleaned) && /[aeiou]/i.test(cleaned)) {
    const words = cleaned.split(/\s+/);
    const indoish = words.filter((w) =>
      /^(dan|atau|untuk|dari|yang|ke|di|pada|dengan)$/i.test(w),
    );
    if (indoish.length === 0 && words.every((w) => /^[A-Za-z]+$/.test(w))) {
      return true;
    }
  }
  return false;
}

async function collectStrings(page) {
  return page.evaluate(() => {
    const out = [];
    const push = (kind, value, loc) => {
      const v = (value || "").replace(/\s+/g, " ").trim();
      if (!v) return;
      out.push({ kind, value: v, loc });
    };
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      const parent = n.parentElement;
      if (!parent) continue;
      const tag = parent.tagName.toLowerCase();
      if (["script", "style", "noscript"].includes(tag)) continue;
      const text = n.textContent || "";
      if (!text.trim()) continue;
      const loc =
        parent.getAttribute("data-testid") ||
        parent.id ||
        tag + (parent.className ? "." + String(parent.className).split(/\s+/)[0] : "");
      push("text", text, loc);
    }
    for (const el of document.querySelectorAll(
      "[aria-label], [title], [placeholder], [alt]",
    )) {
      for (const attr of ["aria-label", "title", "placeholder", "alt"]) {
        if (el.hasAttribute(attr)) {
          push(
            attr,
            el.getAttribute(attr),
            el.tagName.toLowerCase() + (el.id ? "#" + el.id : ""),
          );
        }
      }
    }
    return out;
  });
}

const ROUTES = [
  { path: "/login", auth: false, name: "Login" },
  { path: "/dashboard", auth: true, name: "Dashboard" },
  { path: "/complaints", auth: true, name: "Pengaduan" },
  { path: "/complaints/new", auth: true, name: "Buat Pengaduan" },
  { path: "/complaints/cm/supervisor", auth: true, name: "Supervisor Queue" },
  { path: "/queue", auth: true, name: "Queue Dashboard" },
  { path: "/assignments", auth: true, name: "Assignment" },
  { path: "/resolutions", auth: true, name: "Resolution" },
  { path: "/attachments", auth: true, name: "Attachment" },
  { path: "/users", auth: true, name: "Users" },
  { path: "/settings", auth: true, name: "Settings / SLA" },
  { path: "/reports", auth: true, name: "Reports" },
  { path: "/profile", auth: true, name: "Profile" },
  { path: "/profile/security", auth: true, name: "Profile Security" },
  { path: "/not-a-real-page-404", auth: false, name: "404" },
];

async function main() {
  const refresh = mintRefresh();
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ locale: "id-ID" });
  // Cookie for API host (baked NEXT_PUBLIC may be IP or localhost)
  const apiHost = new URL(API).hostname;
  await context.addCookies([
    {
      name: "ecmp_refresh_token",
      value: refresh,
      domain: apiHost,
      path: "/api/v1/auth",
      httpOnly: true,
      secure: false,
      sameSite: "Lax",
    },
  ]);
  // Also set for localhost alias
  if (apiHost !== "localhost" && apiHost !== "127.0.0.1") {
    await context.addCookies([
      {
        name: "ecmp_refresh_token",
        value: refresh,
        domain: "127.0.0.1",
        path: "/api/v1/auth",
        httpOnly: true,
        secure: false,
        sameSite: "Lax",
      },
      {
        name: "ecmp_refresh_token",
        value: refresh,
        domain: "localhost",
        path: "/api/v1/auth",
        httpOnly: true,
        secure: false,
        sameSite: "Lax",
      },
    ]);
  }

  const findings = [];
  const pages = [];

  for (const route of ROUTES) {
    const page = await context.newPage();
    const url = BASE + route.path;
    let status = "ok";
    try {
      await page.goto(url, { waitUntil: "networkidle", timeout: 45000 });
      await page.waitForTimeout(800);
      // dismiss loading
      await page.waitForTimeout(500);
      const strings = await collectStrings(page);
      const hits = [];
      for (const s of strings) {
        if (looksEnglish(s.value)) {
          hits.push(s);
        }
      }
      // dedupe
      const seen = new Set();
      const uniq = [];
      for (const h of hits) {
        const k = h.kind + "|" + h.value;
        if (seen.has(k)) continue;
        seen.add(k);
        uniq.push(h);
      }
      const shot = `/tmp/ecmp-l10-08-${route.name.replace(/\s+/g, "_").toLowerCase()}.png`;
      await page.screenshot({ path: shot, fullPage: true });
      pages.push({
        name: route.name,
        path: route.path,
        finalUrl: page.url(),
        title: await page.title(),
        englishHits: uniq,
        screenshot: shot,
        sampleText: strings
          .filter((x) => x.kind === "text")
          .map((x) => x.value)
          .slice(0, 40),
      });
      for (const h of uniq) {
        findings.push({ page: route.name, path: route.path, ...h, screenshot: shot });
      }
    } catch (err) {
      status = String(err);
      pages.push({ name: route.name, path: route.path, error: status });
    } finally {
      await page.close();
    }
  }

  // Deep-link first complaint if list available
  const page = await context.newPage();
  try {
    await page.goto(BASE + "/complaints", { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForTimeout(1000);
    const href = await page.evaluate(() => {
      const a = document.querySelector('a[href*="/complaints/"]');
      return a ? a.getAttribute("href") : null;
    });
    if (href) {
      await page.goto(BASE + href, { waitUntil: "networkidle", timeout: 45000 });
      await page.waitForTimeout(800);
      const strings = await collectStrings(page);
      const hits = strings.filter((s) => looksEnglish(s.value));
      const shot = "/tmp/ecmp-l10-08-complaint_detail.png";
      await page.screenshot({ path: shot, fullPage: true });
      pages.push({
        name: "Detail Pengaduan",
        path: href,
        englishHits: hits,
        screenshot: shot,
        sampleText: strings
          .filter((x) => x.kind === "text")
          .map((x) => x.value)
          .slice(0, 40),
      });
      for (const h of hits) {
        findings.push({ page: "Detail Pengaduan", path: href, ...h, screenshot: shot });
      }
    }
  } catch (err) {
    pages.push({ name: "Detail Pengaduan", error: String(err) });
  } finally {
    await page.close();
  }

  await browser.close();

  const report = {
    base: BASE,
    api: API,
    pagesAudited: pages.length,
    englishFindingCount: findings.length,
    findings,
    pages: pages.map((p) => ({
      name: p.name,
      path: p.path,
      finalUrl: p.finalUrl,
      error: p.error,
      hitCount: (p.englishHits || []).length,
      hits: p.englishHits || [],
      screenshot: p.screenshot,
      sampleText: p.sampleText,
    })),
  };
  fs.writeFileSync(OUT, JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ pages: report.pagesAudited, findings: report.englishFindingCount, out: OUT }, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
