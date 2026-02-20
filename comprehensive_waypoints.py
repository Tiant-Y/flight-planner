# comprehensive_waypoints.py
# Load comprehensive waypoint database from OurAirports (free database with 50,000+ waypoints)
# Data source: https://ourairports.com/data/

import csv
import urllib.request
import os
from typing import Dict, List, Optional

# ── DATABASE URLS ─────────────────────────────────────────────────────────────
NAVAIDS_URL = "https://davidmegginson.github.io/ourairports-data/navaids.csv"
CACHE_FILE = "navaids_database.csv"

# ── WAYPOINT DATABASE ─────────────────────────────────────────────────────────
WAYPOINT_DATABASE = {}


def download_waypoint_database(force_refresh: bool = False) -> None:
    """
    Download the comprehensive waypoint database from OurAirports.
    This includes VORs, NDBs, DMEs, and waypoints worldwide.
    
    Args:
        force_refresh: Force download even if cache exists
    """
    if os.path.exists(CACHE_FILE) and not force_refresh:
        print(f"✅ Using cached database: {CACHE_FILE}")
        return
    
    print(f"📥 Downloading comprehensive waypoint database...")
    print(f"   Source: {NAVAIDS_URL}")
    
    try:
        urllib.request.urlretrieve(NAVAIDS_URL, CACHE_FILE)
        print(f"✅ Database downloaded: {CACHE_FILE}")
    except Exception as e:
        print(f"❌ Error downloading database: {e}")
        raise


def load_waypoint_database() -> Dict[str, Dict]:
    """
    Load waypoint database from CSV file.
    Returns dict with waypoint identifiers as keys.
    """
    global WAYPOINT_DATABASE
    
    if not os.path.exists(CACHE_FILE):
        download_waypoint_database()
    
    print(f"📖 Loading waypoint database...")
    
    waypoints = {}
    
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract relevant fields
            ident = row.get('ident', '').strip().upper()
            
            if not ident:
                continue
            
            try:
                lat = float(row.get('latitude_deg', 0))
                lon = float(row.get('longitude_deg', 0))
            except (ValueError, TypeError):
                continue
            
            waypoint = {
                'ident': ident,
                'name': row.get('name', ''),
                'type': row.get('type', ''),  # VOR, NDB, DME, WAYPOINT, etc.
                'lat': lat,
                'lon': lon,
                'frequency': row.get('frequency_khz', ''),
                'country': row.get('iso_country', ''),
                'region': row.get('iso_region', ''),
            }
            
            waypoints[ident] = waypoint
    
    WAYPOINT_DATABASE = waypoints
    print(f"✅ Loaded {len(waypoints):,} waypoints from database")
    
    return waypoints


def find_waypoint(ident: str) -> Optional[Dict]:
    """
    Find a waypoint by identifier (e.g., 'IGARI', 'VCENT')
    
    Args:
        ident: Waypoint identifier
    
    Returns:
        Waypoint dict or None if not found
    """
    if not WAYPOINT_DATABASE:
        load_waypoint_database()
    
    return WAYPOINT_DATABASE.get(ident.upper())


def find_waypoints_in_region(min_lat: float, max_lat: float, 
                             min_lon: float, max_lon: float,
                             waypoint_types: List[str] = None) -> List[Dict]:
    """
    Find all waypoints in a geographic region.
    
    Args:
        min_lat, max_lat: Latitude bounds
        min_lon, max_lon: Longitude bounds
        waypoint_types: Filter by type (e.g., ['WAYPOINT', 'VOR'])
    
    Returns:
        List of waypoints in the region
    """
    if not WAYPOINT_DATABASE:
        load_waypoint_database()
    
    results = []
    
    for wp in WAYPOINT_DATABASE.values():
        if min_lat <= wp['lat'] <= max_lat and min_lon <= wp['lon'] <= max_lon:
            if waypoint_types is None or wp['type'] in waypoint_types:
                results.append(wp)
    
    return results


def find_waypoints_near_route(origin_lat: float, origin_lon: float,
                              dest_lat: float, dest_lon: float,
                              corridor_width_nm: float = 100) -> List[Dict]:
    """
    Find waypoints along a route corridor.
    
    Args:
        origin_lat, origin_lon: Origin coordinates
        dest_lat, dest_lon: Destination coordinates
        corridor_width_nm: Width of search corridor in nautical miles
    
    Returns:
        List of waypoints along the route
    """
    import math
    
    if not WAYPOINT_DATABASE:
        load_waypoint_database()
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 3440.065 * c  # nautical miles
    
    def point_to_line_distance(px, py, x1, y1, x2, y2):
        """Calculate perpendicular distance from point to line"""
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return haversine_distance(px, py, x1, y1)
        
        param = dot / len_sq
        
        if param < 0:
            xx = x1
            yy = y1
        elif param > 1:
            xx = x2
            yy = y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D
        
        return haversine_distance(px, py, xx, yy)
    
    # Find waypoints within corridor
    route_waypoints = []
    
    for wp in WAYPOINT_DATABASE.values():
        # Calculate distance from waypoint to route line
        distance_from_route = point_to_line_distance(
            wp['lat'], wp['lon'],
            origin_lat, origin_lon,
            dest_lat, dest_lon
        )
        
        if distance_from_route <= corridor_width_nm:
            # Calculate distance from origin
            dist_from_origin = haversine_distance(
                origin_lat, origin_lon,
                wp['lat'], wp['lon']
            )
            
            route_waypoints.append({
                **wp,
                'distance_from_origin_nm': round(dist_from_origin, 1),
                'distance_from_route_nm': round(distance_from_route, 1)
            })
    
    # Sort by distance from origin
    route_waypoints.sort(key=lambda x: x['distance_from_origin_nm'])
    
    return route_waypoints


def generate_realistic_route(origin_lat: float, origin_lon: float,
                            dest_lat: float, dest_lon: float,
                            num_waypoints: int = 5) -> List[Dict]:
    """
    Generate a realistic route using actual waypoints from the database.
    
    Args:
        origin_lat, origin_lon: Origin coordinates
        dest_lat, dest_lon: Destination coordinates
        num_waypoints: Desired number of intermediate waypoints
    
    Returns:
        List of waypoints along the route
    """
    # Find all waypoints along the route
    candidates = find_waypoints_near_route(
        origin_lat, origin_lon,
        dest_lat, dest_lon,
        corridor_width_nm=150
    )
    
    if not candidates:
        return []
    
    # Calculate total route distance
    import math
    def haversine_distance(lat1, lon1, lat2, lon2):
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 3440.065 * c
    
    total_distance = haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    
    # Select waypoints at regular intervals
    selected_waypoints = []
    segment_distance = total_distance / (num_waypoints + 1)
    
    for i in range(1, num_waypoints + 1):
        target_distance = segment_distance * i
        
        # Find closest waypoint to target distance
        closest_wp = min(
            candidates,
            key=lambda wp: abs(wp['distance_from_origin_nm'] - target_distance)
        )
        
        if closest_wp not in selected_waypoints:
            selected_waypoints.append(closest_wp)
    
    return selected_waypoints[:num_waypoints]


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 70)
    print("  COMPREHENSIVE WAYPOINT DATABASE TEST")
    print("═" * 70)
    
    # Load database
    load_waypoint_database()
    
    # Test 1: Find specific waypoints
    print("\n📊 Test 1: Find famous waypoints")
    print("─" * 70)
    famous_waypoints = ["IGARI", "VCENT", "BOBOB", "NYLON", "PIANO"]
    for ident in famous_waypoints:
        wp = find_waypoint(ident)
        if wp:
            print(f"✅ {ident}: {wp['name']} at ({wp['lat']:.4f}, {wp['lon']:.4f}) - {wp['type']}")
        else:
            print(f"❌ {ident}: Not found")
    
    # Test 2: Find waypoints in Southeast Asia
    print("\n📊 Test 2: Waypoints in Southeast Asia region")
    print("─" * 70)
    sea_waypoints = find_waypoints_in_region(
        min_lat=0, max_lat=15,
        min_lon=95, max_lon=110,
        waypoint_types=['WAYPOINT']
    )
    print(f"Found {len(sea_waypoints)} waypoints in Southeast Asia")
    for wp in sea_waypoints[:10]:
        print(f"  {wp['ident']}: ({wp['lat']:.2f}, {wp['lon']:.2f})")
    
    # Test 3: Find waypoints along Singapore-Hong Kong route
    print("\n📊 Test 3: Waypoints along Singapore → Hong Kong route")
    print("─" * 70)
    route_wps = generate_realistic_route(
        origin_lat=1.3644, origin_lon=103.9915,  # Singapore
        dest_lat=22.3080, dest_lon=113.9185,      # Hong Kong
        num_waypoints=5
    )
    print(f"Selected {len(route_wps)} waypoints for route:")
    for i, wp in enumerate(route_wps, 1):
        print(f"  {i}. {wp['ident']}: {wp['distance_from_origin_nm']:.0f} nm from origin")
    
    print("\n✅ Database test complete!")
    print(f"📁 Database cached at: {CACHE_FILE}")
    print("💡 This database will be reused on future runs (no re-download needed)\n")
