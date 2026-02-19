# weather_integration.py
# Real-time Aviation Weather Integration
# Uses free FAA Aviation Weather Center API

import requests
import json
from datetime import datetime
from typing import Optional


# ── API CONFIGURATION ─────────────────────────────────────────────────────────
# Using FAA Aviation Weather Center (free, no API key required)
BASE_URL = "https://aviationweather.gov/api/data"


# ── METAR (CURRENT WEATHER) ───────────────────────────────────────────────────
def get_metar(airport_code: str) -> dict:
    """
    Get current weather (METAR) for an airport.
    
    Args:
        airport_code: ICAO code (e.g., "KLAX", "EGLL")
    
    Returns:
        dict with weather data or error
    """
    try:
        url = f"{BASE_URL}/metar"
        params = {
            "ids": airport_code.upper(),
            "format": "json",
            "taf": "false",
            "hours": "2"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return {"error": f"No METAR data available for {airport_code}"}
        
        # Parse the most recent METAR
        metar = data[0] if isinstance(data, list) else data
        
        return {
            "airport": airport_code.upper(),
            "raw_text": metar.get("rawOb", ""),
            "observation_time": metar.get("reportTime", ""),
            "temp_c": metar.get("temp"),
            "dewpoint_c": metar.get("dewp"),
            "wind_dir": metar.get("wdir"),
            "wind_speed_kt": metar.get("wspd"),
            "wind_gust_kt": metar.get("wgst"),
            "visibility_sm": metar.get("visib"),
            "altimeter_inhg": metar.get("altim"),
            "flight_category": metar.get("fltcat"),  # VFR, MVFR, IFR, LIFR
            "clouds": metar.get("clouds", []),
            "weather": metar.get("wxString", ""),
        }
    
    except requests.RequestException as e:
        return {"error": f"Failed to fetch METAR: {str(e)}"}
    except Exception as e:
        return {"error": f"Error parsing METAR: {str(e)}"}


# ── TAF (FORECAST) ────────────────────────────────────────────────────────────
def get_taf(airport_code: str) -> dict:
    """
    Get Terminal Area Forecast (TAF) for an airport.
    
    Args:
        airport_code: ICAO code (e.g., "KLAX", "EGLL")
    
    Returns:
        dict with forecast data or error
    """
    try:
        url = f"{BASE_URL}/taf"
        params = {
            "ids": airport_code.upper(),
            "format": "json",
            "hours": "24"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return {"error": f"No TAF data available for {airport_code}"}
        
        taf = data[0] if isinstance(data, list) else data
        
        return {
            "airport": airport_code.upper(),
            "raw_text": taf.get("rawTAF", ""),
            "issue_time": taf.get("issueTime", ""),
            "valid_time_from": taf.get("validTimeFrom", ""),
            "valid_time_to": taf.get("validTimeTo", ""),
            "forecast": taf.get("fcsts", []),
        }
    
    except requests.RequestException as e:
        return {"error": f"Failed to fetch TAF: {str(e)}"}
    except Exception as e:
        return {"error": f"Error parsing TAF: {str(e)}"}


# ── WINDS ALOFT ───────────────────────────────────────────────────────────────
def get_winds_aloft(lat: float, lon: float, altitude_ft: int = 35000) -> dict:
    """
    Get winds aloft forecast for a specific location and altitude.
    
    Args:
        lat: Latitude
        lon: Longitude  
        altitude_ft: Altitude in feet (typical cruise: 30000-42000)
    
    Returns:
        dict with wind data (direction, speed, temperature) or error
    
    Note: This is a simplified implementation. For production, you'd use
    NOAA's GFS wind data or commercial wind forecast APIs.
    """
    try:
        # For demonstration, we'll use a placeholder
        # In production, integrate with NOAA GFS data or commercial APIs
        
        # Example: https://nomads.ncep.noaa.gov/
        # Real implementation would fetch gridded wind data
        
        # Placeholder response
        return {
            "lat": lat,
            "lon": lon,
            "altitude_ft": altitude_ft,
            "wind_direction": 270,  # Example: westerly wind
            "wind_speed_kt": 65,    # Example: 65 knot wind
            "temperature_c": -50,
            "note": "This is placeholder data. Integrate NOAA GFS or commercial API for real winds aloft."
        }
    
    except Exception as e:
        return {"error": f"Error fetching winds aloft: {str(e)}"}


# ── SIGMETS / AIRMETS (HAZARDOUS WEATHER) ─────────────────────────────────────
def get_sigmets(region: str = "US") -> list:
    """
    Get SIGMETs (Significant Meteorological Information) for hazardous weather.
    
    Args:
        region: Region code (e.g., "US", "EU")
    
    Returns:
        list of active SIGMETs
    """
    try:
        url = f"{BASE_URL}/airsigmet"
        params = {
            "format": "json",
            "level": "sigmet",
            "hazard": "all"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        sigmets = []
        for item in data:
            sigmets.append({
                "id": item.get("airsigmetId"),
                "hazard": item.get("hazard"),
                "severity": item.get("severity"),
                "valid_time_from": item.get("validTimeFrom"),
                "valid_time_to": item.get("validTimeTo"),
                "raw_text": item.get("rawAIRSIGMET", ""),
            })
        
        return sigmets
    
    except Exception as e:
        return [{"error": f"Error fetching SIGMETs: {str(e)}"}]


# ── ROUTE WEATHER SUMMARY ─────────────────────────────────────────────────────
def get_route_weather_summary(origin_icao: str, dest_icao: str) -> dict:
    """
    Get a comprehensive weather summary for a route.
    
    Args:
        origin_icao: Origin airport ICAO code
        dest_icao: Destination airport ICAO code
    
    Returns:
        dict with origin weather, destination weather, and route hazards
    """
    print(f"\n🌤️  Fetching weather for route {origin_icao} → {dest_icao}...\n")
    
    # Get METARs
    origin_metar = get_metar(origin_icao)
    dest_metar = get_metar(dest_icao)
    
    # Get TAFs
    origin_taf = get_taf(origin_icao)
    dest_taf = get_taf(dest_icao)
    
    # Get SIGMETs
    sigmets = get_sigmets()
    
    return {
        "origin": {
            "airport": origin_icao,
            "current_weather": origin_metar,
            "forecast": origin_taf,
        },
        "destination": {
            "airport": dest_icao,
            "current_weather": dest_metar,
            "forecast": dest_taf,
        },
        "route_hazards": sigmets,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# ── WEATHER DISPLAY FUNCTIONS ─────────────────────────────────────────────────
def format_metar_display(metar: dict) -> str:
    """Format METAR data for human-readable display"""
    if "error" in metar:
        return f"❌ {metar['error']}"
    
    output = f"**Current Weather at {metar['airport']}**\n"
    output += f"Time: {metar.get('observation_time', 'N/A')}\n"
    
    if metar.get('temp_c') is not None:
        output += f"Temperature: {metar['temp_c']}°C\n"
    
    if metar.get('wind_speed_kt') is not None:
        wind_dir = metar.get('wind_dir', 'VRB')
        wind_spd = metar['wind_speed_kt']
        gust = metar.get('wind_gust_kt')
        wind_text = f"Wind: {wind_dir}° at {wind_spd} kt"
        if gust:
            wind_text += f" gusting {gust} kt"
        output += wind_text + "\n"
    
    if metar.get('visibility_sm'):
        output += f"Visibility: {metar['visibility_sm']} SM\n"
    
    flight_cat = metar.get('flight_category')
    if flight_cat:
        cat_emoji = {"VFR": "🟢", "MVFR": "🟡", "IFR": "🟠", "LIFR": "🔴"}.get(flight_cat, "⚪")
        output += f"Flight Category: {cat_emoji} {flight_cat}\n"
    
    if metar.get('weather'):
        output += f"Weather: {metar['weather']}\n"
    
    output += f"\nRaw METAR: {metar.get('raw_text', 'N/A')}"
    
    return output


def format_weather_summary(summary: dict) -> str:
    """Format complete route weather summary"""
    output = "\n" + "═" * 70 + "\n"
    output += "  🌤️  ROUTE WEATHER BRIEFING\n"
    output += "═" * 70 + "\n\n"
    
    # Origin weather
    output += "📍 ORIGIN\n"
    output += "─" * 70 + "\n"
    output += format_metar_display(summary['origin']['current_weather']) + "\n\n"
    
    # Destination weather
    output += "📍 DESTINATION\n"
    output += "─" * 70 + "\n"
    output += format_metar_display(summary['destination']['current_weather']) + "\n\n"
    
    # Hazardous weather
    hazards = summary.get('route_hazards', [])
    if hazards and not any('error' in h for h in hazards):
        output += "⚠️  ROUTE HAZARDS\n"
        output += "─" * 70 + "\n"
        for sigmet in hazards[:5]:  # Show first 5
            output += f"• {sigmet.get('hazard', 'Unknown')} - {sigmet.get('severity', 'N/A')}\n"
        output += "\n"
    
    output += "═" * 70 + "\n"
    output += f"Briefing time: {summary['timestamp']}\n"
    output += "═" * 70 + "\n"
    
    return output


# ── QUICK TEST ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "═" * 70)
    print("  AVIATION WEATHER MODULE TEST")
    print("═" * 70)
    
    # Test METAR
    print("\n📊 Test 1: Current Weather (METAR) for KLAX")
    print("─" * 70)
    metar = get_metar("KLAX")
    print(format_metar_display(metar))
    
    # Test route weather
    print("\n\n📊 Test 2: Route Weather Summary")
    print("─" * 70)
    summary = get_route_weather_summary("KLAX", "KJFK")
    print(format_weather_summary(summary))
    
    print("\n✅ Weather module test complete!")
    print("Note: Install 'requests' if not already: pip install requests\n")
