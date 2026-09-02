"""Stdlib PDF 1.4 (Helvetica) for operator-facing snapshots.

Shared by Case (API-539) and Pengaduan Internal (API-550). Not customer-safe.
Not reporting. Callers never embed attachment bytes.
"""

from __future__ import annotations

_PAGE_W = 595
_PAGE_H = 842
_MARGIN_X = 50
_MARGIN_TOP = 800
_MARGIN_BOTTOM = 48
_BODY_SIZE = 10
_HEAD_SIZE = 13
_TITLE_SIZE = 16
_AGENCY_SIZE = 16
_MASTHEAD_UNIT_SIZE = 11
_SUBJECT_SIZE = 10
_LINE = 13
_WRAP = 92
_RULE_WIDTH = 0.6
_CONTENT_WIDTH = _PAGE_W - 2 * _MARGIN_X
_KV_COLON_GAP = 10
_KV_VALUE_GAP = 8

_UNICODE_ASCII = str.maketrans(
    {
        "\u2014": "-",
        "\u2013": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
)
# Adobe Helvetica-Bold AFM widths for ASCII 32-126 (units / 1000 em).
_HELVETICA_BOLD_ASCII = (
    278, 333, 474, 556, 556, 889, 722, 278, 333, 333, 389, 584, 278, 333, 278,
    278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584,
    584, 611, 975, 722, 667, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611,
    833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333,
    278, 333, 584, 556, 278, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278,
    556, 278, 889, 611, 611, 611, 611, 389, 556, 333, 611, 556, 778, 556, 556,
    500, 389, 280, 389, 584,
)
# Adobe Helvetica AFM widths for ASCII 32-126 (units / 1000 em).
_HELVETICA_ASCII = (
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278,
    278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584,
    584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556,
    833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278,
    278, 278, 469, 556, 333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222,
    500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500,
    500, 334, 260, 334, 584,
)

OPERATOR_PDF_AGENCY = "Unit Pelayanan Pemungutan Pajak Daerah"


def dash(value: str | None) -> str:
    text = (value or "").strip()
    return text if text else "-"


def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


class OperatorPdfDoc:
    def __init__(self, *, footer: str) -> None:
        self._footer = footer
        self._pages: list[list[str]] = [[]]
        self._y = _MARGIN_TOP

    def title(self, text: str) -> None:
        self._ensure(28)
        self._text(text, size=_TITLE_SIZE, bold=True)
        self._y -= 20

    def letterhead_centered(
        self,
        agency: str,
        unit_line: str,
        *,
        subject: str | None = None,
    ) -> None:
        self._ensure(72)
        for line in _wrap_to_width(
            agency, max_pt=_CONTENT_WIDTH, size=_AGENCY_SIZE, bold=True
        ):
            self._text(line, size=_AGENCY_SIZE, bold=True, align="center")
            self._y -= 20
        self._y -= 2
        for line in _wrap_to_width(
            unit_line, max_pt=_CONTENT_WIDTH, size=_MASTHEAD_UNIT_SIZE, bold=True
        ):
            self._text(line, size=_MASTHEAD_UNIT_SIZE, bold=True, align="center")
            self._y -= 15
        topic = (subject or "").strip()
        if topic:
            self._y -= 2
            for line in _wrap_to_width(
                topic, max_pt=_CONTENT_WIDTH, size=_SUBJECT_SIZE, bold=False
            ):
                self._text(line, size=_SUBJECT_SIZE, align="center")
                self._y -= 13

    def rule(self) -> None:
        self._ensure(14)
        self._y -= 4
        y = self._y
        x1 = _MARGIN_X
        x2 = _PAGE_W - _MARGIN_X
        self._pages[-1].append(
            f"{_RULE_WIDTH} w {x1:.2f} {y:.2f} m {x2:.2f} {y:.2f} l S"
        )
        self._y -= 10

    def heading(self, text: str) -> None:
        self._ensure(24)
        self._y -= 4
        self._text(text, size=_HEAD_SIZE, bold=True)
        self._y -= 16

    def muted(self, text: str) -> None:
        for line in _wrap(text, _WRAP):
            self._ensure(_LINE)
            self._text(line, size=9, italic=True)
            self._y -= _LINE

    def kv(self, label: str, value: str | None) -> None:
        self.kv_block([(label, value)])

    def kv_block(self, rows: list[tuple[str, str | None]]) -> None:
        """Identity-style rows: labels left, colons aligned, values in a column."""
        if not rows:
            return
        label_width = max(
            _helvetica_width(label, _BODY_SIZE, bold=False) for label, _ in rows
        )
        colon_x = _MARGIN_X + label_width + _KV_COLON_GAP
        value_x = colon_x + _helvetica_width(":", _BODY_SIZE, bold=False) + _KV_VALUE_GAP
        value_max = max(_CONTENT_WIDTH - (value_x - _MARGIN_X), 80)
        for label, value in rows:
            lines = _wrap_to_width(
                dash(value), max_pt=value_max, size=_BODY_SIZE, bold=False
            )
            self._ensure(_LINE)
            self._text(label, size=_BODY_SIZE, x=_MARGIN_X)
            self._text(":", size=_BODY_SIZE, x=colon_x)
            self._text(lines[0], size=_BODY_SIZE, x=value_x)
            self._y -= _LINE
            for extra in lines[1:]:
                self._ensure(_LINE)
                self._text(extra, size=_BODY_SIZE, x=value_x)
                self._y -= _LINE

    def block(self, label: str, value: str | None) -> None:
        self.para(f"{label}:")
        body = (value or "").strip() or "-"
        for line in _wrap(body, _WRAP):
            self.para(line)

    def pre(self, text: str) -> None:
        for line in _wrap((text or "").replace("\r", ""), _WRAP):
            self._ensure(_LINE)
            self._text(line, size=_BODY_SIZE)
            self._y -= _LINE

    def para(self, text: str, *, indent: float = 0) -> None:
        if indent > 0:
            max_pt = max(_CONTENT_WIDTH - indent, 80)
            for line in _wrap_to_width(
                text, max_pt=max_pt, size=_BODY_SIZE, bold=False
            ):
                self._ensure(_LINE)
                self._text(line, size=_BODY_SIZE, x=_MARGIN_X + indent)
                self._y -= _LINE
            return
        for line in _wrap(text, _WRAP):
            self._ensure(_LINE)
            self._text(line, size=_BODY_SIZE)
            self._y -= _LINE

    def blank(self) -> None:
        self._y -= 8

    def _ensure(self, need: int) -> None:
        if self._y - need < _MARGIN_BOTTOM:
            self._pages.append([])
            self._y = _MARGIN_TOP

    def _text(
        self,
        text: str,
        *,
        size: int,
        bold: bool = False,
        italic: bool = False,
        align: str = "left",
        x: float | None = None,
    ) -> None:
        font = "F2" if bold else "F3" if italic else "F1"
        draw_x = float(_MARGIN_X) if x is None else float(x)
        if align == "center":
            width = _helvetica_width(text, size, bold=bold)
            draw_x = max((_PAGE_W - width) / 2.0, _MARGIN_X / 2.0)
        cmd = (
            f"BT /{font} {size} Tf {draw_x:.2f} {self._y} Td "
            f"({_pdf_escape(text)}) Tj ET"
        )
        self._pages[-1].append(cmd)

    def build(self) -> bytes:
        objects: list[bytes] = []
        font_f1 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
        font_f2 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"
        font_f3 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>"

        page_streams: list[bytes] = []
        for index, commands in enumerate(self._pages, start=1):
            stamp = (
                f"BT /F3 8 Tf {_MARGIN_X} 28 Td "
                f"({_pdf_escape(self._footer)}  |  {index}/{len(self._pages)}) Tj ET"
            )
            content = "\n".join([*commands, stamp]).encode("latin-1", "replace")
            page_streams.append(content)

        fonts_start = 3
        first_page_obj = 6
        kids: list[int] = []
        page_objs: list[tuple[int, bytes]] = []
        for i, stream in enumerate(page_streams):
            page_id = first_page_obj + i * 2
            content_id = page_id + 1
            kids.append(page_id)
            page_dict = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {_PAGE_W} {_PAGE_H}] "
                f"/Contents {content_id} 0 R /Resources << /Font << "
                f"/F1 {fonts_start} 0 R /F2 {fonts_start + 1} 0 R "
                f"/F3 {fonts_start + 2} 0 R >> >> >>"
            ).encode("ascii")
            stream_obj = (
                f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
                + stream
                + b"\nendstream"
            )
            page_objs.append((page_id, page_dict))
            page_objs.append((content_id, stream_obj))

        kids_ref = " ".join(f"{n} 0 R" for n in kids)
        catalog = b"<< /Type /Catalog /Pages 2 0 R >>"
        pages = (
            f"<< /Type /Pages /Kids [{kids_ref}] /Count {len(self._pages)} >>"
        ).encode("ascii")

        objects = [catalog, pages, font_f1, font_f2, font_f3]
        objects.extend(body for _, body in page_objs)
        return _finalize_pdf(objects)


def _helvetica_width(text: str, size: int, *, bold: bool) -> float:
    table = _HELVETICA_BOLD_ASCII if bold else _HELVETICA_ASCII
    total = 0
    for ch in text.translate(_UNICODE_ASCII):
        o = ord(ch)
        if 32 <= o <= 126:
            total += table[o - 32]
        else:
            total += 600
    return total * size / 1000.0


def _wrap_to_width(
    text: str, *, max_pt: float, size: int, bold: bool = True
) -> list[str]:
    raw = (text or "").strip()
    if not raw:
        return [""]
    words = raw.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip() if current else word
        if _helvetica_width(trial, size, bold=bold) <= max_pt:
            current = trial
            continue
        if current:
            lines.append(current)
        current = word
        while (
            _helvetica_width(current, size, bold=bold) > max_pt and len(current) > 1
        ):
            width_now = _helvetica_width(current, size, bold=bold)
            cut = max(1, int(len(current) * max_pt / width_now))
            lines.append(current[:cut])
            current = current[cut:]
    if current:
        lines.append(current)
    return lines or [""]


def _wrap(text: str, width: int) -> list[str]:
    if not text:
        return [""]
    lines: list[str] = []
    for paragraph in text.replace("\r", "").split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for word in paragraph.split(" "):
            piece = word if word else ""
            trial = f"{current} {piece}".strip() if current else piece
            if len(trial) <= width:
                current = trial
                continue
            if current:
                lines.append(current)
            while len(piece) > width:
                lines.append(piece[:width])
                piece = piece[width:]
            current = piece
        lines.append(current)
    return lines or [""]


def _pdf_escape(text: str) -> str:
    out: list[str] = []
    for ch in text.translate(_UNICODE_ASCII):
        o = ord(ch)
        if ch in "\\()":
            out.append(f"\\{ch}")
        elif 32 <= o <= 126:
            out.append(ch)
        elif 128 <= o <= 255:
            out.append(f"\\{o:03o}")
        else:
            out.append("?")
    return "".join(out)


def _finalize_pdf(objects: list[bytes]) -> bytes:
    chunks: list[bytes] = [b"%PDF-1.4\n"]
    offsets = [0]
    cursor = len(chunks[0])
    for i, body in enumerate(objects, start=1):
        header = f"{i} 0 obj\n".encode("ascii")
        block = header + body + b"\nendobj\n"
        offsets.append(cursor)
        chunks.append(block)
        cursor += len(block)
    xref_pos = cursor
    xref = [f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii")]
    for off in offsets[1:]:
        xref.append(f"{off:010d} 00000 n \n".encode("ascii"))
    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode("ascii")
    return b"".join(chunks + xref + [trailer])
