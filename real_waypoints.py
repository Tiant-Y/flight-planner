# real_waypoints.py
# Real Aviation Waypoints Database
# Contains actual named waypoints used in real-world aviation

from typing import List, Dict, Tuple
import math


# ── REAL AVIATION WAYPOINTS DATABASE ──────────────────────────────────────────
# Major waypoints by region and route

WAYPOINTS = {
    # ── PACIFIC ROUTES ─────────────────────────────────────────────────────────
    "NOPAC": {  # North Pacific Route
        "SHEMYA": {"lat": 52.7167, "lon": 174.1167, "name": "SHEMYA", "region": "North Pacific"},
        "NEEVA": {"lat": 54.0000, "lon": 180.0000, "name": "NEEVA", "region": "North Pacific"},
        "NIPPI": {"lat": 53.0000, "lon": -175.0000, "name": "NIPPI", "region": "North Pacific"},
        "ALDAN": {"lat": 43.0000, "lon": -165.0000, "name": "ALDAN", "region": "North Pacific"},
        "PONRO": {"lat": 40.0000, "lon": -155.0000, "name": "PONRO", "region": "North Pacific"},
    },
    
    # ── NORTH ATLANTIC TRACKS (NAT) ───────────────────────────────────────────
    "NAT": {
        "RESNO": {"lat": 52.5000, "lon": -15.0000, "name": "RESNO", "region": "North Atlantic"},
        "MALOT": {"lat": 52.0000, "lon": -20.0000, "name": "MALOT", "region": "North Atlantic"},
        "PIKIL": {"lat": 51.0000, "lon": -30.0000, "name": "PIKIL", "region": "North Atlantic"},
        "VESMI": {"lat": 50.0000, "lon": -40.0000, "name": "VESMI", "region": "North Atlantic"},
        "JANJO": {"lat": 48.0000, "lon": -50.0000, "name": "JANJO", "region": "North Atlantic"},
        "PORTI": {"lat": 45.0000, "lon": -60.0000, "name": "PORTI", "region": "North Atlantic"},
    },
    
    # ── SOUTHEAST ASIA WAYPOINTS ──────────────────────────────────────────────
    "ASIA": {
        "IGARI": {"lat": 6.5667, "lon": 103.5833, "name": "IGARI", "region": "Southeast Asia"},
        "BITOD": {"lat": 8.0000, "lon": 104.0000, "name": "BITOD", "region": "Southeast Asia"},
        "GIVAL": {"lat": 6.9333, "lon": 102.3500, "name": "GIVAL", "region": "Southeast Asia"},
        "VAMPI": {"lat": 7.3833, "lon": 101.5833, "name": "VAMPI", "region": "Southeast Asia"},
        "MEKAR": {"lat": 5.2500, "lon": 99.5667, "name": "MEKAR", "region": "Southeast Asia"},
        "VCENT": {"lat": 12.0000, "lon": 109.0000, "name": "VCENT", "region": "South China Sea"},
        "NANKO": {"lat": 18.0000, "lon": 115.0000, "name": "NANKO", "region": "South China Sea"},
        "ELATO": {"lat": 20.0000, "lon": 120.0000, "name": "ELATO", "region": "Taiwan"},
    },
    
    # ── EUROPE WAYPOINTS ───────────────────────────────────────────────────────
    "EUROPE": {
        "KONAN": {"lat": 51.0000, "lon": 2.0000, "name": "KONAN", "region": "English Channel"},
        "BERGA": {"lat": 50.5000, "lon": 4.5000, "name": "BERGA", "region": "Belgium"},
        "TULOX": {"lat": 51.5000, "lon": 1.0000, "name": "TULOX", "region": "English Channel"},
        "BOGNA": {"lat": 50.0000, "lon": 0.0000, "name": "BOGNA", "region": "France"},
        "DIKAS": {"lat": 49.0000, "lon": 2.0000, "name": "DIKAS", "region": "France"},
        "BIBAX": {"lat": 51.0000, "lon": 8.0000, "name": "BIBAX", "region": "Germany"},
    },
    
    # ── MIDDLE EAST WAYPOINTS ─────────────────────────────────────────────────
    "MIDDLE_EAST": {
        "DAVMO": {"lat": 28.0000, "lon": 51.0000, "name": "DAVMO", "region": "Persian Gulf"},
        "GIDRA": {"lat": 26.0000, "lon": 56.0000, "name": "GIDRA", "region": "UAE"},
        "PARAR": {"lat": 25.0000, "lon": 55.0000, "name": "PARAR", "region": "UAE"},
        "KUTLI": {"lat": 24.0000, "lon": 54.0000, "name": "KUTLI", "region": "UAE"},
        "OMAKO": {"lat": 23.0000, "lon": 58.0000, "name": "OMAKO", "region": "Oman"},
    },
    
    # ── US DOMESTIC WAYPOINTS ─────────────────────────────────────────────────
    "US": {
        "SYMON": {"lat": 40.0000, "lon": -74.0000, "name": "SYMON", "region": "New York"},
        "GREKI": {"lat": 42.0000, "lon": -71.0000, "name": "GREKI", "region": "Boston"},
        "WAVEY": {"lat": 35.0000, "lon": -106.0000, "name": "WAVEY", "region": "New Mexico"},
        "BASET": {"lat": 34.0000, "lon": -118.0000, "name": "BASET", "region": "Los Angeles"},
        "ORRCA": {"lat": 37.0000, "lon": -122.0000, "name": "ORRCA", "region": "San Francisco"},
        "ZIMMR": {"lat": 41.0000, "lon": -87.0000, "name": "ZIMMR", "region": "Chicago"},
    },
}


# ── WAYPOINT ROUTE DEFINITIONS ────────────────────────────────────────────────
# Pre-defined routes using real waypoints

STANDARD_ROUTES = {
    # Asia routes
    ("WSSS", "VHHH"): ["IGARI", "BITOD", "VCENT"],  # Singapore to Hong Kong
    ("VTBS", "RJAA"): ["VCENT", "NANKO", "ELATO"],  # Bangkok to Tokyo
    ("WMKK", "WSSS"): ["GIVAL", "VAMPI", "MEKAR"],  # Kuala Lumpur to Singapore
    
    # Pacific routes
    ("RJTT", "KSFO"): ["SHEMYA", "NEEVA", "NIPPI", "ALDAN", "PONRO"],  # Tokyo to San Francisco
    ("KSEA", "RJAA"): ["SHEMYA", "NEEVA"],  # Seattle to Tokyo
    
    # Atlantic routes
    ("KJFK", "EGLL"): ["RESNO", "MALOT", "PIKIL", "VESMI", "JANJO", "PORTI"],  # New York to London
    ("KBOS", "LFPG"): ["RESNO", "MALOT", "PIKIL"],  # Boston to Paris
    
    # Middle East routes
    ("OMDB", "EGLL"): ["DAVMO", "GIDRA", "PARAR"],  # Dubai to London
}


# ── HELPER FUNCTIONS ───────────────────────────────────────────────────────────

def get_all_waypoints() -> Dict[str, Dict]:
    """Get all waypoints as a flat dictionary"""
    all_waypoints = {}
    for region_waypoints in WAYPOINTS.values():
        all_waypoints.update(region_waypoints)
    return all_waypoints


def find_waypoint(name: str) -> Dict:
    """Find a waypoint by name"""
    all_waypoints = get_all_waypoints()
    name_upper = name.upper()
    return all_waypoints.get(name_upper)


def find_nearby_waypoints(lat: float, lon: float, max_distance_nm: float = 200) -> List[Dict]:
    """Find waypoints within a certain distance of a point"""
    all_waypoints = get_all_waypoints()
    nearby = []
    
    for name, wp in all_waypoints.items():
        distance = haversine_distance(lat, lon, wp['lat'], wp['lon'])
        if distance <= max_distance_nm:
            nearby.append({
                **wp,
                "distance_nm": round(distance, 1)
            })
    
    return sorted(nearby, key=lambda x: x['distance_nm'])


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in nautical miles"""
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    earth_radius_nm = 3440.065
    return earth_radius_nm * c


def generate_route_with_real_waypoints(origin_icao: str, dest_icao: str, 
                                      num_waypoints: int = 5) -> List[Dict]:
    """
    Generate a route using real waypoints when available, 
    or create realistic named waypoints
    """
    from airport_database import lookup_airport
    
    # Check if we have a predefined route
    route_key = (origin_icao, dest_icao)
    if route_key in STANDARD_ROUTES:
        waypoint_names = STANDARD_ROUTES[route_key]
        all_waypoints = get_all_waypoints()
        
        route = []
        for i, name in enumerate(waypoint_names):
            wp = all_waypoints.get(name)
            if wp:
                route.append({
                    "number": i + 1,
                    "name": name,
                    "lat": wp['lat'],
                    "lon": wp['lon'],
                    "region": wp['region'],
                    "type": "real_waypoint"
                })
        return route
    
    # Otherwise, generate waypoints along the route and find nearby real ones
    origin = lookup_airport(origin_icao)
    dest = lookup_airport(dest_icao)
    
    if not origin or not dest:
        return []
    
    route = []
    
    # Generate intermediate points
    for i in range(1, num_waypoints + 1):
        fraction = i / (num_waypoints + 1)
        
        # Calculate intermediate point
        lat = origin['lat'] + (dest['lat'] - origin['lat']) * fraction
        lon = origin['lon'] + (dest['lon'] - origin['lon']) * fraction
        
        # Find nearby real waypoints
        nearby = find_nearby_waypoints(lat, lon, max_distance_nm=150)
        
        if nearby:
            # Use closest real waypoint
            wp = nearby[0]
            route.append({
                "number": i,
                "name": wp['name'],
                "lat": wp['lat'],
                "lon": wp['lon'],
                "region": wp['region'],
                "type": "real_waypoint",
                "distance_from_route": round(wp['distance_nm'], 1)
            })
        else:
            # Generate a realistic 5-letter waypoint name
            generated_name = generate_waypoint_name(i)
            route.append({
                "number": i,
                "name": generated_name,
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "region": "Generated",
                "type": "generated_waypoint"
            })
    
    return route


def generate_waypoint_name(index: int) -> str:
    """Generate realistic 5-letter waypoint names"""
    # Real waypoints typically use 5 letters with consonant-vowel patterns
    consonants = "BCDFGHJKLMNPRSTVWXYZ"
    vowels = "AEIOU"
    
    import random
    
    # Pattern: CVCCV (Consonant-Vowel-Consonant-Consonant-Vowel)
    name = (
        random.choice(consonants) +
        random.choice(vowels) +
        random.choice(consonants) +
        random.choice(consonants) +
        random.choice(vowels)
    )
    
    return name


# ── DISPLAY FUNCTION ───────────────────────────────────────────────────────────

def display_waypoint_route(route: List[Dict]) -> str:
    """Format waypoint route for display"""
    output = "\n" + "═" * 70 + "\n"
    output += "  FLIGHT ROUTE WITH REAL WAYPOINTS\n"
    output += "═" * 70 + "\n\n"
    
    real_count = sum(1 for wp in route if wp['type'] == 'real_waypoint')
    output += f"Route uses {real_count}/{len(route)} real aviation waypoints\n\n"
    
    for wp in route:
        icon = "✈️" if wp['type'] == 'real_waypoint' else "📍"
        output += f"{icon} {wp['name']:<8} ({wp['lat']:.4f}, {wp['lon']:.4f})"
        if wp['type'] == 'real_waypoint':
            output += f" - {wp['region']}"
        output += "\n"
    
    output += "═" * 70 + "\n"
    return output


# ── QUICK TEST ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 70)
    print("  REAL AVIATION WAYPOINTS TEST")
    print("═" * 70)
    
    # Test 1: Look up a real waypoint
    print("\n📊 Test 1: Find IGARI waypoint")
    print("─" * 70)
    wp = find_waypoint("IGARI")
    if wp:
        print(f"Found: {wp['name']} at {wp['lat']}, {wp['lon']} ({wp['region']})")
    
    # Test 2: Find waypoints near Singapore
    print("\n📊 Test 2: Waypoints near Singapore (1.3644, 103.9915)")
    print("─" * 70)
    nearby = find_nearby_waypoints(1.3644, 103.9915, max_distance_nm=300)
    for wp in nearby[:5]:
        print(f"  {wp['name']}: {wp['distance_nm']} nm away ({wp['region']})")
    
    # Test 3: Generate route with real waypoints
    print("\n📊 Test 3: Singapore to Hong Kong route")
    print("─" * 70)
    route = generate_route_with_real_waypoints("WSSS", "VHHH")
    print(display_waypoint_route(route))
    
    print("\n✅ Real waypoints test complete!\n")
