# fuel_calculator.py
# Phase 1 - Part B: Fuel Calculation Engine
# Based on ICAO / airline industry standard fuel planning rules

from aircraft_database import lookup_aircraft


# ── FUEL PLANNING CONSTANTS ───────────────────────────────────────────────────
CONTINGENCY_PERCENT     = 0.05   # 5% of trip fuel (ICAO standard minimum)
TAXI_FUEL_KG            = 200    # average fuel used during taxi/startup
RESERVE_FUEL_MINUTES    = 30     # final reserve (30 min holding at destination)
ALTERNATE_FUEL_MINUTES  = 45     # fuel to fly to alternate airport if needed


def calculate_flight_time(distance_nm: float, cruise_speed_ktas: float) -> float:
    """
    Calculate estimated flight time in hours.
    distance_nm     : distance in nautical miles
    cruise_speed_ktas: cruise speed in knots true airspeed
    """
    if cruise_speed_ktas <= 0:
        raise ValueError("Cruise speed must be greater than 0.")
    return distance_nm / cruise_speed_ktas


def calculate_fuel(aircraft_code: str, distance_nm: float,
                   headwind_kt: float = 0.0,
                   include_alternate: bool = True) -> dict:
    """
    Calculate full fuel requirements for a flight.

    Parameters:
        aircraft_code    : e.g. "B777-300ER", "777", "A380"
        distance_nm      : flight distance in nautical miles
        headwind_kt      : headwind in knots (negative = tailwind)
        include_alternate: whether to include alternate airport fuel

    Returns a dict with full fuel breakdown and safety checks.
    """

    # ── 1. Look up aircraft ───────────────────────────────────────────────────
    aircraft = lookup_aircraft(aircraft_code)
    if not aircraft:
        return {"error": f"Aircraft '{aircraft_code}' not found in database."}

    # ── 2. Adjust effective cruise speed for wind ─────────────────────────────
    effective_speed = aircraft["typical_cruise_ktas"] - headwind_kt
    if effective_speed <= 0:
        return {"error": "Headwind too strong — effective ground speed is zero or negative."}

    # ── 3. Calculate trip fuel ────────────────────────────────────────────────
    flight_time_hr   = calculate_flight_time(distance_nm, effective_speed)
    trip_fuel_kg     = flight_time_hr * aircraft["fuel_burn_kgh"]

    # ── 4. Contingency fuel (5% of trip fuel) ─────────────────────────────────
    contingency_kg   = trip_fuel_kg * CONTINGENCY_PERCENT

    # ── 5. Alternate fuel (fuel to fly ~200nm to alternate airport) ───────────
    alternate_fuel_kg = 0.0
    if include_alternate:
        alternate_time_hr  = ALTERNATE_FUEL_MINUTES / 60
        alternate_fuel_kg  = alternate_time_hr * aircraft["fuel_burn_kgh"]

    # ── 6. Final reserve fuel (30 min holding) ────────────────────────────────
    reserve_fuel_kg  = (RESERVE_FUEL_MINUTES / 60) * aircraft["fuel_burn_kgh"]

    # ── 7. Taxi fuel ──────────────────────────────────────────────────────────
    taxi_kg          = TAXI_FUEL_KG

    # ── 8. Total fuel required ────────────────────────────────────────────────
    total_fuel_kg    = (trip_fuel_kg + contingency_kg +
                        alternate_fuel_kg + reserve_fuel_kg + taxi_kg)

    # ── 9. Safety checks ──────────────────────────────────────────────────────

    # Check: does fuel fit in tanks?
    fuel_fits_in_tanks = total_fuel_kg <= aircraft["max_fuel_kg"]

    # Check: will aircraft be under MTOW at takeoff?
    # (We estimate Operating Empty Weight as ~50% of MTOW for a rough check)
    estimated_oew_kg   = aircraft["mtow_kg"] * 0.50
    estimated_tow_kg   = estimated_oew_kg + total_fuel_kg  # simplified (no payload)
    under_mtow         = estimated_tow_kg <= aircraft["mtow_kg"]

    # Check: will aircraft be under MLW at landing?
    # Fuel remaining at landing = total - trip fuel - taxi
    fuel_at_landing_kg = total_fuel_kg - trip_fuel_kg - taxi_kg
    estimated_ldw_kg   = estimated_oew_kg + fuel_at_landing_kg
    under_mlw          = estimated_ldw_kg <= aircraft["mlw_kg"]

    # Check: is the flight within aircraft range?
    within_range       = distance_nm <= aircraft["range_nm"]

    # Check: ETOPS warning for overwater flights
    etops_warning = None
    if aircraft["etops_minutes"] is None and distance_nm > 1000:
        etops_warning = (f"⚠️  {aircraft['full_name']} is not ETOPS rated. "
                         f"Overwater flights over ~1,000nm may not be permitted.")

    # ── 10. Build result ──────────────────────────────────────────────────────
    result = {
        # Aircraft info
        "aircraft":              aircraft["full_name"],
        "aircraft_code":         aircraft["code"],

        # Flight info
        "distance_nm":           round(distance_nm, 1),
        "headwind_kt":           headwind_kt,
        "effective_speed_ktas":  round(effective_speed, 1),
        "flight_time_hr":        round(flight_time_hr, 2),
        "flight_time_formatted": _format_time(flight_time_hr),

        # Fuel breakdown (all in kg)
        "trip_fuel_kg":          round(trip_fuel_kg),
        "contingency_fuel_kg":   round(contingency_kg),
        "alternate_fuel_kg":     round(alternate_fuel_kg),
        "reserve_fuel_kg":       round(reserve_fuel_kg),
        "taxi_fuel_kg":          taxi_kg,
        "total_fuel_kg":         round(total_fuel_kg),
        "max_fuel_capacity_kg":  aircraft["max_fuel_kg"],

        # Weight checks
        "mtow_kg":               aircraft["mtow_kg"],
        "mlw_kg":                aircraft["mlw_kg"],
        "fuel_at_landing_kg":    round(fuel_at_landing_kg),

        # Safety flags
        "fuel_fits_in_tanks":    fuel_fits_in_tanks,
        "under_mtow":            under_mtow,
        "under_mlw":             under_mlw,
        "within_range":          within_range,
        "etops_warning":         etops_warning,

        # Overall go / no-go
        "safe_to_fly":           all([fuel_fits_in_tanks, under_mtow,
                                      under_mlw, within_range]),
    }

    return result


def _format_time(hours: float) -> str:
    """Convert decimal hours to HH:MM string."""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m:02d}m"


def print_fuel_report(result: dict) -> None:
    """Print a nicely formatted fuel planning report."""

    if "error" in result:
        print(f"\n❌ ERROR: {result['error']}\n")
        return

    safe_icon = "✅" if result["safe_to_fly"] else "❌"

    print("\n" + "═" * 58)
    print(f"  FUEL PLANNING REPORT  {safe_icon}")
    print("═" * 58)
    print(f"  Aircraft   : {result['aircraft']}")
    print(f"  Distance   : {result['distance_nm']:,.0f} nm")
    if result["headwind_kt"] != 0:
        wind_label = "headwind" if result["headwind_kt"] > 0 else "tailwind"
        print(f"  Wind       : {abs(result['headwind_kt'])} kt {wind_label}")
    print(f"  Est. Speed : {result['effective_speed_ktas']} ktas")
    print(f"  Flight Time: {result['flight_time_formatted']}")
    print("─" * 58)
    print(f"  FUEL BREAKDOWN                              (kg)")
    print("─" * 58)
    print(f"  Trip fuel                        {result['trip_fuel_kg']:>10,}")
    print(f"  Contingency (5%)                 {result['contingency_fuel_kg']:>10,}")
    print(f"  Alternate fuel                   {result['alternate_fuel_kg']:>10,}")
    print(f"  Final reserve (30 min)           {result['reserve_fuel_kg']:>10,}")
    print(f"  Taxi fuel                        {result['taxi_fuel_kg']:>10,}")
    print("─" * 58)
    print(f"  TOTAL FUEL REQUIRED              {result['total_fuel_kg']:>10,}")
    print(f"  Max fuel capacity                {result['max_fuel_capacity_kg']:>10,}")
    print("─" * 58)
    print(f"  WEIGHT CHECKS")
    print("─" * 58)
    print(f"  MTOW                             {result['mtow_kg']:>10,} kg")
    print(f"  MLW                              {result['mlw_kg']:>10,} kg")
    print(f"  Fuel at landing (est.)           {result['fuel_at_landing_kg']:>10,} kg")
    print("─" * 58)
    print(f"  SAFETY CHECKS")
    print("─" * 58)

    checks = [
        ("Fuel fits in tanks",     result["fuel_fits_in_tanks"]),
        ("Under MTOW at takeoff",  result["under_mtow"]),
        ("Under MLW at landing",   result["under_mlw"]),
        ("Within aircraft range",  result["within_range"]),
    ]
    for label, passed in checks:
        icon = "✅" if passed else "❌"
        print(f"  {icon}  {label}")

    if result["etops_warning"]:
        print(f"\n  {result['etops_warning']}")

    print("═" * 58)
    if result["safe_to_fly"]:
        print("  ✅  ALL CHECKS PASSED — SAFE TO PLAN THIS FLIGHT")
    else:
        print("  ❌  ONE OR MORE CHECKS FAILED — REVIEW BEFORE FLIGHT")
    print("═" * 58 + "\n")


# ── QUICK TEST ────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n📋 TEST 1: B777-300ER — Los Angeles (KLAX) to London (EGLL)")
    print("         Distance: ~5,456 nm | 30 kt headwind")
    r1 = calculate_fuel("B777-300ER", distance_nm=5456, headwind_kt=30)
    print_fuel_report(r1)

    print("\n📋 TEST 2: A320 — Short haul, Kuala Lumpur (WMKK) to Singapore (WSSS)")
    print("         Distance: ~175 nm | No wind")
    r2 = calculate_fuel("A320", distance_nm=175, headwind_kt=0)
    print_fuel_report(r2)

    print("\n📋 TEST 3: B737-800 — Long overwater route (ETOPS check)")
    print("         Distance: ~2,500 nm | 20 kt headwind")
    r3 = calculate_fuel("B737-800", distance_nm=2500, headwind_kt=20)
    print_fuel_report(r3)

    print("\n📋 TEST 4: A380 — Sydney (YSSY) to Dallas (KDFW)")
    print("         Distance: ~8,578 nm | 20 kt tailwind")
    r4 = calculate_fuel("A380", distance_nm=8578, headwind_kt=-20)
    print_fuel_report(r4)
