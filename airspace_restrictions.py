# airspace_restrictions.py
# Airspace Restrictions & No-Fly Zone Checker
# Checks routes against known restricted airspace

from typing import List, Dict, Tuple
import math


# ── KNOWN RESTRICTED AIRSPACE ─────────────────────────────────────────────────
# This is a simplified database. In production, integrate with:
# - FAA NOTAM system
# - ICAO airspace databases
# - Real-time TFR (Temporary Flight Restrictions)
# - Country-specific aviation authorities

RESTRICTED_AIRSPACE = {
    "P-56": {
        "name": "White House Prohibited Area",
        "type": "Prohibited",
        "country": "USA",
        "center_lat": 38.8977,
        "center_lon": -77.0365,
        "radius_nm": 1.5,
        "altitude_limit_ft": None,  # All altitudes
        "description": "Presidential and governmental facilities",
        "severity": "CRITICAL"
    },
    "P-40": {
        "name": "Camp David Prohibited Area",
        "type": "Prohibited",
        "country": "USA",
        "center_lat": 39.6483,
        "center_lon": -77.4650,
        "radius_nm": 1.5,
        "altitude_limit_ft": None,
        "description": "Presidential retreat",
        "severity": "CRITICAL"
    },
    "TFR-DMZ": {
        "name": "Korean DMZ",
        "type": "Prohibited",
        "country": "Korea",
        "center_lat": 38.0,
        "center_lon": 127.5,
        "radius_nm": 50,
        "altitude_limit_ft": None,
        "description": "Demilitarized Zone",
        "severity": "CRITICAL"
    },
    "R-2508": {
        "name": "Edwards AFB Restricted Area",
        "type": "Restricted",
        "country": "USA",
        "center_lat": 34.9054,
        "center_lon": -117.8840,
        "radius_nm": 20,
        "altitude_limit_ft": 80000,
        "description": "Military test range",
        "severity": "HIGH"
    },
    "LIBYA-NFZ": {
        "name": "Libya Conflict Zone",
        "type": "Danger",
        "country": "Libya",
        "center_lat": 32.0,
        "center_lon": 20.0,
        "radius_nm": 200,
        "altitude_limit_ft": None,
        "description": "Conflict zone - avoid all operations",
        "severity": "CRITICAL"
    },
    "UKRAINE-NFZ": {
        "name": "Ukraine Conflict Zone",
        "type": "Danger",
        "country": "Ukraine",
        "center_lat": 48.0,
        "center_lon": 37.0,
        "radius_nm": 150,
        "altitude_limit_ft": None,
        "description": "Active conflict zone",
        "severity": "CRITICAL"
    },
    "SYRIA-NFZ": {
        "name": "Syria Conflict Zone",
        "type": "Danger",
        "country": "Syria",
        "center_lat": 35.0,
        "center_lon": 38.0,
        "radius_nm": 100,
        "altitude_limit_ft": None,
        "description": "Conflict zone",
        "severity": "CRITICAL"
    },
    "YEMEN-NFZ": {
        "name": "Yemen Conflict Zone",
        "type": "Danger",
        "country": "Yemen",
        "center_lat": 15.5,
        "center_lon": 48.0,
        "radius_nm": 100,
        "altitude_limit_ft": None,
        "description": "Active conflict zone",
        "severity": "CRITICAL"
    },
    "R-BERMUDA": {
        "name": "Bermuda Triangle",
        "type": "Warning",
        "country": "International",
        "center_lat": 25.0,
        "center_lon": -71.0,
        "radius_nm": 200,
        "altitude_limit_ft": None,
        "description": "High traffic area - enhanced vigilance required",
        "severity": "LOW"
    },
    "NORTH-KOREA": {
        "name": "North Korea Airspace",
        "type": "Prohibited",
        "country": "North Korea",
        "center_lat": 40.0,
        "center_lon": 127.0,
        "radius_nm": 150,
        "altitude_limit_ft": None,
        "description": "No overflight permitted",
        "severity": "CRITICAL"
    },
    "IRAN-RESTRICTED": {
        "name": "Iran Airspace (Limited Access)",
        "type": "Restricted",
        "country": "Iran",
        "center_lat": 32.0,
        "center_lon": 53.0,
        "radius_nm": 300,
        "altitude_limit_ft": None,
        "description": "Special authorization required",
        "severity": "HIGH"
    },
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


# ── AIRSPACE VIOLATION CHECKS ─────────────────────────────────────────────────

def check_point_in_restricted_airspace(lat: float, lon: float, 
                                       altitude_ft: float = 35000) -> List[Dict]:
    """
    Check if a point violates any restricted airspace.
    
    Args:
        lat: Latitude
        lon: Longitude
        altitude_ft: Altitude in feet (default cruise altitude)
    
    Returns:
        List of violated airspace zones
    """
    violations = []
    
    for zone_id, zone in RESTRICTED_AIRSPACE.items():
        distance = haversine_distance(
            lat, lon,
            zone['center_lat'], zone['center_lon']
        )
        
        # Check if within restricted radius
        if distance <= zone['radius_nm']:
            # Check altitude restriction if applicable
            if zone['altitude_limit_ft'] is None or altitude_ft <= zone['altitude_limit_ft']:
                violations.append({
                    "zone_id": zone_id,
                    "zone_name": zone['name'],
                    "type": zone['type'],
                    "severity": zone['severity'],
                    "distance_from_center_nm": round(distance, 1),
                    "description": zone['description'],
                    "country": zone['country']
                })
    
    return violations


def check_route_airspace_violations(waypoints: List[Dict], 
                                    altitude_ft: float = 35000,
                                    buffer_nm: float = 50) -> Dict:
    """
    Check if a route violates any airspace restrictions.
    
    Args:
        waypoints: List of waypoint dicts with 'lat' and 'lon'
        altitude_ft: Cruise altitude in feet
        buffer_nm: Safety buffer around restricted zones (default 50nm)
    
    Returns:
        dict with violations and warnings
    """
    critical_violations = []
    warnings = []
    near_restricted = []
    
    for i, waypoint in enumerate(waypoints):
        lat = waypoint['lat']
        lon = waypoint['lon']
        
        # Check each restricted zone
        for zone_id, zone in RESTRICTED_AIRSPACE.items():
            distance = haversine_distance(
                lat, lon,
                zone['center_lat'], zone['center_lon']
            )
            
            # Direct violation
            if distance <= zone['radius_nm']:
                if zone['altitude_limit_ft'] is None or altitude_ft <= zone['altitude_limit_ft']:
                    violation = {
                        "waypoint_number": waypoint.get('number', i),
                        "waypoint_name": waypoint.get('name', f"WPT{i}"),
                        "zone_id": zone_id,
                        "zone_name": zone['name'],
                        "type": zone['type'],
                        "severity": zone['severity'],
                        "distance_from_center_nm": round(distance, 1),
                        "description": zone['description'],
                        "country": zone['country']
                    }
                    
                    if zone['severity'] == "CRITICAL":
                        critical_violations.append(violation)
                    else:
                        warnings.append(violation)
            
            # Near restricted (within buffer)
            elif distance <= zone['radius_nm'] + buffer_nm:
                near_restricted.append({
                    "waypoint_number": waypoint.get('number', i),
                    "waypoint_name": waypoint.get('name', f"WPT{i}"),
                    "zone_id": zone_id,
                    "zone_name": zone['name'],
                    "type": zone['type'],
                    "distance_to_boundary_nm": round(distance - zone['radius_nm'], 1),
                    "description": zone['description']
                })
    
    return {
        "critical_violations": critical_violations,
        "warnings": warnings,
        "near_restricted": near_restricted,
        "route_clear": len(critical_violations) == 0,
        "caution_advised": len(warnings) > 0 or len(near_restricted) > 0
    }


def get_airspace_summary(lat: float, lon: float, radius_nm: float = 200) -> List[Dict]:
    """
    Get all restricted airspace within a radius of a point.
    
    Args:
        lat: Center latitude
        lon: Center longitude
        radius_nm: Search radius in nautical miles
    
    Returns:
        List of nearby restricted zones
    """
    nearby_zones = []
    
    for zone_id, zone in RESTRICTED_AIRSPACE.items():
        distance = haversine_distance(
            lat, lon,
            zone['center_lat'], zone['center_lon']
        )
        
        if distance <= radius_nm:
            nearby_zones.append({
                "zone_id": zone_id,
                "zone_name": zone['name'],
                "type": zone['type'],
                "severity": zone['severity'],
                "distance_nm": round(distance, 1),
                "description": zone['description'],
                "country": zone['country']
            })
    
    # Sort by distance
    nearby_zones.sort(key=lambda x: x['distance_nm'])
    
    return nearby_zones


# ── DISPLAY FUNCTIONS ─────────────────────────────────────────────────────────

def format_airspace_report(check_result: Dict) -> str:
    """Format airspace check results for display"""
    output = "\n" + "═" * 80 + "\n"
    output += "  🚫 AIRSPACE RESTRICTION REPORT\n"
    output += "═" * 80 + "\n\n"
    
    # Critical violations
    if check_result['critical_violations']:
        output += "❌ **CRITICAL VIOLATIONS DETECTED**\n"
        output += "─" * 80 + "\n"
        for v in check_result['critical_violations']:
            output += f"• Waypoint {v['waypoint_number']} ({v['waypoint_name']})\n"
            output += f"  Zone: {v['zone_name']} ({v['zone_id']})\n"
            output += f"  Type: {v['type']} | Severity: {v['severity']}\n"
            output += f"  Distance from center: {v['distance_from_center_nm']} nm\n"
            output += f"  ⚠️  {v['description']}\n\n"
    
    # Warnings
    if check_result['warnings']:
        output += "⚠️  **WARNINGS**\n"
        output += "─" * 80 + "\n"
        for w in check_result['warnings']:
            output += f"• Waypoint {w['waypoint_number']} ({w['waypoint_name']})\n"
            output += f"  Zone: {w['zone_name']}\n"
            output += f"  Type: {w['type']} | Distance: {w['distance_from_center_nm']} nm\n"
            output += f"  {w['description']}\n\n"
    
    # Near restricted
    if check_result['near_restricted']:
        output += "📍 **NEAR RESTRICTED AIRSPACE**\n"
        output += "─" * 80 + "\n"
        for n in check_result['near_restricted']:
            output += f"• Waypoint {n['waypoint_number']}: {n['zone_name']}\n"
            output += f"  Distance to boundary: {n['distance_to_boundary_nm']} nm\n\n"
    
    # Overall assessment
    output += "═" * 80 + "\n"
    if check_result['route_clear'] and not check_result['caution_advised']:
        output += "✅ **ROUTE CLEAR**: No airspace violations detected\n"
    elif check_result['route_clear'] and check_result['caution_advised']:
        output += "⚠️  **CAUTION**: Route is clear but passes near restricted airspace\n"
    else:
        output += "❌ **ROUTE NOT APPROVED**: Critical airspace violations detected\n"
        output += "    Route must be replanned to avoid prohibited areas\n"
    output += "═" * 80 + "\n"
    
    return output


def format_nearby_zones(zones: List[Dict], location_name: str = "Location") -> str:
    """Format nearby restricted zones"""
    if not zones:
        return f"\n✅ No restricted airspace within 200nm of {location_name}\n"
    
    output = f"\n📍 Restricted Airspace near {location_name}:\n"
    output += "─" * 80 + "\n"
    
    for zone in zones[:10]:  # Show top 10
        severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(zone['severity'], "⚪")
        output += f"{severity_icon} {zone['zone_name']} ({zone['type']})\n"
        output += f"   Distance: {zone['distance_nm']} nm | {zone['description']}\n"
    
    return output


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 80)
    print("  AIRSPACE RESTRICTIONS MODULE TEST")
    print("═" * 80)
    
    # Test 1: Check specific point
    print("\n📊 Test 1: Check point near White House")
    print("─" * 80)
    violations = check_point_in_restricted_airspace(38.90, -77.04, altitude_ft=5000)
    if violations:
        print("⚠️  AIRSPACE VIOLATION:")
        for v in violations:
            print(f"  • {v['zone_name']} ({v['severity']})")
            print(f"    Distance: {v['distance_from_center_nm']} nm")
    else:
        print("✅ No violations at this point")
    
    # Test 2: Check route
    print("\n\n📊 Test 2: Check route with sample waypoints")
    print("─" * 80)
    
    # Simulate a route that passes near North Korea
    sample_waypoints = [
        {"number": 0, "name": "Tokyo", "lat": 35.5494, "lon": 139.7798},
        {"number": 1, "name": "WPT1", "lat": 38.0, "lon": 135.0},
        {"number": 2, "name": "WPT2", "lat": 40.0, "lon": 128.0},  # Near North Korea!
        {"number": 3, "name": "Beijing", "lat": 40.0799, "lon": 116.6031},
    ]
    
    result = check_route_airspace_violations(sample_waypoints, altitude_ft=35000, buffer_nm=50)
    print(format_airspace_report(result))
    
    # Test 3: Get nearby zones
    print("\n📊 Test 3: Restricted zones near Washington DC")
    print("─" * 80)
    zones = get_airspace_summary(38.90, -77.04, radius_nm=200)
    print(format_nearby_zones(zones, "Washington DC"))
    
    print("\n✅ Airspace restrictions module test complete!")
    print("\n💡 Note: This is a simplified database. Production systems should integrate")
    print("   with FAA NOTAMs, ICAO databases, and real-time TFR systems.\n")
