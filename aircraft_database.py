# aircraft_database.py
# Phase 1 - Part A: Aircraft Performance Database
# All weights in KG, ranges in NM, fuel burn in KG/HOUR

AIRCRAFT_DATABASE = {

    # ── BOEING ──────────────────────────────────────────────────────────────
    "B737-800": {
        "full_name":        "Boeing 737-800",
        "manufacturer":     "Boeing",
        "mtow_kg":          79_016,
        "mlw_kg":           65_317,
        "max_fuel_kg":      20_894,
        "fuel_burn_kgh":    2_600,   # cruise fuel burn per hour
        "typical_cruise_ktas": 454,  # knots true airspeed
        "range_nm":         3_115,
        "etops_minutes":    None,    # not ETOPS rated by default
        "pax_typical":      162,
    },
    "B737-MAX8": {
        "full_name":        "Boeing 737 MAX 8",
        "manufacturer":     "Boeing",
        "mtow_kg":          82_191,
        "mlw_kg":           66_360,
        "max_fuel_kg":      20_894,
        "fuel_burn_kgh":    2_400,
        "typical_cruise_ktas": 453,
        "range_nm":         3_550,
        "etops_minutes":    180,
        "pax_typical":      162,
    },
    "B747-400": {
        "full_name":        "Boeing 747-400",
        "manufacturer":     "Boeing",
        "mtow_kg":          412_775,
        "mlw_kg":           295_742,
        "max_fuel_kg":      173_074,
        "fuel_burn_kgh":    11_000,
        "typical_cruise_ktas": 490,
        "range_nm":         8_355,
        "etops_minutes":    180,
        "pax_typical":      416,
    },
    "B777-300ER": {
        "full_name":        "Boeing 777-300ER",
        "manufacturer":     "Boeing",
        "mtow_kg":          352_400,
        "mlw_kg":           251_290,
        "max_fuel_kg":      181_283,
        "fuel_burn_kgh":    8_600,
        "typical_cruise_ktas": 490,
        "range_nm":         7_370,
        "etops_minutes":    180,
        "pax_typical":      396,
    },
    "B777-200LR": {
        "full_name":        "Boeing 777-200LR",
        "manufacturer":     "Boeing",
        "mtow_kg":          347_452,
        "mlw_kg":           223_168,
        "max_fuel_kg":      202_285,
        "fuel_burn_kgh":    7_800,
        "typical_cruise_ktas": 490,
        "range_nm":         9_395,
        "etops_minutes":    180,
        "pax_typical":      301,
    },
    "B787-8": {
        "full_name":        "Boeing 787-8 Dreamliner",
        "manufacturer":     "Boeing",
        "mtow_kg":          227_930,
        "mlw_kg":           172_365,
        "max_fuel_kg":      101_323,
        "fuel_burn_kgh":    5_500,
        "typical_cruise_ktas": 488,
        "range_nm":         7_355,
        "etops_minutes":    180,
        "pax_typical":      242,
    },
    "B787-9": {
        "full_name":        "Boeing 787-9 Dreamliner",
        "manufacturer":     "Boeing",
        "mtow_kg":          254_011,
        "mlw_kg":           192_777,
        "max_fuel_kg":      126_917,
        "fuel_burn_kgh":    6_000,
        "typical_cruise_ktas": 488,
        "range_nm":         7_635,
        "etops_minutes":    180,
        "pax_typical":      296,
    },

    # ── AIRBUS ───────────────────────────────────────────────────────────────
    "A320": {
        "full_name":        "Airbus A320-200",
        "manufacturer":     "Airbus",
        "mtow_kg":          77_000,
        "mlw_kg":           64_500,
        "max_fuel_kg":      18_728,
        "fuel_burn_kgh":    2_500,
        "typical_cruise_ktas": 450,
        "range_nm":         3_300,
        "etops_minutes":    None,
        "pax_typical":      150,
    },
    "A320NEO": {
        "full_name":        "Airbus A320neo",
        "manufacturer":     "Airbus",
        "mtow_kg":          79_000,
        "mlw_kg":           67_400,
        "max_fuel_kg":      18_728,
        "fuel_burn_kgh":    2_200,
        "typical_cruise_ktas": 450,
        "range_nm":         3_400,
        "etops_minutes":    180,
        "pax_typical":      150,
    },
    "A321NEO": {
        "full_name":        "Airbus A321neo",
        "manufacturer":     "Airbus",
        "mtow_kg":          97_000,
        "mlw_kg":           79_200,
        "max_fuel_kg":      26_730,
        "fuel_burn_kgh":    2_800,
        "typical_cruise_ktas": 450,
        "range_nm":         4_000,
        "etops_minutes":    180,
        "pax_typical":      180,
    },
    "A330-300": {
        "full_name":        "Airbus A330-300",
        "manufacturer":     "Airbus",
        "mtow_kg":          242_000,
        "mlw_kg":           185_000,
        "max_fuel_kg":      97_530,
        "fuel_burn_kgh":    6_800,
        "typical_cruise_ktas": 472,
        "range_nm":         6_350,
        "etops_minutes":    180,
        "pax_typical":      277,
    },
    "A350-900": {
        "full_name":        "Airbus A350-900",
        "manufacturer":     "Airbus",
        "mtow_kg":          280_000,
        "mlw_kg":           205_000,
        "max_fuel_kg":      141_000,
        "fuel_burn_kgh":    6_300,
        "typical_cruise_ktas": 488,
        "range_nm":         8_100,
        "etops_minutes":    180,
        "pax_typical":      325,
    },
    "A380-800": {
        "full_name":        "Airbus A380-800",
        "manufacturer":     "Airbus",
        "mtow_kg":          575_000,
        "mlw_kg":           394_000,
        "max_fuel_kg":      254_000,
        "fuel_burn_kgh":    13_000,
        "typical_cruise_ktas": 488,
        "range_nm":         8_200,
        "etops_minutes":    None,  # 4-engine, ETOPS not required
        "pax_typical":      555,
    },

    # ── EMBRAER ──────────────────────────────────────────────────────────────
    "E190": {
        "full_name":        "Embraer E190",
        "manufacturer":     "Embraer",
        "mtow_kg":          47_790,
        "mlw_kg":           43_000,
        "max_fuel_kg":      13_986,
        "fuel_burn_kgh":    2_100,
        "typical_cruise_ktas": 447,
        "range_nm":         2_450,
        "etops_minutes":    None,
        "pax_typical":      98,
    },
}

# ── ALIAS LOOKUP ─────────────────────────────────────────────────────────────
# Maps common pilot shorthand / ICAO codes to database keys
AIRCRAFT_ALIASES = {
    # Boeing
    "737":         "B737-800",
    "738":         "B737-800",
    "B738":        "B737-800",
    "737-800":     "B737-800",
    "737MAX":      "B737-MAX8",
    "737 MAX":     "B737-MAX8",
    "7M8":         "B737-MAX8",
    "744":         "B747-400",
    "B744":        "B747-400",
    "747":         "B747-400",
    "747-400":     "B747-400",
    "773":         "B777-300ER",
    "B773":        "B777-300ER",
    "777":         "B777-300ER",
    "777-300ER":   "B777-300ER",
    "77L":         "B777-200LR",
    "777-200LR":   "B777-200LR",
    "787":         "B787-9",
    "788":         "B787-8",
    "B788":        "B787-8",
    "789":         "B787-9",
    "B789":        "B787-9",
    "787-8":       "B787-8",
    "787-9":       "B787-9",
    "DREAMLINER":  "B787-9",
    # Airbus
    "320":         "A320",
    "A320":        "A320",
    "320NEO":      "A320NEO",
    "A320NEO":     "A320NEO",
    "321NEO":      "A321NEO",
    "A321NEO":     "A321NEO",
    "333":         "A330-300",
    "A333":        "A330-300",
    "330":         "A330-300",
    "A330":        "A330-300",
    "359":         "A350-900",
    "A359":        "A350-900",
    "350":         "A350-900",
    "A350":        "A350-900",
    "388":         "A380-800",
    "A388":        "A380-800",
    "380":         "A380-800",
    "A380":        "A380-800",
    # Embraer
    "E190":        "E190",
    "190":         "E190",
}


def lookup_aircraft(query: str) -> dict | None:
    """
    Look up aircraft data by type code, alias, or partial name.
    Returns the aircraft data dict, or None if not found.

    Examples:
        lookup_aircraft("B777-300ER")
        lookup_aircraft("777")
        lookup_aircraft("a380")
    """
    query_upper = query.strip().upper().replace("-", "").replace(" ", "")

    # 1. Direct key match
    for key in AIRCRAFT_DATABASE:
        if key.replace("-", "").upper() == query_upper:
            return {"code": key, **AIRCRAFT_DATABASE[key]}

    # 2. Alias match
    for alias in AIRCRAFT_ALIASES:
        if alias.replace("-", "").replace(" ", "").upper() == query_upper:
            code = AIRCRAFT_ALIASES[alias]
            return {"code": code, **AIRCRAFT_DATABASE[code]}

    # 3. Partial name match (e.g. "dreamliner", "777")
    for key, data in AIRCRAFT_DATABASE.items():
        if query_upper in data["full_name"].upper().replace(" ", "").replace("-", ""):
            return {"code": key, **data}

    return None  # not found


def list_all_aircraft() -> None:
    """Print a summary table of all aircraft in the database."""
    print(f"\n{'CODE':<12} {'FULL NAME':<30} {'MTOW (kg)':<12} {'MLW (kg)':<12} {'ETOPS'}")
    print("─" * 80)
    for code, data in AIRCRAFT_DATABASE.items():
        etops = f"{data['etops_minutes']} min" if data["etops_minutes"] else "N/A"
        print(f"{code:<12} {data['full_name']:<30} {data['mtow_kg']:<12,} {data['mlw_kg']:<12,} {etops}")
    print()


# ── QUICK TEST ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AIRCRAFT DATABASE — Phase 1 Part A")
    print("=" * 60)

    # Show all aircraft
    list_all_aircraft()

    # Test lookups
    test_queries = ["777", "A380", "B788", "dreamliner", "A320NEO", "XYZ999"]
    print("LOOKUP TESTS:")
    print("─" * 40)
    for q in test_queries:
        result = lookup_aircraft(q)
        if result:
            print(f"  '{q}' → {result['full_name']} | MTOW: {result['mtow_kg']:,} kg | MLW: {result['mlw_kg']:,} kg")
        else:
            print(f"  '{q}' → ❌ Not found in database")
    print()
