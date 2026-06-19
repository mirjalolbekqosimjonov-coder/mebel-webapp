import math


def fmt(n: float) -> str:
    return f"{int(n):,}".replace(",", " ")


# ── Material hisob-kitob ──────────────────────────────────────────────────────

def calculate_oshxona(w, h, d, material, doors, drawers, s):
    """Oshxona mebeli. w/h/d — sm da."""
    W, H, D = w / 100, h / 100, d / 100

    # Body panellari (LDSP yoki MDF), m²
    sides     = 2 * H * D                          # 2 ta yon panel
    top_bot   = 2 * W * D                          # yuqori + pastki
    n_shelves = math.ceil(H / 0.40)                # har 40sm da 1 javon
    shelves   = n_shelves * W * D
    body_area = sides + top_bot + shelves

    # Orqa panel (XDF), m²
    xdf_area = W * H

    # Qirra lenta, metr
    edge_m = (2 * H) + (2 * W) + (2 * D) + (n_shelves * W)

    hinges     = doors * 2
    handles    = doors + drawers
    screw_sets = 1

    return _build(material, body_area, xdf_area, edge_m,
                  hinges, handles, screw_sets, s)


def calculate_shkaf(w, h, d, material, sections, mirror, s):
    """Shkaf / Kupe. w/h/d — sm da."""
    W, H, D = w / 100, h / 100, d / 100

    sides      = 2 * H * D
    top_bot    = 2 * W * D
    dividers   = (sections - 1) * H * D
    n_shelves  = sections * 2                      # har bo'limda 2 javon
    shelves    = n_shelves * (W / sections) * D
    body_area  = sides + top_bot + dividers + shelves

    xdf_area = W * H

    edge_m = (2 * H + 2 * W + 2 * D
              + (sections - 1) * H
              + n_shelves * (W / sections))

    hinges     = 0   # kupe (slayder)
    handles    = 2
    screw_sets = 1

    r = _build(material, body_area, xdf_area, edge_m,
               hinges, handles, screw_sets, s)

    if mirror:
        mirror_cost = W * H * 25_000   # 25 000 so'm/m²
        r["mirror_cost"] = mirror_cost
        r["mat_cost"]   += mirror_cost
        r["profit"]      = r["sell_price"] - r["mat_cost"]
        r["profit_pct"]  = _pct(r["profit"], r["sell_price"])
    else:
        r["mirror_cost"] = 0

    return r


def calculate_divan(size_key, material, storage, s):
    """Divan / Krovat."""
    DIMS = {
        "90x200":  (0.90, 2.00, 0.45),
        "140x200": (1.40, 2.00, 0.45),
        "160x200": (1.60, 2.00, 0.45),
        "180x200": (1.80, 2.00, 0.45),
    }
    W, L, H = DIMS.get(size_key, (1.40, 2.00, 0.45))

    two_sides = 2 * L * H
    head_foot = 2 * W * H
    base      = W * L
    body_area = two_sides + head_foot + base

    xdf_area = 0
    edge_m   = 2 * (L + W) + 4 * H

    hinges     = 0
    handles    = 2 if storage else 0
    screw_sets = 1

    r = _build(material, body_area, xdf_area, edge_m,
               hinges, handles, screw_sets, s)

    if storage:
        r["storage_cost"] = 80_000
        r["mat_cost"]    += 80_000
        r["profit"]       = r["sell_price"] - r["mat_cost"]
        r["profit_pct"]   = _pct(r["profit"], r["sell_price"])
    else:
        r["storage_cost"] = 0

    return r


def calculate_stol(size_key, chairs, material, s):
    """Stol / Stul."""
    DIMS = {
        "60x120":  (0.60, 1.20),
        "80x160":  (0.80, 1.60),
        "100x200": (1.00, 2.00),
    }
    W, L = DIMS.get(size_key, (0.80, 1.60))

    top_area  = W * L
    leg_area  = 4 * (0.10 * 0.75)   # 4 oyoq: 10sm × 75sm yuzasi (soddalashtirish)
    body_area = top_area + leg_area

    xdf_area = 0
    edge_m   = 2 * (W + L)

    hinges     = 0
    handles    = 0
    screw_sets = 1

    r = _build(material, body_area, xdf_area, edge_m,
               hinges, handles, screw_sets, s)

    chair_cost = int(chairs) * 45_000
    r["chair_cost"] = chair_cost
    r["mat_cost"]  += chair_cost
    r["profit"]     = r["sell_price"] - r["mat_cost"]
    r["profit_pct"] = _pct(r["profit"], r["sell_price"])
    return r


# ── Ichki yordamchi ──────────────────────────────────────────────────────────

def _build(material, body_area, xdf_area, edge_m, hinges, handles, screw_sets, s):
    mat_key  = f"{material.lower()}_cost"
    sell_key = f"{material.lower()}_sell"

    body_cost   = body_area  * s.get(mat_key,   45_000)
    xdf_cost    = xdf_area   * s.get("xdf_cost",12_000)
    edge_cost   = edge_m     * s.get("edge_cost", 2_500)
    hinge_cost  = hinges     * s.get("hinge_cost", 5_000)
    handle_cost = handles    * s.get("handle_cost",8_000)
    screw_cost  = screw_sets * s.get("screw_cost",15_000)

    mat_cost   = body_cost + xdf_cost + edge_cost + hinge_cost + handle_cost + screw_cost
    sell_price = body_area * s.get(sell_key, 130_000)
    profit     = sell_price - mat_cost
    profit_pct = _pct(profit, sell_price)

    return {
        "material":    material,
        "body_area":   body_area,
        "xdf_area":    xdf_area,
        "edge_m":      edge_m,
        "hinges":      hinges,
        "handles":     handles,
        "screw_sets":  screw_sets,
        "body_cost":   body_cost,
        "xdf_cost":    xdf_cost,
        "edge_cost":   edge_cost,
        "hinge_cost":  hinge_cost,
        "handle_cost": handle_cost,
        "screw_cost":  screw_cost,
        "mat_cost":    mat_cost,
        "sell_price":  sell_price,
        "profit":      profit,
        "profit_pct":  profit_pct,
    }


def _pct(profit, sell):
    return (profit / sell * 100) if sell > 0 else 0
