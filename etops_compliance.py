# etops_compliance.py
# ETOPS (Extended-range Twin-engine Operational Performance Standards) Compliance Checker
# Verifies that twin-engine aircraft have suitable diversion airports within required time limits

from typing import List, Dict, Tuple
import math
from airport_database import AIRPORTS, lookup_airport
from aircraft_database import AIRCRAFT_DATABASE, lookup_aircraft


# ── ETOPS DIVERSION AIRPORTS ──────────────────────────────────────────────────
# Airports suitable for ETOPS diversions (adequate runway, facilities, weather)
# In production, this would be dynamically updated based on NOTAMs and weather

ETOPS_SUITABLE_AIRPORTS = {
    # North Atlantic
    "BIKF": {"name": "Keflavik (Reykjavik)", "country": "Iceland"},
    "BGBW": {"name": "Narsarsuaq", "country": "Greenland"},
    "CYYR": {"name": "Goose Bay", "country": "Canada"},
    "CYQX": {"name": "Gander", "country": "Canada"},
    "LPLA": {"name": "Lajes (Azores)", "country": "Portugal"},
    "EGLL": {"name": "London Heathrow", "country": "UK"},
    "KJFK": {"name": "New York JFK", "country": "USA"},
    "KBOS": {"name": "Boston", "country": "USA"},
    
    # North Pacific
    "RJAA": {"name": "Tokyo Narita", "country": "Japan"},
    "RJTT": {"name": "Tokyo Haneda", "country": "Japan"},
    "PANC": {"name": "Anchorage", "country": "USA"},
    "PHNL": {"name": "Honolulu", "country": "USA"},
    "KSEA": {"name": "Seattle", "country": "USA"},
    "CYVR": {"name": "Vancouver", "country": "Canada"},
    "RKSI": {"name": "Seoul Incheon", "country": "South Korea"},
    
    # South Pacific
    "YSSY": {"name": "Sydney", "country": "Australia"},
    "YMML": {"name": "Melbourne", "country": "Australia"},
    "NZAA": {"name": "Auckland", "country": "New Zealand"},
    "NZCH": {"name": "Christchurch", "country": "New Zealand"},
    "NFFN": {"name": "Nadi", "country": "Fiji"},
    "NTAA": {"name": "Papeete", "country": "French Polynesia"},
    
    # Indian Ocean
    "VOMM": {"name": "Chennai", "country": "India"},
    "VCBI": {"name": "Colombo", "country": "Sri Lanka"},
    "VRMM": {"name": "Male", "country": "Maldives"},
    "FIMP": {"name": "Mauritius", "country": "Mauritius"},
    "FACT": {"name": "Cape Town", "country": "South Africa"},
    
    # South Atlantic
    "SBGL": {"name": "Rio de Janeiro", "country": "Brazil"},
    "SBGR": {"name": "Sao Paulo", "country": "Brazil"},
    "SAEZ": {"name": "Buenos Aires", "country": "Argentina"},
    "SCCI": {"name": "Santiago", "country": "Chile"},
    
    # Middle East
    "OMDB": {"name": "Dubai", "country": "UAE"},
    "OTHH": {"name": "Doha", "country": "Qatar"},
    "OJAI": {"name": "Amman", "country": "Jordan"},
}


# ── DISTANCE CALCULATIONS ─────────────────────────────────────────────────────

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


# ── ETOPS COMPLIANCE CHECKING ─────────────────────────────────────────────────

def check_etops_compliance(aircraft_code: str, waypoints: List[Dict], 
                          cruise_speed_kt: float = None) -> Dict:
    """
    Check if a route meets ETOPS requirements for twin-engine aircraft.
    
    ETOPS rules require that at any point along the route, the aircraft must be
    within a certain flying time (typically 60, 90, 120, 138, 180, or 240 minutes)
    of a suitable diversion airport.
    
    Args:
        aircraft_code: Aircraft type code
        waypoints: List of waypoint dicts with 'lat', 'lon', 'number', 'name'
        cruise_speed_kt: Aircraft cruise speed (if None, uses aircraft database)
    
    Returns:
        dict with compliance status and details
    """
    # Look up aircraft
    aircraft = lookup_aircraft(aircraft_code)
    if not aircraft:
        return {"error": f"Aircraft '{aircraft_code}' not found"}
    
    # Check if aircraft is ETOPS rated
    etops_minutes = aircraft.get('etops_minutes')
    if etops_minutes is None:
        return {
            "compliant": True,
            "reason": "not_required",
            "message": f"{aircraft['full_name']} is not ETOPS rated (likely 4-engine or not certified for extended overwater). ETOPS rules do not apply.",
            "aircraft": aircraft['full_name']
        }
    
    # Use aircraft cruise speed if not provided
    if cruise_speed_kt is None:
        cruise_speed_kt = aircraft['typical_cruise_ktas']
    
    # Calculate maximum diversion distance based on ETOPS rating
    max_diversion_distance_nm = (etops_minutes / 60) * cruise_speed_kt
    
    # Check each waypoint
    violations = []
    compliant_points = []
    
    for waypoint in waypoints:
        lat = waypoint['lat']
        lon = waypoint['lon']
        
        # Find nearest ETOPS-suitable airport
        nearest_airport = None
        nearest_distance = float('inf')
        
        for icao, airport_info in ETOPS_SUITABLE_AIRPORTS.items():
            if icao in AIRPORTS:
                airport = AIRPORTS[icao]
                distance = haversine_distance(lat, lon, airport['lat'], airport['lon'])
                
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_airport = {
                        "icao": icao,
                        "name": airport_info['name'],
                        "country": airport_info['country'],
                        "distance_nm": round(distance, 1),
                        "time_minutes": round((distance / cruise_speed_kt) * 60, 1)
                    }
        
        # Check if within ETOPS limit
        if nearest_airport and nearest_distance <= max_diversion_distance_nm:
            compliant_points.append({
                "waypoint": waypoint,
                "nearest_diversion": nearest_airport,
                "compliant": True
            })
        else:
            violations.append({
                "waypoint": waypoint,
                "nearest_diversion": nearest_airport,
                "required_time_minutes": etops_minutes,
                "actual_time_minutes": nearest_airport['time_minutes'] if nearest_airport else None,
                "compliant": False
            })
    
    # Overall compliance
    is_compliant = len(violations) == 0
    
    return {
        "compliant": is_compliant,
        "aircraft": aircraft['full_name'],
        "etops_rating": f"ETOPS-{etops_minutes}",
        "max_diversion_distance_nm": round(max_diversion_distance_nm, 1),
        "cruise_speed_kt": cruise_speed_kt,
        "total_waypoints_checked": len(waypoints),
        "compliant_waypoints": len(compliant_points),
        "violations": violations,
        "sample_diversions": compliant_points[:3] if compliant_points else [],
        "message": _generate_compliance_message(is_compliant, aircraft, etops_minutes, violations)
    }


def _generate_compliance_message(compliant: bool, aircraft: Dict, 
                                etops_minutes: int, violations: List) -> str:
    """Generate human-readable compliance message"""
    if compliant:
        return (f"✅ Route is ETOPS-{etops_minutes} compliant for {aircraft['full_name']}. "
                f"All waypoints are within {etops_minutes} minutes flying time of a suitable diversion airport.")
    else:
        return (f"❌ Route violates ETOPS-{etops_minutes} requirements for {aircraft['full_name']}. "
                f"{len(violations)} waypoint(s) exceed the maximum diversion time. "
                f"Route must be adjusted or a 4-engine aircraft used.")


def find_etops_diversions_along_route(origin_code: str, dest_code: str, 
                                      max_distance_nm: float = 500) -> List[Dict]:
    """
    Find all ETOPS-suitable diversion airports along a route.
    
    Args:
        origin_code: Origin airport code
        dest_code: Destination airport code
        max_distance_nm: Maximum distance from route to consider (default 500nm)
    
    Returns:
        List of suitable diversion airports with distances
    """
    origin = lookup_airport(origin_code)
    dest = lookup_airport(dest_code)
    
    if not origin or not dest:
        return []
    
    # Calculate midpoint
    mid_lat = (origin['lat'] + dest['lat']) / 2
    mid_lon = (origin['lon'] + dest['lon']) / 2
    
    # Find airports near the route
    route_airports = []
    
    for icao, airport_info in ETOPS_SUITABLE_AIRPORTS.items():
        if icao in AIRPORTS:
            airport = AIRPORTS[icao]
            
            # Calculate distance from route midpoint
            distance_from_midpoint = haversine_distance(
                mid_lat, mid_lon,
                airport['lat'], airport['lon']
            )
            
            # Calculate distances from origin and destination
            distance_from_origin = haversine_distance(
                origin['lat'], origin['lon'],
                airport['lat'], airport['lon']
            )
            
            distance_from_dest = haversine_distance(
                dest['lat'], dest['lon'],
                airport['lat'], airport['lon']
            )
            
            # Include if reasonably close to the route
            if distance_from_midpoint <= max_distance_nm:
                route_airports.append({
                    "icao": icao,
                    "name": airport_info['name'],
                    "country": airport_info['country'],
                    "lat": airport['lat'],
                    "lon": airport['lon'],
                    "distance_from_origin_nm": round(distance_from_origin, 1),
                    "distance_from_dest_nm": round(distance_from_dest, 1),
                    "distance_from_route_nm": round(distance_from_midpoint, 1)
                })
    
    # Sort by distance from origin
    route_airports.sort(key=lambda x: x['distance_from_origin_nm'])
    
    return route_airports


# ── DISPLAY FUNCTIONS ─────────────────────────────────────────────────────────

def format_etops_report(result: Dict) -> str:
    """Format ETOPS compliance report"""
    output = "\n" + "═" * 80 + "\n"
    output += "  ✈️  ETOPS COMPLIANCE REPORT\n"
    output += "═" * 80 + "\n\n"
    
    if result.get('error'):
        return output + f"❌ Error: {result['error']}\n" + "═" * 80 + "\n"
    
    if result.get('reason') == 'not_required':
        output += result['message'] + "\n"
        output += "═" * 80 + "\n"
        return output
    
    output += f"**Aircraft:** {result['aircraft']}\n"
    output += f"**ETOPS Rating:** {result['etops_rating']}\n"
    output += f"**Maximum Diversion Distance:** {result['max_diversion_distance_nm']} nm\n"
    output += f"**Cruise Speed:** {result['cruise_speed_kt']} kt\n\n"
    
    # Compliance status
    if result['compliant']:
        output += "✅ **ROUTE IS ETOPS COMPLIANT**\n\n"
        output += f"All {result['total_waypoints_checked']} waypoints have suitable diversion airports "
        output += f"within ETOPS-{result['etops_rating'].split('-')[1]} limits.\n\n"
        
        # Show sample diversions
        if result['sample_diversions']:
            output += "**Sample Diversion Airports:**\n"
            output += "─" * 80 + "\n"
            for item in result['sample_diversions']:
                wp = item['waypoint']
                div = item['nearest_diversion']
                output += f"• Waypoint {wp['number']} ({wp['name']})\n"
                output += f"  Nearest: {div['name']} ({div['icao']}) - {div['distance_nm']} nm / {div['time_minutes']} min\n"
    
    else:
        output += "❌ **ROUTE VIOLATES ETOPS REQUIREMENTS**\n\n"
        output += f"{len(result['violations'])} waypoint(s) do not meet ETOPS-{result['etops_rating'].split('-')[1]} compliance.\n\n"
        
        output += "**Violations:**\n"
        output += "─" * 80 + "\n"
        for v in result['violations']:
            wp = v['waypoint']
            div = v['nearest_diversion']
            output += f"❌ Waypoint {wp['number']} ({wp['name']})\n"
            if div:
                output += f"   Nearest: {div['name']} - {div['distance_nm']} nm / {div['time_minutes']} min\n"
                output += f"   Required: < {v['required_time_minutes']} min | Actual: {v['actual_time_minutes']} min\n"
            else:
                output += "   No suitable diversion airport found\n"
            output += "\n"
    
    output += "═" * 80 + "\n"
    output += result['message'] + "\n"
    output += "═" * 80 + "\n"
    
    return output


def format_diversion_airports(airports: List[Dict], origin: str, dest: str) -> str:
    """Format list of ETOPS diversion airports"""
    output = f"\n📍 ETOPS Diversion Airports: {origin} → {dest}\n"
    output += "─" * 80 + "\n"
    
    if not airports:
        return output + "No suitable diversion airports found along this route.\n"
    
    for airport in airports:
        output += f"• {airport['name']} ({airport['icao']}) - {airport['country']}\n"
        output += f"  From origin: {airport['distance_from_origin_nm']} nm | "
        output += f"From dest: {airport['distance_from_dest_nm']} nm\n"
    
    return output


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 80)
    print("  ETOPS COMPLIANCE MODULE TEST")
    print("═" * 80)
    
    # Test 1: Check B777-300ER (ETOPS-180) on transatlantic route
    print("\n📊 Test 1: B777-300ER on Transatlantic Route (KLAX → EGLL)")
    print("─" * 80)
    
    # Sample waypoints for LAX-London route
    transatlantic_waypoints = [
        {"number": 0, "name": "Los Angeles", "lat": 33.9425, "lon": -118.4081},
        {"number": 1, "name": "WPT1", "lat": 40.0, "lon": -100.0},
        {"number": 2, "name": "WPT2", "lat": 45.0, "lon": -80.0},
        {"number": 3, "name": "WPT3", "lat": 50.0, "lon": -60.0},
        {"number": 4, "name": "WPT4", "lat": 52.0, "lon": -40.0},
        {"number": 5, "name": "WPT5", "lat": 53.0, "lon": -20.0},
        {"number": 6, "name": "London", "lat": 51.4700, "lon": -0.4543},
    ]
    
    result1 = check_etops_compliance("B777-300ER", transatlantic_waypoints)
    print(format_etops_report(result1))
    
    # Test 2: Find diversion airports along route
    print("\n📊 Test 2: Find ETOPS Diversion Airports (KLAX → EGLL)")
    print("─" * 80)
    diversions = find_etops_diversions_along_route("KLAX", "EGLL", max_distance_nm=800)
    print(format_diversion_airports(diversions, "KLAX", "EGLL"))
    
    # Test 3: Check B737-800 (not ETOPS rated)
    print("\n📊 Test 3: B737-800 (Not ETOPS Rated)")
    print("─" * 80)
    result3 = check_etops_compliance("B737-800", transatlantic_waypoints)
    print(format_etops_report(result3))
    
    print("\n✅ ETOPS compliance module test complete!")
    print("\n💡 Note: This uses a simplified database of ETOPS-suitable airports.")
    print("   Production systems should integrate with real-time NOTAM and weather data.\n")
