# airport_database.py
# Airport Database with Coordinates and Distance Calculation
# Contains major international airports worldwide

import math

# ── AIRPORT DATABASE ──────────────────────────────────────────────────────────
# Format: ICAO_CODE: {name, city, country, latitude, longitude}

AIRPORTS = {
    # ── NORTH AMERICA ──────────────────────────────────────────────────────────
    "KLAX": {"name": "Los Angeles Intl", "city": "Los Angeles", "country": "USA", "lat": 33.9425, "lon": -118.4081},
    "KJFK": {"name": "John F. Kennedy Intl", "city": "New York", "country": "USA", "lat": 40.6398, "lon": -73.7789},
    "KORD": {"name": "O'Hare Intl", "city": "Chicago", "country": "USA", "lat": 41.9742, "lon": -87.9073},
    "KDFW": {"name": "Dallas/Fort Worth Intl", "city": "Dallas", "country": "USA", "lat": 32.8968, "lon": -97.0380},
    "KSFO": {"name": "San Francisco Intl", "city": "San Francisco", "country": "USA", "lat": 37.6213, "lon": -122.3790},
    "KDEN": {"name": "Denver Intl", "city": "Denver", "country": "USA", "lat": 39.8561, "lon": -104.6737},
    "KATL": {"name": "Hartsfield-Jackson Atlanta Intl", "city": "Atlanta", "country": "USA", "lat": 33.6367, "lon": -84.4281},
    "KMIA": {"name": "Miami Intl", "city": "Miami", "country": "USA", "lat": 25.7932, "lon": -80.2906},
    "KBOS": {"name": "Boston Logan Intl", "city": "Boston", "country": "USA", "lat": 42.3656, "lon": -71.0096},
    "KSEA": {"name": "Seattle-Tacoma Intl", "city": "Seattle", "country": "USA", "lat": 47.4502, "lon": -122.3088},
    "CYVR": {"name": "Vancouver Intl", "city": "Vancouver", "country": "Canada", "lat": 49.1939, "lon": -123.1844},
    "CYYZ": {"name": "Toronto Pearson Intl", "city": "Toronto", "country": "Canada", "lat": 43.6777, "lon": -79.6248},
    "MMMX": {"name": "Mexico City Intl", "city": "Mexico City", "country": "Mexico", "lat": 19.4363, "lon": -99.0721},
    
    # ── EUROPE ─────────────────────────────────────────────────────────────────
    "EGLL": {"name": "London Heathrow", "city": "London", "country": "UK", "lat": 51.4700, "lon": -0.4543},
    "EGKK": {"name": "London Gatwick", "city": "London", "country": "UK", "lat": 51.1537, "lon": -0.1821},
    "LFPG": {"name": "Paris Charles de Gaulle", "city": "Paris", "country": "France", "lat": 49.0097, "lon": 2.5479},
    "EDDF": {"name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "lat": 50.0379, "lon": 8.5622},
    "EHAM": {"name": "Amsterdam Schiphol", "city": "Amsterdam", "country": "Netherlands", "lat": 52.3105, "lon": 4.7683},
    "LEMD": {"name": "Madrid-Barajas", "city": "Madrid", "country": "Spain", "lat": 40.4983, "lon": -3.5676},
    "LIRF": {"name": "Rome Fiumicino", "city": "Rome", "country": "Italy", "lat": 41.8003, "lon": 12.2389},
    "LSZH": {"name": "Zurich Airport", "city": "Zurich", "country": "Switzerland", "lat": 47.4647, "lon": 8.5492},
    "EKCH": {"name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark", "lat": 55.6180, "lon": 12.6560},
    "LOWW": {"name": "Vienna Intl", "city": "Vienna", "country": "Austria", "lat": 48.1103, "lon": 16.5697},
    "UUEE": {"name": "Moscow Sheremetyevo", "city": "Moscow", "country": "Russia", "lat": 55.9726, "lon": 37.4146},
    "LEBL": {"name": "Barcelona-El Prat", "city": "Barcelona", "country": "Spain", "lat": 41.2971, "lon": 2.0785},
    
    # ── MIDDLE EAST ────────────────────────────────────────────────────────────
    "OMDB": {"name": "Dubai Intl", "city": "Dubai", "country": "UAE", "lat": 25.2532, "lon": 55.3657},
    "OTHH": {"name": "Hamad Intl", "city": "Doha", "country": "Qatar", "lat": 25.2731, "lon": 51.6080},
    "OEJN": {"name": "King Abdulaziz Intl", "city": "Jeddah", "country": "Saudi Arabia", "lat": 21.6796, "lon": 39.1565},
    "LTFM": {"name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey", "lat": 41.2753, "lon": 28.7519},
    "LLBG": {"name": "Ben Gurion Airport", "city": "Tel Aviv", "country": "Israel", "lat": 32.0114, "lon": 34.8867},
    
    # ── ASIA ───────────────────────────────────────────────────────────────────
    "RJTT": {"name": "Tokyo Haneda", "city": "Tokyo", "country": "Japan", "lat": 35.5494, "lon": 139.7798},
    "RJBB": {"name": "Osaka Kansai", "city": "Osaka", "country": "Japan", "lat": 34.4347, "lon": 135.2440},
    "RKSI": {"name": "Seoul Incheon", "city": "Seoul", "country": "South Korea", "lat": 37.4602, "lon": 126.4407},
    "VHHH": {"name": "Hong Kong Intl", "city": "Hong Kong", "country": "Hong Kong", "lat": 22.3080, "lon": 113.9185},
    "ZSSS": {"name": "Shanghai Pudong", "city": "Shanghai", "country": "China", "lat": 31.1443, "lon": 121.8083},
    "ZBAA": {"name": "Beijing Capital Intl", "city": "Beijing", "country": "China", "lat": 40.0799, "lon": 116.6031},
    "ZSPD": {"name": "Shanghai Hongqiao", "city": "Shanghai", "country": "China", "lat": 31.1979, "lon": 121.3364},
    "VTBS": {"name": "Bangkok Suvarnabhumi", "city": "Bangkok", "country": "Thailand", "lat": 13.6900, "lon": 100.7501},
    "WSSS": {"name": "Singapore Changi", "city": "Singapore", "country": "Singapore", "lat": 1.3644, "lon": 103.9915},
    "WMKK": {"name": "Kuala Lumpur Intl", "city": "Kuala Lumpur", "country": "Malaysia", "lat": 2.7456, "lon": 101.7099},
    "VABB": {"name": "Mumbai Chhatrapati Shivaji", "city": "Mumbai", "country": "India", "lat": 19.0896, "lon": 72.8656},
    "VIDP": {"name": "Delhi Indira Gandhi Intl", "city": "Delhi", "country": "India", "lat": 28.5665, "lon": 77.1031},
    "RPLL": {"name": "Manila Ninoy Aquino Intl", "city": "Manila", "country": "Philippines", "lat": 14.5086, "lon": 121.0194},
    "WIIH": {"name": "Jakarta Soekarno-Hatta", "city": "Jakarta", "country": "Indonesia", "lat": -6.1256, "lon": 106.6559},
    
    # ── OCEANIA ────────────────────────────────────────────────────────────────
    "YSSY": {"name": "Sydney Kingsford Smith", "city": "Sydney", "country": "Australia", "lat": -33.9461, "lon": 151.1772},
    "YMML": {"name": "Melbourne Airport", "city": "Melbourne", "country": "Australia", "lat": -37.6690, "lon": 144.8410},
    "YBBN": {"name": "Brisbane Airport", "city": "Brisbane", "country": "Australia", "lat": -27.3942, "lon": 153.1218},
    "NZAA": {"name": "Auckland Airport", "city": "Auckland", "country": "New Zealand", "lat": -37.0081, "lon": 174.7850},
    
    # ── SOUTH AMERICA ──────────────────────────────────────────────────────────
    "SBGR": {"name": "São Paulo-Guarulhos Intl", "city": "São Paulo", "country": "Brazil", "lat": -23.4356, "lon": -46.4731},
    "SAEZ": {"name": "Buenos Aires Ezeiza", "city": "Buenos Aires", "country": "Argentina", "lat": -34.8222, "lon": -58.5358},
    "SCEL": {"name": "Santiago Arturo Merino Benítez", "city": "Santiago", "country": "Chile", "lat": -33.3930, "lon": -70.7858},
    "SKBO": {"name": "Bogotá El Dorado Intl", "city": "Bogotá", "country": "Colombia", "lat": 4.7016, "lon": -74.1469},
    "SBGL": {"name": "Rio de Janeiro-Galeão", "city": "Rio de Janeiro", "country": "Brazil", "lat": -22.8099, "lon": -43.2505},
    
    # ── AFRICA ─────────────────────────────────────────────────────────────────
    "FACT": {"name": "Cape Town Intl", "city": "Cape Town", "country": "South Africa", "lat": -33.9715, "lon": 18.6021},
    "FAOR": {"name": "Johannesburg O.R. Tambo", "city": "Johannesburg", "country": "South Africa", "lat": -26.1367, "lon": 28.2411},
    "HECA": {"name": "Cairo Intl", "city": "Cairo", "country": "Egypt", "lat": 30.1219, "lon": 31.4056},
    "HAAB": {"name": "Addis Ababa Bole Intl", "city": "Addis Ababa", "country": "Ethiopia", "lat": 8.9779, "lon": 38.7993},
}

# ── IATA TO ICAO MAPPING ───────────────────────────────────────────────────────
# Allows lookup by common 3-letter IATA codes (e.g., "LAX" → "KLAX")
IATA_TO_ICAO = {
    "LAX": "KLAX", "JFK": "KJFK", "ORD": "KORD", "DFW": "KDFW", "SFO": "KSFO",
    "DEN": "KDEN", "ATL": "KATL", "MIA": "KMIA", "BOS": "KBOS", "SEA": "KSEA",
    "YVR": "CYVR", "YYZ": "CYYZ", "MEX": "MMMX",
    "LHR": "EGLL", "LGW": "EGKK", "CDG": "LFPG", "FRA": "EDDF", "AMS": "EHAM",
    "MAD": "LEMD", "FCO": "LIRF", "ZRH": "LSZH", "CPH": "EKCH", "VIE": "LOWW",
    "SVO": "UUEE", "BCN": "LEBL",
    "DXB": "OMDB", "DOH": "OTHH", "JED": "OEJN", "IST": "LTFM", "TLV": "LLBG",
    "HND": "RJTT", "KIX": "RJBB", "ICN": "RKSI", "HKG": "VHHH", "PVG": "ZSSS",
    "PEK": "ZBAA", "SHA": "ZSPD", "BKK": "VTBS", "SIN": "WSSS", "KUL": "WMKK",
    "BOM": "VABB", "DEL": "VIDP", "MNL": "RPLL", "CGK": "WIIH",
    "SYD": "YSSY", "MEL": "YMML", "BNE": "YBBN", "AKL": "NZAA",
    "GRU": "SBGR", "EZE": "SAEZ", "SCL": "SCEL", "BOG": "SKBO", "GIG": "SBGL",
    "CPT": "FACT", "JNB": "FAOR", "CAI": "HECA", "ADD": "HAAB",
}


# ── DISTANCE CALCULATION (HAVERSINE FORMULA) ──────────────────────────────────
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great circle distance between two points using Haversine formula.
    Returns distance in nautical miles.
    
    Args:
        lat1, lon1: Coordinates of first point (degrees)
        lat2, lon2: Coordinates of second point (degrees)
    
    Returns:
        Distance in nautical miles
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in nautical miles
    earth_radius_nm = 3440.065
    
    distance = earth_radius_nm * c
    return distance


# ── AIRPORT LOOKUP ────────────────────────────────────────────────────────────
def lookup_airport(code: str) -> dict | None:
    """
    Look up airport by ICAO (4-letter) or IATA (3-letter) code.
    
    Args:
        code: Airport code (e.g., "KLAX", "LAX", "klax")
    
    Returns:
        Airport data dict or None if not found
    """
    code_upper = code.strip().upper()
    
    # Try direct ICAO lookup
    if code_upper in AIRPORTS:
        return {"icao": code_upper, **AIRPORTS[code_upper]}
    
    # Try IATA to ICAO conversion
    if code_upper in IATA_TO_ICAO:
        icao = IATA_TO_ICAO[code_upper]
        return {"icao": icao, **AIRPORTS[icao]}
    
    return None


# ── CALCULATE ROUTE DISTANCE ──────────────────────────────────────────────────
def calculate_route(origin: str, destination: str) -> dict:
    """
    Calculate distance between two airports.
    
    Args:
        origin: Origin airport code (ICAO or IATA)
        destination: Destination airport code (ICAO or IATA)
    
    Returns:
        dict with origin/destination info and distance, or error
    """
    # Lookup airports
    origin_airport = lookup_airport(origin)
    destination_airport = lookup_airport(destination)
    
    if not origin_airport:
        return {"error": f"Origin airport '{origin}' not found in database"}
    
    if not destination_airport:
        return {"error": f"Destination airport '{destination}' not found in database"}
    
    # Calculate distance
    distance_nm = calculate_distance(
        origin_airport["lat"], origin_airport["lon"],
        destination_airport["lat"], destination_airport["lon"]
    )
    
    return {
        "origin": {
            "icao": origin_airport["icao"],
            "iata": next((k for k, v in IATA_TO_ICAO.items() if v == origin_airport["icao"]), None),
            "name": origin_airport["name"],
            "city": origin_airport["city"],
            "country": origin_airport["country"],
            "lat": origin_airport["lat"],
            "lon": origin_airport["lon"],
        },
        "destination": {
            "icao": destination_airport["icao"],
            "iata": next((k for k, v in IATA_TO_ICAO.items() if v == destination_airport["icao"]), None),
            "name": destination_airport["name"],
            "city": destination_airport["city"],
            "country": destination_airport["country"],
            "lat": destination_airport["lat"],
            "lon": destination_airport["lon"],
        },
        "distance_nm": round(distance_nm, 1),
        "distance_km": round(distance_nm * 1.852, 1),
    }


# ── LIST AIRPORTS ─────────────────────────────────────────────────────────────
def list_airports_by_region(region: str = None) -> None:
    """Print airports, optionally filtered by region."""
    
    regions = {
        "North America": ["K", "C", "M"],  # USA, Canada, Mexico (starting letters)
        "Europe": ["E", "L", "U"],
        "Middle East": ["O", "LT", "LL"],
        "Asia": ["R", "V", "W", "Z"],
        "Oceania": ["Y", "N"],
        "South America": ["S"],
        "Africa": ["F", "H"],
    }
    
    if region and region not in regions:
        print(f"Unknown region. Available: {', '.join(regions.keys())}")
        return
    
    print(f"\n{'ICAO':<6} {'IATA':<6} {'NAME':<35} {'CITY':<20} {'COUNTRY':<15}")
    print("─" * 95)
    
    for icao, data in sorted(AIRPORTS.items()):
        # Filter by region if specified
        if region:
            prefixes = regions[region]
            if not any(icao.startswith(p) for p in prefixes):
                continue
        
        iata = next((k for k, v in IATA_TO_ICAO.items() if v == icao), "N/A")
        print(f"{icao:<6} {iata:<6} {data['name']:<35} {data['city']:<20} {data['country']:<15}")
    
    print()


# ── QUICK TEST ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "═" * 80)
    print("  AIRPORT DATABASE & DISTANCE CALCULATOR")
    print("═" * 80)
    
    # Test airport lookups
    print("\n📍 AIRPORT LOOKUP TESTS:")
    print("─" * 80)
    test_codes = ["KLAX", "LAX", "lhr", "EGLL", "SIN", "WSSS", "XYZ123"]
    for code in test_codes:
        result = lookup_airport(code)
        if result:
            print(f"  '{code}' → {result['name']} ({result['city']}, {result['country']})")
        else:
            print(f"  '{code}' → ❌ Not found")
    
    # Test route calculations
    print("\n✈️  ROUTE DISTANCE TESTS:")
    print("─" * 80)
    
    routes = [
        ("KLAX", "EGLL"),  # Los Angeles to London
        ("JFK", "HND"),    # New York to Tokyo
        ("SIN", "SYD"),    # Singapore to Sydney
        ("DXB", "JFK"),    # Dubai to New York
    ]
    
    for origin, dest in routes:
        result = calculate_route(origin, dest)
        if "error" not in result:
            print(f"  {result['origin']['city']} → {result['destination']['city']}")
            print(f"    Distance: {result['distance_nm']:,.0f} nm ({result['distance_km']:,.0f} km)")
        else:
            print(f"  ❌ {result['error']}")
    
    print("\n📋 AIRPORT COUNT BY REGION:")
    print("─" * 80)
    for region in ["North America", "Europe", "Asia", "Oceania"]:
        count = sum(1 for icao in AIRPORTS if any(icao.startswith(p) for p in 
            {"North America": ["K", "C", "M"], "Europe": ["E", "L", "U"], 
             "Asia": ["R", "V", "W", "Z"], "Oceania": ["Y", "N"]}[region]))
        print(f"  {region:<20} {count} airports")
    
    print("\n" + "═" * 80 + "\n")
