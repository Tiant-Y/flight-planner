# route_optimization.py
# Route Optimization: Great Circle + Wind Optimization + Real Waypoints
# Calculates optimal flight paths considering winds aloft and uses real aviation waypoints

import math
from typing import List, Tuple, Dict
from airport_database import lookup_airport
from real_waypoints import generate_route_with_real_waypoints, get_all_waypoints

# Import comprehensive waypoint database (50,000+ waypoints worldwide)
try:
    from comprehensive_waypoints import (
        load_waypoint_database, 
        find_waypoint as find_comprehensive_waypoint,
        generate_realistic_route as generate_comprehensive_route
    )
    COMPREHENSIVE_DB_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_DB_AVAILABLE = False
    print("⚠️ Comprehensive waypoint database not available")


# ── GREAT CIRCLE CALCULATIONS ─────────────────────────────────────────────────

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate initial bearing (heading) from point 1 to point 2.
    
    Returns:
        Bearing in degrees (0-360)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    
    x = math.sin(dlon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def calculate_intermediate_point(lat1: float, lon1: float, 
                                 lat2: float, lon2: float, 
                                 fraction: float) -> Tuple[float, float]:
    """
    Calculate intermediate point along great circle route.
    
    Args:
        lat1, lon1: Start coordinates
        lat2, lon2: End coordinates
        fraction: Position along route (0.0 = start, 1.0 = end)
    
    Returns:
        Tuple of (latitude, longitude)
    """
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Angular distance
    d = math.acos(math.sin(lat1_rad) * math.sin(lat2_rad) + 
                  math.cos(lat1_rad) * math.cos(lat2_rad) * 
                  math.cos(lon2_rad - lon1_rad))
    
    if d == 0:  # Same point
        return (lat1, lon1)
    
    a = math.sin((1 - fraction) * d) / math.sin(d)
    b = math.sin(fraction * d) / math.sin(d)
    
    x = a * math.cos(lat1_rad) * math.cos(lon1_rad) + \
        b * math.cos(lat2_rad) * math.cos(lon2_rad)
    y = a * math.cos(lat1_rad) * math.sin(lon1_rad) + \
        b * math.cos(lat2_rad) * math.sin(lon2_rad)
    z = a * math.sin(lat1_rad) + b * math.sin(lat2_rad)
    
    lat = math.degrees(math.atan2(z, math.sqrt(x*x + y*y)))
    lon = math.degrees(math.atan2(y, x))
    
    return (lat, lon)


# ── ROUTE WAYPOINT GENERATION ─────────────────────────────────────────────────

def generate_route_waypoints(origin_code: str, dest_code: str, 
                            num_waypoints: int = 5) -> Dict:
    """
    Generate waypoints along great circle route using real aviation waypoints.
    Uses two-tier system:
    1. First tries curated real_waypoints.py (fast, common routes)
    2. Falls back to comprehensive database (complete worldwide coverage)
    
    Args:
        origin_code: Origin airport code
        dest_code: Destination airport code
        num_waypoints: Number of intermediate waypoints (default 5)
    
    Returns:
        dict with route information and waypoints (uses real waypoint names like IGARI, VCENT)
    """
    # Look up airports
    origin = lookup_airport(origin_code)
    dest = lookup_airport(dest_code)
    
    if not origin or not dest:
        return {"error": "Airport not found"}
    
    # Calculate total distance
    distance_nm = haversine_distance(
        origin['lat'], origin['lon'], 
        dest['lat'], dest['lon']
    )
    
    # Calculate initial and final bearings
    initial_bearing = calculate_bearing(
        origin['lat'], origin['lon'],
        dest['lat'], dest['lon']
    )
    
    final_bearing = calculate_bearing(
        dest['lat'], dest['lon'],
        origin['lat'], origin['lon']
    )
    final_bearing = (final_bearing + 180) % 360  # Reverse direction
    
    # Try to generate waypoints using curated database first
    real_waypoints = generate_route_with_real_waypoints(origin_code, dest_code, num_waypoints)
    
    # If no waypoints found and comprehensive database is available, use it
    if (not real_waypoints or len(real_waypoints) == 0) and COMPREHENSIVE_DB_AVAILABLE:
        try:
            print(f"🔍 Using comprehensive waypoint database for {origin_code} → {dest_code}")
            comprehensive_wps = generate_comprehensive_route(
                origin['lat'], origin['lon'],
                dest['lat'], dest['lon'],
                num_waypoints
            )
            
            # Convert comprehensive format to our format
            real_waypoints = []
            for i, wp in enumerate(comprehensive_wps, 1):
                real_waypoints.append({
                    "number": i,
                    "name": wp['ident'],
                    "lat": wp['lat'],
                    "lon": wp['lon'],
                    "region": wp.get('region', 'N/A'),
                    "type": "comprehensive_waypoint"
                })
        except Exception as e:
            print(f"⚠️ Error using comprehensive database: {e}")
    
    # Build complete waypoint list with origin and destination
    waypoints = []
    
    # Add origin
    waypoints.append({
        "number": 0,
        "lat": origin['lat'],
        "lon": origin['lon'],
        "distance_from_origin_nm": 0,
        "bearing": initial_bearing,
        "name": origin['city'],
        "type": "airport"
    })
    
    # Add intermediate waypoints (real, comprehensive, or generated)
    for wp in real_waypoints:
        distance_from_origin = haversine_distance(
            origin['lat'], origin['lon'],
            wp['lat'], wp['lon']
        )
        
        waypoints.append({
            "number": wp['number'],
            "lat": wp['lat'],
            "lon": wp['lon'],
            "distance_from_origin_nm": round(distance_from_origin, 1),
            "bearing": round(calculate_bearing(wp['lat'], wp['lon'], 
                                              dest['lat'], dest['lon']), 1),
            "name": wp['name'],
            "type": wp.get('type', 'waypoint'),
            "region": wp.get('region', 'N/A')
        })
    
    # Add destination
    waypoints.append({
        "number": num_waypoints + 1,
        "lat": dest['lat'],
        "lon": dest['lon'],
        "distance_from_origin_nm": round(distance_nm, 1),
        "bearing": final_bearing,
        "name": dest['city'],
        "type": "airport"
    })
    
    # Count real waypoints
    real_wp_count = sum(1 for wp in waypoints if wp.get('type') in ['real_waypoint', 'comprehensive_waypoint'])
    
    return {
        "origin": {
            "code": origin['icao'],
            "name": origin['name'],
            "city": origin['city'],
            "lat": origin['lat'],
            "lon": origin['lon']
        },
        "destination": {
            "code": dest['icao'],
            "name": dest['name'],
            "city": dest['city'],
            "lat": dest['lat'],
            "lon": dest['lon']
        },
        "route_type": "Great Circle with Real Waypoints",
        "total_distance_nm": round(distance_nm, 1),
        "initial_bearing": round(initial_bearing, 1),
        "final_bearing": round(final_bearing, 1),
        "waypoints": waypoints,
        "real_waypoints_used": real_wp_count,
        "total_waypoints": len(waypoints) - 2,  # Excluding origin and destination
        "database_used": "comprehensive" if COMPREHENSIVE_DB_AVAILABLE and real_wp_count > 0 else "curated"
    }
    
    # Calculate total distance
    distance_nm = haversine_distance(
        origin['lat'], origin['lon'], 
        dest['lat'], dest['lon']
    )


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great circle distance (same as in airport_database but included here for completeness)"""
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


# ── WIND OPTIMIZATION ─────────────────────────────────────────────────────────

def calculate_wind_correction(true_airspeed_kt: float, 
                              true_heading: float,
                              wind_direction: float, 
                              wind_speed_kt: float) -> Dict:
    """
    Calculate wind correction angle and ground speed.
    
    Args:
        true_airspeed_kt: Aircraft true airspeed in knots
        true_heading: Desired heading in degrees
        wind_direction: Wind FROM direction in degrees
        wind_speed_kt: Wind speed in knots
    
    Returns:
        dict with wind correction angle, ground speed, etc.
    """
    # Convert to radians
    heading_rad = math.radians(true_heading)
    wind_dir_rad = math.radians(wind_direction)
    
    # Wind components
    headwind = wind_speed_kt * math.cos(wind_dir_rad - heading_rad)
    crosswind = wind_speed_kt * math.sin(wind_dir_rad - heading_rad)
    
    # Wind correction angle
    if true_airspeed_kt > 0:
        wca = math.degrees(math.asin(crosswind / true_airspeed_kt))
    else:
        wca = 0
    
    # Ground speed
    ground_speed = math.sqrt(
        (true_airspeed_kt + headwind)**2 + crosswind**2
    )
    
    return {
        "wind_correction_angle": round(wca, 1),
        "ground_speed_kt": round(ground_speed, 1),
        "headwind_component": round(headwind, 1),
        "crosswind_component": round(crosswind, 1),
        "effective_tailwind": round(-headwind, 1)  # Negative headwind = tailwind
    }


def optimize_route_for_winds(route: Dict, 
                             winds_aloft: List[Dict],
                             true_airspeed_kt: float) -> Dict:
    """
    Optimize route considering winds aloft at different waypoints.
    
    Args:
        route: Route dict from generate_route_waypoints()
        winds_aloft: List of wind data at different points
                     Format: [{"lat": x, "lon": y, "wind_dir": z, "wind_spd": w}, ...]
        true_airspeed_kt: Aircraft true airspeed
    
    Returns:
        Updated route with wind corrections and optimized timings
    """
    optimized_waypoints = []
    total_time_hr = 0
    total_distance_nm = 0
    
    for i, waypoint in enumerate(route['waypoints']):
        if i == len(route['waypoints']) - 1:
            break  # Skip last waypoint (destination)
        
        next_waypoint = route['waypoints'][i + 1]
        
        # Get wind data for this segment (simplified: use first wind in list)
        # In production, interpolate winds for each segment
        if winds_aloft:
            wind = winds_aloft[0]
            wind_dir = wind.get('wind_direction', 270)
            wind_spd = wind.get('wind_speed_kt', 0)
        else:
            wind_dir = 270  # Default westerly
            wind_spd = 0
        
        # Calculate bearing to next waypoint
        bearing = calculate_bearing(
            waypoint['lat'], waypoint['lon'],
            next_waypoint['lat'], next_waypoint['lon']
        )
        
        # Calculate wind correction
        correction = calculate_wind_correction(
            true_airspeed_kt, bearing, wind_dir, wind_spd
        )
        
        # Calculate segment distance and time
        segment_distance = haversine_distance(
            waypoint['lat'], waypoint['lon'],
            next_waypoint['lat'], next_waypoint['lon']
        )
        
        segment_time_hr = segment_distance / correction['ground_speed_kt']
        
        total_time_hr += segment_time_hr
        total_distance_nm += segment_distance
        
        optimized_waypoint = {
            **waypoint,
            "bearing_to_next": round(bearing, 1),
            "wind_direction": wind_dir,
            "wind_speed_kt": wind_spd,
            "wind_correction_angle": correction['wind_correction_angle'],
            "ground_speed_kt": correction['ground_speed_kt'],
            "segment_distance_nm": round(segment_distance, 1),
            "segment_time_hr": round(segment_time_hr, 2),
            "cumulative_time_hr": round(total_time_hr, 2)
        }
        optimized_waypoints.append(optimized_waypoint)
    
    # Add final waypoint
    final_waypoint = {
        **route['waypoints'][-1],
        "cumulative_time_hr": round(total_time_hr, 2)
    }
    optimized_waypoints.append(final_waypoint)
    
    return {
        **route,
        "waypoints": optimized_waypoints,
        "total_time_hr": round(total_time_hr, 2),
        "total_time_formatted": format_hours(total_time_hr),
        "average_ground_speed_kt": round(total_distance_nm / total_time_hr, 1) if total_time_hr > 0 else 0,
        "optimized_for_winds": True
    }


def format_hours(hours: float) -> str:
    """Format hours as HH:MM"""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m:02d}m"


# ── DISPLAY FUNCTIONS ─────────────────────────────────────────────────────────

def display_route(route: Dict) -> str:
    """Format route for display"""
    output = "\n" + "═" * 80 + "\n"
    output += "  ✈️  FLIGHT ROUTE PLAN\n"
    output += "═" * 80 + "\n\n"
    
    output += f"**Origin:** {route['origin']['city']} ({route['origin']['code']})\n"
    output += f"**Destination:** {route['destination']['city']} ({route['destination']['code']})\n"
    output += f"**Route Type:** {route['route_type']}\n"
    output += f"**Total Distance:** {route['total_distance_nm']:,.0f} nm\n"
    output += f"**Initial Bearing:** {route['initial_bearing']:.0f}°\n"
    
    if route.get('optimized_for_winds'):
        output += f"**Total Flight Time:** {route['total_time_formatted']}\n"
        output += f"**Average Ground Speed:** {route['average_ground_speed_kt']:.0f} kt\n"
    
    output += "\n**Waypoints:**\n"
    output += "─" * 80 + "\n"
    
    header = f"{'#':<4} {'NAME':<15} {'LAT':<10} {'LON':<11} {'DIST':<8}"
    if route.get('optimized_for_winds'):
        header += f" {'GS':<7} {'TIME':<8} {'CUM TIME':<10}"
    output += header + "\n"
    output += "─" * 80 + "\n"
    
    for wp in route['waypoints']:
        line = f"{wp['number']:<4} {wp['name']:<15} {wp['lat']:<10.4f} {wp['lon']:<11.4f} {wp['distance_from_origin_nm']:<8.0f}"
        
        if route.get('optimized_for_winds') and 'ground_speed_kt' in wp:
            line += f" {wp.get('ground_speed_kt', 0):<7.0f} "
            line += f"{wp.get('segment_time_hr', 0):<8.2f} "
            line += f"{wp.get('cumulative_time_hr', 0):<10.2f}"
        
        output += line + "\n"
    
    output += "═" * 80 + "\n"
    
    return output


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 80)
    print("  ROUTE OPTIMIZATION MODULE TEST")
    print("═" * 80)
    
    # Test 1: Generate basic great circle route
    print("\n📊 Test 1: Great Circle Route KLAX → EGLL")
    print("─" * 80)
    route = generate_route_waypoints("KLAX", "EGLL", num_waypoints=5)
    print(display_route(route))
    
    # Test 2: Optimize with winds
    print("\n📊 Test 2: Wind-Optimized Route KLAX → EGLL")
    print("─" * 80)
    
    # Simulate winds aloft (westerly jet stream)
    winds = [
        {"wind_direction": 270, "wind_speed_kt": 100}  # 100kt headwind from west
    ]
    
    optimized = optimize_route_for_winds(route, winds, true_airspeed_kt=490)
    print(display_route(optimized))
    
    print("\n✅ Route optimization module test complete!\n")
