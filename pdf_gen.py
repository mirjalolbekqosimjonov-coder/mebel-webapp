import os
from io import BytesIO
from datetime import datetime, timedelta
from fpdf import FPDF

LOGO1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pics", "LOGO1.png")

BLUE       = (26, 82, 118)
LIGHT_BLUE = (232, 240, 250)
GREEN      = (39, 174, 96)
RED        = (231, 76, 60)


def _fmt(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", " ")


def _s(text) -> str:
    """Latin-1 safe string — replaces unmappable chars."""
    if text is None:
        return ""
    return str(text).encode("latin-1", errors="replace").decode("latin-1")


class _PDF(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 5, "UMEBEL - Ishonch bilan yaratilgan!", align="C")
        self.set_text_color(0, 0, 0)


# ── Buyurtma varog'i ──────────────────────────────────────────────────────────

def make_order_pdf(data: dict, order_id: int, customer: str, settings: dict) -> BytesIO:
    pdf = _PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_margins(14, 14, 14)

    now = (datetime.utcnow() + timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")

    # ── Header ──
    if os.path.exists(LOGO1):
        pdf.image(LOGO1, x=14, y=9, w=82)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(120, 120, 120)
    pdf.set_xy(140, 11)
    pdf.cell(56, 5, f"Buyurtma #: {order_id}", align="R")
    pdf.set_xy(140, 16)
    pdf.cell(56, 5, f"Sana: {now}", align="R")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(32)

    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(0.4)
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(5)

    # ── Title ──
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 9, "BUYURTMA VAROG'I", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(11)

    # ── Mijoz ──
    pdf.set_fill_color(*LIGHT_BLUE)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, f"  Mijoz: {_s(customer)}", fill=True)
    pdf.ln(11)

    # ── Mebel ma'lumotlari ──
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 7, "Mebel ma'lumotlari")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    details = [
        ("Mebel turi", _s(data.get("furniture", ""))),
        ("Material",   _s(data.get("material", ""))),
    ]
    w, h, d = data.get("width"), data.get("height"), data.get("depth")
    if w and h and d:
        details.append(("O'lchamlar (sm)", f"{int(w)} x {int(h)} x {int(d)}"))
    extra = data.get("extra", "")
    if extra:
        details.append(("Qo'shimcha", _s(extra)[:80]))

    for label, value in details:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(55, 6, _s(label) + ":", border="B")
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 6, value, border="B")
        pdf.ln(8)

    pdf.ln(4)

    # ── Materiallar jadvali ──
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 7, "Materiallar ro'yxati")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    CW = [88, 28, 38, 28]  # 182 total
    ALIGNS = ["L", "C", "R", "R"]

    def _row(cols, bold=False, fill_color=None, text_color=None):
        if fill_color:
            pdf.set_fill_color(*fill_color)
        if text_color:
            pdf.set_text_color(*text_color)
        pdf.set_font("Helvetica", "B" if bold else "", 9)
        for txt, w_col, aln in zip(cols, CW, ALIGNS):
            pdf.cell(w_col, 6, _s(txt), border=1,
                     fill=bool(fill_color), align=aln)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)

    _row(["Material", "Miqdor", "Birlik narx", "Jami"],
         bold=True, fill_color=BLUE, text_color=(255, 255, 255))

    mat       = data.get("material", "LDSP")
    body_area = data.get("body_area", 0) or 0
    xdf_area  = data.get("xdf_area", 0) or 0
    edge_m    = data.get("edge_m", 0) or 0
    hinges    = data.get("hinges", 0) or 0
    handles   = data.get("handles", 0) or 0
    screw_sets= data.get("screw_sets", 0) or 0

    trows = []
    if body_area > 0:
        key = "ldsp_cost" if mat == "LDSP" else "mdf_cost"
        up = settings.get(key, 0)
        trows.append([f"{mat} panel", f"{body_area:.3f} m2",
                      f"{_fmt(up)} so'm/m2", f"{_fmt(body_area * up)} so'm"])
    if xdf_area > 0:
        up = settings.get("xdf_cost", 0)
        trows.append(["XDF orqa panel", f"{xdf_area:.3f} m2",
                      f"{_fmt(up)} so'm/m2", f"{_fmt(xdf_area * up)} so'm"])
    if edge_m > 0:
        up = settings.get("edge_cost", 0)
        trows.append(["Qirra lenta", f"{edge_m:.1f} m",
                      f"{_fmt(up)} so'm/m", f"{_fmt(edge_m * up)} so'm"])
    if hinges > 0:
        up = settings.get("hinge_cost", 0)
        trows.append(["Petlyalar", f"{int(hinges)} dona",
                      f"{_fmt(up)} so'm/dona", f"{_fmt(hinges * up)} so'm"])
    if handles > 0:
        up = settings.get("handle_cost", 0)
        trows.append(["Tutqichlar", f"{int(handles)} dona",
                      f"{_fmt(up)} so'm/dona", f"{_fmt(handles * up)} so'm"])
    if screw_sets > 0:
        up = settings.get("screw_cost", 0)
        trows.append(["Vintlar to'plami", f"{int(screw_sets)} ta",
                      f"{_fmt(up)} so'm", f"{_fmt(screw_sets * up)} so'm"])

    for i, r in enumerate(trows):
        fc = LIGHT_BLUE if i % 2 == 0 else (255, 255, 255)
        _row(r, fill_color=fc)

    # ── Jami ──
    pdf.ln(5)
    mat_cost   = data.get("mat_cost", 0) or 0
    sell_price = data.get("sell_price", 0) or 0
    profit     = data.get("profit", 0) or 0
    profit_pct = data.get("profit_pct", 0) or 0

    def _total_row(label, value, color=None):
        pdf.set_fill_color(*LIGHT_BLUE)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(118, 7, "")
        pdf.cell(42, 7, _s(label), fill=True, align="L")
        if color:
            pdf.set_text_color(*color)
        pdf.cell(22, 7, _s(value), fill=True, align="R")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(8)

    _total_row("Material xarajati:", f"{_fmt(mat_cost)} so'm")
    _total_row("Sotish narxi:",      f"{_fmt(sell_price)} so'm")
    _total_row(
        f"Foyda ({profit_pct:.1f}%):",
        f"{_fmt(profit)} so'm",
        color=GREEN if profit >= 0 else RED,
    )

    return BytesIO(pdf.output())


# ── Admin hisobotlar PDF ───────────────────────────────────────────────────────

def make_report_pdf(rows: list) -> BytesIO:
    pdf = _PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page("L")           # Landscape A4
    pdf.set_margins(10, 10, 10)

    now = (datetime.utcnow() + timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")

    # ── Header ──
    if os.path.exists(LOGO1):
        pdf.image(LOGO1, x=10, y=8, w=72)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(120, 120, 120)
    pdf.set_xy(220, 10)
    pdf.cell(67, 5, f"Hisobot: {now}", align="R")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(28)

    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(0.4)
    pdf.line(10, pdf.get_y(), 287, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 8, "HISOBOTLAR JADVALI", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # Landscape A4 = 297mm, margins 10+10 = 277mm usable
    CW = [10, 22, 35, 42, 18, 15, 15, 15, 33, 33, 27]
    HDR = ["#", "Sana", "Foydalanuvchi", "Mebel", "Material",
           "Ken.", "Bal.", "Chu.", "Mat.xarajat", "Sotish narxi", "Foyda"]

    pdf.set_fill_color(*BLUE)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 7)
    for txt, w in zip(HDR, CW):
        pdf.cell(w, 6, txt, border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Helvetica", size=7)
    for i, row in enumerate(rows):
        fc = LIGHT_BLUE if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*fc)
        vals = [
            str(row[0]),
            _s(row[1][:10]) if row[1] else "",
            _s((row[3] or "")[:18]),
            _s((row[4] or "")[:22]),
            _s((row[5] or "")[:10]),
            f"{row[6]:.0f}" if row[6] else "",
            f"{row[7]:.0f}" if row[7] else "",
            f"{row[8]:.0f}" if row[8] else "",
            f"{_fmt(row[16])} s'm" if row[16] else "",
            f"{_fmt(row[17])} s'm" if row[17] else "",
            f"{_fmt(row[18])} s'm" if row[18] else "",
        ]
        for txt, w in zip(vals, CW):
            pdf.cell(w, 5, txt, border=1, fill=True, align="C")
        pdf.ln()

    # ── Jami qator ──
    if rows:
        pdf.ln(4)
        total_mat    = sum(r[16] or 0 for r in rows)
        total_sell   = sum(r[17] or 0 for r in rows)
        total_profit = sum(r[18] or 0 for r in rows)

        pdf.set_fill_color(*LIGHT_BLUE)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(157, 7, f"  Jami: {len(rows)} ta buyurtma", fill=True)
        pdf.cell(33, 7, f"{_fmt(total_mat)} so'm",    fill=True, align="R")
        pdf.cell(33, 7, f"{_fmt(total_sell)} so'm",   fill=True, align="R")
        clr = GREEN if total_profit >= 0 else RED
        pdf.set_text_color(*clr)
        pdf.cell(27, 7, f"{_fmt(total_profit)} so'm", fill=True, align="R")
        pdf.set_text_color(0, 0, 0)

    return BytesIO(pdf.output())
