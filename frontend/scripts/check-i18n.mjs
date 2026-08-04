#!/usr/bin/env node
/**
 * I18N guardrail — static localization coverage validator.
 *
 * Follow-on to the Wave 1–4 i18n recovery program: prevents the app from
 * silently regressing back into rendering "…" for a missing translation key.
 *
 * Detects, from source only (no running app, no network):
 *   1. Missing translation keys (literal AND statically-resolvable dynamic calls)
 *   2. EN / ID key-set parity mismatches
 *   3. Duplicate keys within a single locale JSON file
 *   4. Invalid JSON in either locale file
 *   5. Dynamic translation keys resolved via local lookup tables / switch functions
 *
 * Hard-fails CI (exit 1) on 1–4. Everything else (unused entries, hardcoded
 * English, duplicate values, cross-namespace naming drift) is a warning only
 * and never fails the build — see FALSE-POSITIVE AVOIDANCE in the header of
 * each checker below, and the "Dynamic-key limitations" note near resolveDynamicKey().
 *
 * Usage:
 *   node scripts/check-i18n.mjs
 *   node scripts/check-i18n.mjs --quiet   (suppress warning sections)
 *
 * Exit codes:
 *   0 = PASS (no missing keys, no parity mismatch, no duplicate keys, valid JSON)
 *   1 = FAIL
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = path.resolve(__dirname, "..");
const SRC_ROOT = path.join(FRONTEND_ROOT, "src");
const MESSAGES_DIR = path.join(FRONTEND_ROOT, "messages");
const LOCALES = ["en", "id"];

const QUIET = process.argv.includes("--quiet");

// ---------------------------------------------------------------------------
// Small utilities
// ---------------------------------------------------------------------------

/** Recursively collect .ts/.tsx source files, excluding tests and node_modules. */
function walkSourceFiles(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...walkSourceFiles(full));
      continue;
    }
    if (!/\.(tsx?|mts)$/.test(entry.name)) continue;
    if (/\.(test|spec)\.(tsx?|mts)$/.test(entry.name)) continue;
    if (entry.name.endsWith(".d.ts")) continue;
    out.push(full);
  }
  return out;
}

function lineOf(text, index) {
  return text.slice(0, index).split("\n").length;
}

function relPath(p) {
  return path.relative(FRONTEND_ROOT, p).replace(/\\/g, "/");
}

// ---------------------------------------------------------------------------
// 1. Locale JSON loading — invalid JSON + duplicate-key detection
//
// JSON.parse silently keeps the *last* occurrence of a duplicate key, so a
// duplicate is otherwise invisible. We re-scan the raw text with a small
// brace/bracket-depth tracker (string-aware, so braces inside string values
// don't confuse it) and flag any key seen twice at the same object path.
// ---------------------------------------------------------------------------

function findDuplicateKeys(raw) {
  const duplicates = [];
  const pathStack = []; // entries: { kind: "object"|"array", key: string|null }
  const seenStack = [new Map()];
  let pendingChildKey = null; // key just read, waiting to see if `{`/`[` follows
  let i = 0;
  let inString = false;
  let stringStart = -1;
  let expectingKey = true; // true right after `{` or `,` at object level

  const isObjectTop = () =>
    pathStack.length === 0 || pathStack[pathStack.length - 1].kind === "object";
  const currentPath = () =>
    pathStack.map((p) => p.key).filter(Boolean).join(".") || "(root)";

  while (i < raw.length) {
    const ch = raw[i];

    if (inString) {
      if (ch === "\\") {
        i += 2;
        continue;
      }
      if (ch === '"') {
        inString = false;
        const key = raw.slice(stringStart + 1, i);
        // Only treat this string as an object *key* if we're expecting one
        // (i.e. it's immediately followed by a colon).
        let j = i + 1;
        while (j < raw.length && /\s/.test(raw[j])) j++;
        if (expectingKey && isObjectTop() && raw[j] === ":") {
          const seen = seenStack[seenStack.length - 1];
          if (seen.has(key)) {
            duplicates.push({
              key,
              path: currentPath(),
              firstLine: seen.get(key),
              duplicateLine: lineOf(raw, stringStart),
            });
          } else {
            seen.set(key, lineOf(raw, stringStart));
          }
          pendingChildKey = key; // if the value is an object/array, it inherits this key
          expectingKey = false;
        }
      }
      i++;
      continue;
    }

    if (ch === '"') {
      inString = true;
      stringStart = i;
      i++;
      continue;
    }

    if (ch === "{" || ch === "[") {
      pathStack.push({ kind: ch === "{" ? "object" : "array", key: pendingChildKey });
      pendingChildKey = null;
      seenStack.push(new Map());
      expectingKey = ch === "{";
      i++;
      continue;
    }
    if (ch === "}" || ch === "]") {
      pathStack.pop();
      seenStack.pop();
      expectingKey = false;
      i++;
      continue;
    }
    if (ch === ":") {
      expectingKey = false;
      i++;
      continue;
    }
    if (ch === ",") {
      expectingKey = isObjectTop();
      i++;
      continue;
    }
    i++;
  }

  return duplicates;
}

function loadLocale(locale) {
  const file = path.join(MESSAGES_DIR, `${locale}.json`);
  const raw = fs.readFileSync(file, "utf8");
  let parsed;
  let parseError = null;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    parseError = err.message;
    parsed = null;
  }
  const duplicates = parseError ? [] : findDuplicateKeys(raw);
  return { locale, file, raw, parsed, parseError, duplicates };
}

function getNode(obj, dottedPath) {
  const parts = dottedPath.split(".");
  let node = obj;
  for (const part of parts) {
    if (node == null || typeof node !== "object" || !(part in node)) return undefined;
    node = node[part];
  }
  return node;
}

function flattenKeys(obj, prefix = "") {
  const out = new Set();
  for (const [k, v] of Object.entries(obj)) {
    const full = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) {
      for (const sub of flattenKeys(v, full)) out.add(sub);
    } else {
      out.add(full);
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
// 2. Source scanning — literal + dynamic translation key usage
//
// DETECTION ALGORITHM
// --------------------
// For every source file:
//   a. Find `const X = useTranslations("ns")` (or no-arg / variable-arg forms).
//   b. For every `X(<arg>, ...)` call in the same file, classify <arg>:
//        - string literal            -> direct key
//        - `identifier(...)`         -> look for a local function
//                                       `function identifier(...) { ... }`
//                                       in the same file and extract every
//                                       `return "literal"` inside it (handles
//                                       switch/if-chains and ternaries whose
//                                       branches are string literals)
//        - `identifier.property`     -> look for object/array literals in the
//                                       same file, or in a sibling module
//                                       reachable via a same-directory
//                                       relative `import { X } from "./Y"`,
//                                       containing `property: "literal"` and
//                                       collect every literal assigned to
//                                       that property name across the file
//        - bare `identifier`         -> look for `const identifier = <expr>`
//                                       nearby and re-classify <expr>
//        - anything else             -> "unresolved" (reported as a warning,
//                                       never a hard failure — see below)
// ---------------------------------------------------------------------------

const USE_TRANSLATIONS_RE =
  /const\s+(\w+)\s*=\s*useTranslations\(\s*(?:(["'`])((?:\\.|(?!\2).)*)\2)?\s*([^)]*)\)/g;

/** Extract the balanced-paren argument list starting at `openParenIdx` (the `(` itself). */
function extractBalancedArgs(text, openParenIdx) {
  let depth = 0;
  let i = openParenIdx;
  let inStr = null;
  const start = openParenIdx + 1;
  for (; i < text.length; i++) {
    const ch = text[i];
    if (inStr) {
      if (ch === "\\") {
        i++;
        continue;
      }
      if (ch === inStr) inStr = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") {
      inStr = ch;
      continue;
    }
    if (ch === "(") depth++;
    else if (ch === ")") {
      depth--;
      if (depth === 0) break;
    }
  }
  return { raw: text.slice(start, i), endIdx: i };
}

/** Split a balanced argument string on top-level commas. */
function splitTopLevelArgs(raw) {
  const parts = [];
  let depth = 0;
  let inStr = null;
  let cur = "";
  for (let i = 0; i < raw.length; i++) {
    const ch = raw[i];
    if (inStr) {
      cur += ch;
      if (ch === "\\") {
        cur += raw[++i] ?? "";
        continue;
      }
      if (ch === inStr) inStr = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") {
      inStr = ch;
      cur += ch;
      continue;
    }
    if ("([{".includes(ch)) depth++;
    if (")]}".includes(ch)) depth--;
    if (ch === "," && depth === 0) {
      parts.push(cur.trim());
      cur = "";
      continue;
    }
    cur += ch;
  }
  if (cur.trim()) parts.push(cur.trim());
  return parts;
}

const LITERAL_RE = /^(["'`])((?:\\.|(?!\1).)*)\1$/;

function isSimpleLiteral(expr) {
  const m = expr.match(LITERAL_RE);
  if (!m) return null;
  // Reject template literals containing interpolation — can't resolve statically.
  if (m[1] === "`" && /\$\{/.test(m[2])) return null;
  return m[2];
}

/** Find every `return "literal"` (or `'literal'`) inside a function body, by name, in `text`. */
function literalsReturnedByFunction(text, fnName) {
  const fnRe = new RegExp(`function\\s+${fnName}\\s*\\([^)]*\\)[^{]*\\{`, "g");
  const results = new Set();
  let m;
  while ((m = fnRe.exec(text))) {
    const bodyStart = m.index + m[0].length - 1; // at the opening `{`
    let depth = 0;
    let i = bodyStart;
    for (; i < text.length; i++) {
      if (text[i] === "{") depth++;
      else if (text[i] === "}") {
        depth--;
        if (depth === 0) break;
      }
    }
    const body = text.slice(bodyStart, i + 1);
    const retRe = /return\s+(["'])((?:\\.|(?!\1).)*)\1/g;
    let rm;
    while ((rm = retRe.exec(body))) results.add(rm[2]);
  }
  return results;
}

/** A translation key, by convention across this codebase, is a camelCase JS
 *  identifier (e.g. "activityCreated"). Enum/status codes read from the same
 *  kind of object ("NEW", "MEDIUM", "") are plain data, not lookup-table
 *  keys — filtering them out here is what keeps this resolver from mistaking
 *  an ordinary `{ status: "NEW" }` state object for a label lookup table. */
const KEY_LIKE_RE = /^[a-z][A-Za-z0-9]*$/;

/**
 * Find every literal assigned to `propName` in `text`, via either object-literal
 * syntax (`propName: "literal"`, lookup tables / row shapes) or assignment
 * syntax (`x.propName = "literal"`, e.g. validator functions building a
 * field-errors map). Only key-shaped literals are returned — see KEY_LIKE_RE.
 */
function literalsForProperty(text, propName) {
  const results = new Set();
  const colonRe = new RegExp(`\\b${propName}\\s*:\\s*(["'])((?:\\\\.|(?!\\1).)*)\\1`, "g");
  const assignRe = new RegExp(`\\.${propName}\\s*=\\s*(["'])((?:\\\\.|(?!\\1).)*)\\1`, "g");
  for (const re of [colonRe, assignRe]) {
    let m;
    while ((m = re.exec(text))) {
      if (KEY_LIKE_RE.test(m[2])) results.add(m[2]);
    }
  }
  return results;
}

/** Resolve a same-directory relative import ("./x" or "../x") to a source file path, if any. */
function resolveRelativeImport(fromFile, specifier) {
  const dir = path.dirname(fromFile);
  const base = path.resolve(dir, specifier);
  for (const suffix of ["", ".ts", ".tsx", "/index.ts", "/index.tsx"]) {
    const candidate = base + suffix;
    if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) return candidate;
  }
  return null;
}

function localImportFiles(text, fromFile) {
  const files = [fromFile];
  const importRe = /import\s+(?:type\s+)?\{[^}]*\}\s+from\s+["'](\.[^"']+)["']/g;
  let m;
  while ((m = importRe.exec(text))) {
    const resolved = resolveRelativeImport(fromFile, m[1]);
    if (resolved && !files.includes(resolved)) files.push(resolved);
  }
  return files;
}

/**
 * DYNAMIC-KEY LIMITATIONS
 * ------------------------
 * This resolver handles the concrete patterns found across ECMP's codebase
 * during the Wave 1–4 recovery (switch-returning-literals functions,
 * labelKey/titleKey/descriptionKey/badgeKey lookup-table properties, one hop
 * of local relative imports). It does NOT evaluate arbitrary JavaScript:
 *
 *   - Values built via string concatenation or template interpolation
 *     (`t(`prefix.${x}`)`) are NOT resolved.
 *   - Lookup tables defined more than one import-hop away, or re-exported
 *     through a barrel (`index.ts`) that itself re-exports from elsewhere
 *     without a literal object present, are NOT resolved.
 *   - Values passed in from outside the component (e.g. a `namespace` prop)
 *     are NOT resolved — the associated calls are reported as
 *     "dynamic-namespace-unresolved" (informational only, does not fail CI).
 *
 * Anything the resolver cannot prove is printed under "Unresolved dynamic
 * calls" as a warning, not a failure — a static tool must never hard-fail CI
 * on a pattern it cannot actually verify. Extend `resolveDynamicKey` here as
 * new patterns are introduced; see "Future maintenance" in the report.
 */
function resolveDynamicKey(expr, context) {
  const { fileText, fileFiles } = context;

  // identifier(...) — function call
  let m = expr.match(/^([A-Za-z_$][\w$]*)\(/);
  if (m) {
    const fnName = m[1];
    for (const text of fileFiles) {
      const found = literalsReturnedByFunction(text, fnName);
      if (found.size > 0) return { resolved: [...found], via: `function ${fnName}()` };
    }
    return null;
  }

  // identifier.property (single hop member access)
  m = expr.match(/^[A-Za-z_$][\w$]*\.([A-Za-z_$][\w$]*)$/);
  if (m) {
    const propName = m[1];
    for (const text of fileFiles) {
      const found = literalsForProperty(text, propName);
      if (found.size > 0) return { resolved: [...found], via: `property "${propName}"` };
    }
    return null;
  }

  // bare identifier — look for `const identifier = <expr>` and re-classify
  m = expr.match(/^[A-Za-z_$][\w$]*$/);
  if (m) {
    const declRe = new RegExp(`const\\s+${expr}\\s*=\\s*([^;\\n]+)`);
    const dm = fileText.match(declRe);
    if (dm) {
      const inner = dm[1].trim();
      const lit = isSimpleLiteral(inner);
      if (lit !== null) return { resolved: [lit], via: `const ${expr} = literal` };
      return resolveDynamicKey(inner.replace(/[;,]\s*$/, ""), context);
    }
    return null;
  }

  return null;
}

/**
 * Scan one file for useTranslations bindings and their call sites.
 * Returns { usages: [{ namespace, key, file, line, kind, via }], unresolved: [...] }
 */
function scanFile(file) {
  const text = fs.readFileSync(file, "utf8");
  const usages = [];
  const unresolved = [];
  const bindings = [];

  let bm;
  USE_TRANSLATIONS_RE.lastIndex = 0;
  while ((bm = USE_TRANSLATIONS_RE.exec(text))) {
    const [, varName, , nsLiteral, restArgs] = bm;
    if (nsLiteral !== undefined) {
      bindings.push({ varName, namespace: nsLiteral });
    } else if (restArgs && restArgs.trim()) {
      // useTranslations(namespaceVariable) — namespace not statically known.
      bindings.push({ varName, namespace: null });
    } else {
      bindings.push({ varName, namespace: "" }); // useTranslations() — root namespace
    }
  }
  if (bindings.length === 0) return { usages, unresolved };

  const fileFiles = localImportFiles(text, file).map((f) =>
    f === file ? text : fs.readFileSync(f, "utf8"),
  );

  for (const { varName, namespace } of bindings) {
    const callRe = new RegExp(`(?<![.\\w])${varName}\\(`, "g");
    let cm;
    while ((cm = callRe.exec(text))) {
      const openParen = cm.index + cm[0].length - 1;
      const { raw: argsRaw } = extractBalancedArgs(text, openParen);
      const args = splitTopLevelArgs(argsRaw);
      if (args.length === 0) continue;
      const keyExpr = args[0];
      const line = lineOf(text, cm.index);

      const literal = isSimpleLiteral(keyExpr);
      if (literal !== null) {
        if (namespace === null) {
          unresolved.push({ file, line, expr: keyExpr, reason: "dynamic-namespace-unresolved" });
          continue;
        }
        usages.push({ namespace, key: literal, file, line, kind: "literal" });
        continue;
      }

      if (namespace === null) {
        unresolved.push({ file, line, expr: keyExpr, reason: "dynamic-namespace-unresolved" });
        continue;
      }

      const result = resolveDynamicKey(keyExpr, { fileText: text, fileFiles });
      if (result) {
        for (const key of result.resolved) {
          usages.push({ namespace, key, file, line, kind: "dynamic", via: result.via });
        }
      } else {
        unresolved.push({ file, line, expr: keyExpr, reason: "unresolved-dynamic-expression" });
      }
    }
  }

  return { usages, unresolved };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  console.log("ECMP i18n guardrail — checking frontend/messages against frontend/src\n");

  // --- 1 & 3 & 4: load locales, invalid JSON, duplicate keys ---------------
  const locales = LOCALES.map(loadLocale);
  let hardFail = false;

  for (const loc of locales) {
    if (loc.parseError) {
      console.log(`✗ INVALID JSON — messages/${loc.locale}.json: ${loc.parseError}`);
      hardFail = true;
    }
  }
  if (hardFail) {
    console.log("\nFAIL — fix invalid JSON before the validator can check anything else.");
    process.exit(1);
  }

  let duplicatesFound = false;
  for (const loc of locales) {
    if (loc.duplicates.length > 0) {
      duplicatesFound = true;
      console.log(`✗ Duplicate keys in messages/${loc.locale}.json:`);
      for (const d of loc.duplicates) {
        console.log(
          `    "${d.path}.${d.key}" — first at line ${d.firstLine}, duplicated at line ${d.duplicateLine}`,
        );
      }
    }
  }

  const [en, id] = locales;

  // --- 2 & 5: scan source for literal + dynamic usage ----------------------
  const files = walkSourceFiles(SRC_ROOT);
  const allUsages = [];
  const allUnresolved = [];
  for (const file of files) {
    const { usages, unresolved } = scanFile(file);
    allUsages.push(...usages);
    allUnresolved.push(...unresolved);
  }

  // Dedup usages by (namespace, key), keep first occurrence for reporting.
  const usageByKey = new Map(); // "ns.key" -> first usage record
  for (const u of allUsages) {
    const full = u.namespace ? `${u.namespace}.${u.key}` : u.key;
    if (!usageByKey.has(full)) usageByKey.set(full, u);
  }

  // --- missing keys ----------------------------------------------------------
  const missing = [];
  for (const [full, u] of usageByKey) {
    const inEn = getNode(en.parsed, full) !== undefined;
    const inId = getNode(id.parsed, full) !== undefined;
    if (!inEn || !inId) {
      const missingIn = [!inEn ? "en" : null, !inId ? "id" : null].filter(Boolean).join(", ");
      missing.push({
        namespace: u.namespace,
        key: u.key,
        file: relPath(u.file),
        line: u.line,
        reason:
          u.kind === "literal"
            ? `missing locale (${missingIn})`
            : `missing locale (${missingIn}) — resolved dynamically via ${u.via}`,
      });
    }
  }

  console.log(`\nScanned ${files.length} source files, ${usageByKey.size} distinct reachable keys.\n`);

  if (missing.length > 0) {
    console.log(`✗ Missing translation keys: ${missing.length}\n`);
    console.log(
      ["Namespace", "File", "Line", "Missing key", "Reason"].join(" | "),
    );
    for (const m of missing.sort((a, b) => a.namespace.localeCompare(b.namespace) || a.key.localeCompare(b.key))) {
      console.log(
        [m.namespace || "(root)", m.file, m.line, m.key, m.reason].join(" | "),
      );
    }
    hardFail = true;
  } else {
    console.log("✓ Missing translation keys: 0");
  }

  // --- EN / ID parity ----------------------------------------------------
  const enKeys = flattenKeys(en.parsed);
  const idKeys = flattenKeys(id.parsed);
  const enOnly = [...enKeys].filter((k) => !idKeys.has(k));
  const idOnly = [...idKeys].filter((k) => !enKeys.has(k));
  if (enOnly.length > 0 || idOnly.length > 0) {
    console.log(`\n✗ EN / ID parity mismatch:`);
    if (enOnly.length) console.log(`  Present only in en.json (${enOnly.length}): ${enOnly.join(", ")}`);
    if (idOnly.length) console.log(`  Present only in id.json (${idOnly.length}): ${idOnly.join(", ")}`);
    hardFail = true;
  } else {
    console.log(`✓ EN / ID parity: PASS (${enKeys.size} keys each)`);
  }

  if (duplicatesFound) hardFail = true;
  else console.log("✓ Duplicate keys: 0");

  console.log("✓ JSON: valid");

  // --- optional warnings (never fail CI) ----------------------------------
  if (!QUIET) {
    if (allUnresolved.length > 0) {
      console.log(`\n⚠ Unresolved dynamic calls (informational — could not be statically verified): ${allUnresolved.length}`);
      const byReason = new Map();
      for (const u of allUnresolved) {
        byReason.set(u.reason, (byReason.get(u.reason) ?? 0) + 1);
      }
      for (const [reason, count] of byReason) {
        console.log(`    ${reason}: ${count}`);
      }
    }

    // Unused locale entries (approximate — see check-i18n limitations above).
    const usedByNs = new Map();
    for (const [, u] of usageByKey) {
      if (!usedByNs.has(u.namespace)) usedByNs.set(u.namespace, new Set());
      usedByNs.get(u.namespace).add(u.key);
    }
    const unusedByNs = [];
    for (const [ns, obj] of Object.entries(en.parsed)) {
      if (typeof obj !== "object" || Array.isArray(obj)) continue;
      const implemented = new Set(Object.keys(obj));
      const used = usedByNs.get(ns) ?? new Set();
      const unused = [...implemented].filter((k) => !used.has(k));
      if (unused.length > 0) unusedByNs.push({ ns, unused });
    }
    if (unusedByNs.length > 0) {
      const total = unusedByNs.reduce((s, e) => s + e.unused.length, 0);
      console.log(
        `\n⚠ Unused locale entry candidates (approximate, not verified — do not delete without checking): ${total} across ${unusedByNs.length} namespaces`,
      );
      console.log("    Run with full output (omit --quiet) is already default; see per-namespace breakdown below.");
      for (const { ns, unused } of unusedByNs) {
        console.log(`    ${ns} (${unused.length}): ${unused.slice(0, 12).join(", ")}${unused.length > 12 ? ", …" : ""}`);
      }
    }

    // Duplicate values within a namespace (possible copy-paste / redundant key).
    const dupValueFindings = [];
    for (const [ns, obj] of Object.entries(en.parsed)) {
      if (typeof obj !== "object" || Array.isArray(obj)) continue;
      const byValue = new Map();
      for (const [k, v] of Object.entries(obj)) {
        if (typeof v !== "string" || v.length < 4) continue; // skip trivial short strings
        if (!byValue.has(v)) byValue.set(v, []);
        byValue.get(v).push(k);
      }
      for (const [value, keys] of byValue) {
        if (keys.length > 1) dupValueFindings.push({ ns, value, keys });
      }
    }
    if (dupValueFindings.length > 0) {
      console.log(`\n⚠ Duplicate values within a namespace (informational): ${dupValueFindings.length}`);
      for (const f of dupValueFindings.slice(0, 20)) {
        console.log(`    ${f.ns}: [${f.keys.join(", ")}] all = "${f.value}"`);
      }
    }

    // Namespace inconsistency: same key name, different value, across namespaces.
    const keyToNsValues = new Map();
    for (const [ns, obj] of Object.entries(en.parsed)) {
      if (typeof obj !== "object" || Array.isArray(obj)) continue;
      for (const [k, v] of Object.entries(obj)) {
        if (typeof v !== "string") continue;
        if (!keyToNsValues.has(k)) keyToNsValues.set(k, new Map());
        keyToNsValues.get(k).set(ns, v);
      }
    }
    const inconsistent = [];
    for (const [k, nsValues] of keyToNsValues) {
      if (nsValues.size < 2) continue;
      const distinctValues = new Set(nsValues.values());
      if (distinctValues.size > 1) inconsistent.push({ key: k, nsValues: [...nsValues.entries()] });
    }
    if (inconsistent.length > 0) {
      console.log(`\n⚠ Same key name, different value across namespaces (informational, high false-positive rate): ${inconsistent.length}`);
      for (const f of inconsistent.slice(0, 20)) {
        console.log(`    "${f.key}": ${f.nsValues.map(([ns, v]) => `${ns}="${v}"`).join(", ")}`);
      }
    }
  }

  console.log("\n" + (hardFail ? "FAIL" : "PASS"));
  process.exit(hardFail ? 1 : 0);
}

main();
