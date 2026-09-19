/**
 * Single source of truth for user/actor avatar initials.
 *
 * Aturan (konvensi existing repo — dashboard activity & PIC komplain):
 * selalu **tepat 3 huruf**.
 *   - 3 kata atau lebih  → huruf pertama dari 3 kata pertama (Budi Santoso Pratama → BSP)
 *   - 2 kata             → huruf pertama kata-1 + 2 huruf kata-2 (Budi Santoso → BSA);
 *                          bila kata-2 hanya 1 huruf → 2 huruf kata-1 + kata-2 (Ali B → ALB)
 *   - 1 kata             → 3 huruf pertama (Elena → ELE)
 *
 * Nama kosong/null tidak menghasilkan initials; pemanggil yang menentukan
 * placeholder-nya (mis. "?" atau "U").
 */
export function nameInitials(name: string | null | undefined): string | null {
  const value = (name ?? "").trim();
  if (!value) return null;

  const parts = value.split(/\s+/).filter(Boolean);
  let code = "";

  if (parts.length >= 3) {
    code = `${parts[0][0] ?? ""}${parts[1][0] ?? ""}${parts[2][0] ?? ""}`;
  } else if (parts.length === 2) {
    const first = parts[0] ?? "";
    const last = parts[1] ?? "";
    code =
      last.length >= 2
        ? `${first[0] ?? ""}${last.slice(0, 2)}`
        : `${first.slice(0, 2)}${last[0] ?? ""}`;
  } else {
    code = lettersOnly(parts[0] ?? "");
  }

  code = code.slice(0, 3).toUpperCase();

  // Nama pendek (mis. "Bo Ng") bisa menyisakan kurang dari 3 huruf —
  // ambil sisa huruf dari nama utuh agar tetap 3 huruf bila tersedia.
  if (code.length < 3) {
    code = lettersOnly(value).slice(0, 3).toUpperCase();
  }

  return code || null;
}

function lettersOnly(value: string): string {
  return [...value].filter((ch) => /\p{L}|\p{N}/u.test(ch)).join("");
}

/**
 * Kandidat kode 3 huruf untuk satu nama, urut dari yang paling alami:
 * `Budi Santoso` → BSA, lalu BSN, BST, BSO… (huruf berikutnya dari nama itu
 * sendiri), lalu BSA…BSZ sebagai jaring pengaman.
 */
function* initialsCandidates(name: string): Generator<string> {
  const natural = nameInitials(name);
  if (!natural) return;
  yield natural;

  const prefix = natural.slice(0, 2);
  if (prefix.length < 2) return;

  // Huruf lanjutan dari nama belakang lebih dulu — BSA → BSN → BST → BSO.
  const parts = name.trim().split(/\s+/).filter(Boolean);
  const lastWord = lettersOnly(parts[parts.length - 1] ?? "").toUpperCase();
  for (const ch of lastWord.slice(1)) {
    yield `${prefix}${ch}`;
  }
  for (const ch of lettersOnly(name).toUpperCase()) {
    yield `${prefix}${ch}`;
  }
  for (let code = 65; code <= 90; code += 1) {
    yield `${prefix}${String.fromCharCode(code)}`;
  }
}

/**
 * Pembeda untuk orang berbeda yang menghasilkan inisial sama (mis. dua
 * `Budi Santoso`, atau `Budi Santoso` vs `Bagus Sanjaya` yang sama-sama BSA).
 *
 * `key` harus identitas unik user (user id / username). Orang pertama —
 * berdasarkan urutan key, bukan urutan render — mempertahankan kode alaminya;
 * yang berikutnya turun ke kandidat bebas pertama. Hasil selalu 3 huruf dan
 * stabil selama himpunan orangnya sama.
 */
export function disambiguateInitials(
  entries: ReadonlyArray<{ key: string; name?: string | null }>,
): Map<string, string> {
  const byKey = new Map<string, string>();
  for (const entry of entries) {
    if (!byKey.has(entry.key)) byKey.set(entry.key, (entry.name ?? "").trim());
  }

  // Kelompokkan per kode alami; hanya kelompok >1 yang perlu dibedakan.
  const groups = new Map<string, string[]>();
  for (const [key, name] of byKey) {
    const natural = nameInitials(name);
    if (!natural) continue;
    const group = groups.get(natural);
    if (group) group.push(key);
    else groups.set(natural, [key]);
  }

  const taken = new Set<string>();
  const resolved = new Map<string, string>();
  for (const keys of groups.values()) {
    for (const key of [...keys].sort()) {
      const name = byKey.get(key) ?? "";
      let assigned: string | null = null;
      for (const candidate of initialsCandidates(name)) {
        if (taken.has(candidate)) continue;
        assigned = candidate;
        break;
      }
      // Semua kandidat terpakai (>27 orang berkode sama) — pakai kode alami.
      assigned ??= nameInitials(name);
      if (!assigned) continue;
      taken.add(assigned);
      resolved.set(key, assigned);
    }
  }
  return resolved;
}
