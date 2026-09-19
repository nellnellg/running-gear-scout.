#!/usr/bin/env python3
"""Running Gear Scout — a single-file CLI that recommends running shoes.

Inputs: a runner's weekly mileage, run types, foot type, surface, budget,
cushion/drop preferences, and their current rotation (shoe + miles on it).
Output: up to three personalized recommendations with price, the reason each
one fits, and how it slots into the existing rotation.

Run a demo:      python3 scout.py
Interactive:     python3 scout.py --interactive
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Catalog
# --------------------------------------------------------------------------
# durability_miles is the expected usable life of a pair before the midsole dies.
# category is one of: daily, tempo, race, recovery, trail.
# stability shoes are for overpronators; everything else is "neutral".
# surface is "road" or "trail".

CATALOG = [
    # name, brand, category, price, weight_oz, drop_mm, stack_mm, durability_mi, stability, surface, cushion
    ("Brooks Ghost 16",              "Brooks",      "daily",    140, 10.1, 12, 35, 450, False, "road", "balanced"),
    ("New Balance Fresh Foam 1080 v13","New Balance","daily",   165,  9.2,  6, 34, 500, False, "road", "plush"),
    ("ASICS Novablast 5",            "ASICS",       "daily",    140,  9.2,  8, 40, 400, False, "road", "bouncy"),
    ("Nike Pegasus 41",              "Nike",        "daily",    140,  9.8, 10, 33, 450, False, "road", "balanced"),
    ("Saucony Ride 17",              "Saucony",     "daily",    140,  9.7,  8, 35, 450, False, "road", "balanced"),
    ("Hoka Clifton 9",               "Hoka",        "daily",    145,  8.7,  5, 32, 400, False, "road", "plush"),
    ("Adidas Supernova Rise",        "Adidas",      "daily",    140,  9.5, 10, 32, 400, False, "road", "balanced"),
    ("Mizuno Wave Rider 28",         "Mizuno",      "daily",    145,  9.8, 12, 36, 450, False, "road", "balanced"),

    ("Saucony Endorphin Speed 4",    "Saucony",     "tempo",    170,  8.2,  8, 36, 350, False, "road", "bouncy"),
    ("Puma Deviate Nitro 3",         "Puma",        "tempo",    160,  9.2, 10, 36, 350, False, "road", "bouncy"),
    ("New Balance FuelCell Rebel v4","New Balance", "tempo",    140,  7.4,  6, 30, 350, False, "road", "bouncy"),
    ("ASICS Magic Speed 4",          "ASICS",       "tempo",    170,  8.3,  7, 37, 300, False, "road", "firm"),
    ("Adidas Adizero Boston 12",     "Adidas",      "tempo",    160,  8.9,  7, 37, 400, False, "road", "firm"),
    ("Brooks Launch GTS 10",         "Brooks",      "tempo",    120,  8.7, 10, 28, 350, True,  "road", "firm"),

    ("Nike Vaporfly 3",              "Nike",        "race",     260,  6.9,  8, 40, 200, False, "road", "bouncy"),
    ("ASICS Metaspeed Sky Paris",    "ASICS",       "race",     250,  6.6,  5, 40, 250, False, "road", "bouncy"),
    ("Saucony Endorphin Pro 4",      "Saucony",     "race",     225,  7.5,  8, 40, 250, False, "road", "bouncy"),
    ("Adidas Adizero Adios Pro 3",   "Adidas",      "race",     250,  7.5,  6, 40, 250, False, "road", "bouncy"),
    ("Hoka Cielo X1",                "Hoka",        "race",     275,  7.9,  7, 40, 250, False, "road", "bouncy"),

    ("Brooks Glycerin 21",           "Brooks",      "recovery", 160, 10.1, 10, 38, 450, False, "road", "plush"),
    ("New Balance Fresh Foam More v5","New Balance","recovery", 160, 10.5,  4, 34, 450, False, "road", "plush"),
    ("ASICS Gel-Nimbus 26",          "ASICS",       "recovery", 160, 10.4,  8, 40, 500, False, "road", "plush"),
    ("Hoka Bondi 8",                 "Hoka",        "recovery", 165, 10.8,  4, 33, 450, False, "road", "plush"),
    ("Saucony Triumph 22",           "Saucony",     "recovery", 160, 10.1, 10, 40, 450, False, "road", "plush"),

    ("Hoka Speedgoat 5",             "Hoka",        "trail",    155, 10.3,  4, 32, 450, False, "trail", "balanced"),
    ("Salomon Sense Ride 5",         "Salomon",     "trail",    140, 10.1,  8, 29, 450, False, "trail", "balanced"),
    ("Brooks Cascadia 17",           "Brooks",      "trail",    140, 10.7,  8, 33, 450, False, "trail", "balanced"),
    ("Nike Pegasus Trail 4",         "Nike",        "trail",    140,  9.9, 10, 30, 400, False, "trail", "balanced"),

    ("Brooks Adrenaline GTS 23",     "Brooks",      "daily",    140, 10.2, 12, 35, 450, True,  "road", "balanced"),
    ("ASICS Gel-Kayano 31",          "ASICS",       "daily",    160, 10.2, 10, 40, 450, True,  "road", "balanced"),
    ("Saucony Guide 17",             "Saucony",     "daily",    140,  9.9,  8, 35, 450, True,  "road", "balanced"),
    ("New Balance 860 v14",          "New Balance", "daily",    145,  9.8, 10, 33, 450, True,  "road", "balanced"),
    ("Hoka Arahi 7",                 "Hoka",        "daily",    145,  9.1,  5, 32, 400, True,  "road", "balanced"),
]


@dataclass
class Shoe:
    name: str
    brand: str
    category: str
    price: int
    weight_oz: float
    drop_mm: int
    stack_mm: int
    durability_miles: int
    stability: bool
    surface: str
    cushion: str

    @property
    def label(self) -> str:
        return self.name


# --------------------------------------------------------------------------
# Runner profile
# --------------------------------------------------------------------------
RUN_TYPES = ["easy", "tempo", "intervals", "long", "race", "trail"]
# Which shoe category serves each run type.
TYPE_TO_CATEGORY = {
    "easy": "daily",
    "long": "daily",
    "tempo": "tempo",
    "intervals": "tempo",
    "race": "race",
    "trail": "trail",
}
CATEGORY_LABEL = {
    "daily": "daily trainer",
    "tempo": "tempo / uptempo",
    "race": "race day",
    "recovery": "recovery",
    "trail": "trail",
}
CUSHIONS = ["firm", "balanced", "plush", "bouncy"]


@dataclass
class OwnedShoe:
    shoe: Shoe
    miles: int

    @property
    def wear_pct(self) -> float:
        return 100.0 * self.miles / self.shoe.durability_miles


@dataclass
class Runner:
    weekly_miles: int
    run_types: list[str]
    foot_type: str            # "neutral" or "overpronate"
    surface: str              # "road", "trail", or "both"
    budget: int
    preferred_drop: tuple[int, int] = (4, 12)
    preferred_cushion: str | None = None
    rotation: list[OwnedShoe] = field(default_factory=list)


def parse_catalog() -> dict[str, Shoe]:
    shoes = {}
    for row in CATALOG:
        name, brand, category, price, weight, drop, stack, dur, stab, surf, cushion = row
        shoes[name] = Shoe(name, brand, category, price, weight, drop, stack, dur, stab, surf, cushion)
    return shoes


SHOES = parse_catalog()


def find_shoe(name: str) -> Shoe:
    for key, shoe in SHOES.items():
        if name.lower() in key.lower():
            return shoe
    raise KeyError(f"Unknown shoe: {name}")


# --------------------------------------------------------------------------
# Wear + rotation analysis
# --------------------------------------------------------------------------
WORN_PCT = 85.0  # flag a pair once it is this far through its expected life


def needed_categories(runner: Runner) -> list[str]:
    """Map the runner's run types to shoe categories, most-used-first."""
    order = []
    for run_type in RUN_TYPES:
        if run_type in runner.run_types:
            cat = TYPE_TO_CATEGORY[run_type]
            if cat not in order:
                order.append(cat)
    # Recovery is optional but recommended for anyone doing long or tempo work.
    if "recovery" not in order and any(t in runner.run_types for t in ("long", "tempo", "intervals")):
        order.append("recovery")
    if runner.surface == "trail":
        order.append("trail")
    return order


def analyze_rotation(runner: Runner) -> dict[str, list[dict]]:
    """Group owned shoes by category and flag which slots are worn or missing."""
    owned_by_cat: dict[str, list[OwnedShoe]] = {}
    for owned in runner.rotation:
        owned_by_cat.setdefault(owned.shoe.category, []).append(owned)

    report: dict[str, list[dict]] = {"ok": [], "worn": [], "missing": []}
    for cat in needed_categories(runner):
        if cat not in owned_by_cat:
            report["missing"].append(cat)
            continue
        best = max(owned_by_cat[cat], key=lambda o: o.wear_pct)
        entry = {"category": cat, "shoe": best.shoe, "miles": best.miles, "wear_pct": best.wear_pct}
        report["worn" if best.wear_pct >= WORN_PCT else "ok"].append(entry)
    return report


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------
def score(candidate: Shoe, runner: Runner, cat: str) -> tuple[float, list[str]]:
    """Score a candidate 0-100 for a runner and return the reasons it fits."""
    reasons: list[str] = []
    points = 0.0

    # Hard filters are applied before scoring (see recommend()).

    # Foot type: overpronators need stability; neutral runners prefer neutral.
    if runner.foot_type == "overpronate":
        if candidate.stability:
            points += 20
            reasons.append("stability support for your foot type")
        else:
            return -1.0, []  # neutral shoe is a poor fit; treat as excluded
    else:
        points += 20 if not candidate.stability else 10

    # Surface: a road/trail mismatch is handled as a hard filter.

    # Drop preference.
    low, high = runner.preferred_drop
    if low <= candidate.drop_mm <= high:
        points += 15
    else:
        points += max(0, 15 - 3 * min(abs(candidate.drop_mm - low), abs(candidate.drop_mm - high)))

    # Cushion preference.
    if runner.preferred_cushion and candidate.cushion == runner.preferred_cushion:
        points += 15
        reasons.append(f"{candidate.cushion} cushioning you prefer")

    # Durability matters most for high-mileage daily shoes.
    if cat == "daily" and runner.weekly_miles >= 30:
        if candidate.durability_miles >= 450:
            points += 15
            reasons.append(f"{candidate.durability_miles}-mile durability for your volume")
    elif candidate.durability_miles >= 400:
        points += 10

    # Price: under budget scores, closer to budget is fine but cheaper is better.
    if candidate.price <= runner.budget:
        points += 20 if candidate.price <= 0.75 * runner.budget else 15
        reasons.append(f"${candidate.price} fits your ${runner.budget} budget")
    else:
        return -1.0, []  # over budget is excluded

    # Lighter shoes score better for tempo/race work.
    if cat in ("tempo", "race") and candidate.weight_oz <= 8.5:
        points += 10
        reasons.append(f"{candidate.weight_oz} oz — light enough for speed work")

    return min(points, 100.0), reasons


def recommend(runner: Runner, limit: int = 3) -> list[dict]:
    """Recommend up to `limit` shoes that fill the runner's biggest gap."""
    report = analyze_rotation(runner)

    # Gap priority: worn-out slot first, then a missing slot.
    gaps = [g["category"] for g in report["worn"]]
    gaps += [c for c in report["missing"] if c not in gaps]

    if not gaps:
        return []

    gap = gaps[0]
    owned_names = {o.shoe.name for o in runner.rotation}

    surface_ok = lambda s: runner.surface == "both" or s.surface == runner.surface

    scored = []
    for shoe in SHOES.values():
        if shoe.category != gap:
            continue
        if shoe.name in owned_names:
            continue
        if not surface_ok(shoe):
            continue
        s, reasons = score(shoe, runner, gap)
        if s >= 0:
            scored.append((s, shoe, reasons))

    scored.sort(key=lambda t: -t[0])
    results = []
    for s, shoe, reasons in scored[:limit]:
        results.append({
            "shoe": shoe,
            "score": round(s),
            "category": gap,
            "reasons": reasons,
        })
    return results


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
def render(runner: Runner) -> str:
    lines: list[str] = []
    lines.append("=== RUNNING GEAR SCOUT ===")
    lines.append(f"Weekly mileage: {runner.weekly_miles} mi | Foot type: {runner.foot_type} "
                 f"| Surface: {runner.surface} | Budget: ${runner.budget}")
    lines.append("")

    report = analyze_rotation(runner)
    if not report["ok"] and not report["worn"] and not report["missing"]:
        lines.append("No run types selected — nothing to recommend for.")
        return "\n".join(lines)

    lines.append("Current rotation:")
    for cat in needed_categories(runner):
        owned = [o for o in runner.rotation if o.shoe.category == cat]
        if not owned:
            lines.append(f"  {CATEGORY_LABEL[cat]:<18} (none — gap)")
            continue
        for o in owned:
            status = "OK" if o.wear_pct < WORN_PCT else "WORNOUT"
            lines.append(f"  {CATEGORY_LABEL[cat]:<18} {o.shoe.label:<38} {o.miles:>4} mi "
                         f"({o.wear_pct:>5.1f}% used) {status}")
    lines.append("")

    recs = recommend(runner)
    if not recs:
        lines.append("Your rotation is in good shape — no new shoes needed right now.")
        return "\n".join(lines)

    for i, r in enumerate(recs, 1):
        shoe = r["shoe"]
        lines.append(f"{i}. {shoe.label}  —  ${shoe.price}  (score {r['score']}/100)")
        lines.append(f"   Category: {CATEGORY_LABEL[r['category']]}")
        lines.append(f"   Specs: {shoe.drop_mm}mm drop, {shoe.stack_mm}mm stack, "
                     f"{shoe.weight_oz} oz, ~{shoe.durability_miles} mi lifespan")
        for reason in r["reasons"]:
            lines.append(f"   • {reason}")
        fit = CATEGORY_LABEL[r["category"]]
        lines.append(f"   → Fits your rotation as your {fit}, filling the gap above.")
        lines.append("")

    return "\n".join(lines)


# --------------------------------------------------------------------------
# Interactive input
# --------------------------------------------------------------------------
def prompt(p: str, default=None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    ans = input(f"{p}{suffix}: ").strip()
    return ans if ans else str(default) if default is not None else ""


def prompt_int(p: str, default: int, minimum: int = 0, maximum: int | None = None) -> int:
    """Ask until the user gives a whole number inside the allowed range."""
    while True:
        raw = prompt(p, default)
        try:
            value = int(raw)
        except ValueError:
            print(f"  '{raw}' isn't a whole number — try something like {default}.")
            continue
        if value < minimum or (maximum is not None and value > maximum):
            bound = f"{minimum} to {maximum}" if maximum is not None else f"at least {minimum}"
            print(f"  Please enter a number {bound}.")
            continue
        return value


def prompt_choice(p: str, options: list[str], default: str) -> str:
    """Ask until the user picks one of `options`."""
    while True:
        raw = prompt(f"{p} ({' / '.join(options)})", default).lower()
        if raw in options:
            return raw
        print(f"  Choose one of: {', '.join(options)}")


def build_interactive() -> Runner:
    print("Running Gear Scout — let's build your profile.\n")
    weekly = prompt_int("Average weekly mileage", 30, minimum=1, maximum=200)

    print(f"\nRun types available: {', '.join(RUN_TYPES)}")
    while True:
        raw = prompt("Which do you do (comma-separated)", "easy,long,tempo")
        run_types = [t.strip().lower() for t in raw.split(",") if t.strip()]
        unknown = [t for t in run_types if t not in RUN_TYPES]
        if unknown:
            print(f"  Unknown run type(s): {', '.join(unknown)}")
            continue
        if not run_types:
            print("  Pick at least one run type.")
            continue
        break

    foot = prompt_choice("Foot type", ["neutral", "overpronate"], "neutral")
    surface = prompt_choice("Surface", ["road", "trail", "both"], "road")
    budget = prompt_int("Budget for this purchase ($)", 150, minimum=20, maximum=500)
    drop_low = prompt_int("Preferred drop, low end (mm)", 4, minimum=0, maximum=20)
    drop_high = prompt_int("Preferred drop, high end (mm)", 12, minimum=0, maximum=20)
    if drop_low > drop_high:
        drop_low, drop_high = drop_high, drop_low
    cushion = prompt_choice("Cushion preference (or 'any')", CUSHIONS + ["any"], "any")
    cushion = None if cushion == "any" else cushion

    rotation: list[OwnedShoe] = []
    print("\nCurrent rotation — enter a shoe name and miles. Blank name to finish.")
    while True:
        name = prompt("  Shoe name (blank to finish)", "")
        if not name:
            break
        try:
            shoe = find_shoe(name)
        except KeyError:
            print(f"  Not in catalog — skipping '{name}'")
            continue
        miles = prompt_int("  Miles on it", 0, minimum=0, maximum=5000)
        rotation.append(OwnedShoe(shoe, miles))

    return Runner(weekly, run_types, foot, surface, budget, (drop_low, drop_high), cushion, rotation)


def demo_runner() -> Runner:
    """A realistic demo profile so `python3 scout.py` works out of the box."""
    rotation = [
        OwnedShoe(find_shoe("Ghost 16"), 410),        # daily, 91% worn -> gap
        OwnedShoe(find_shoe("Endorphin Speed 4"), 120),
    ]
    return Runner(
        weekly_miles=40,
        run_types=["easy", "long", "tempo", "intervals", "race"],
        foot_type="neutral",
        surface="road",
        budget=175,
        preferred_drop=(4, 10),
        preferred_cushion="balanced",
        rotation=rotation,
    )


if __name__ == "__main__":
    import sys
    runner = build_interactive() if "--interactive" in sys.argv else demo_runner()
    print(render(runner))
