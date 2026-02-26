# weather_checkwx.py
# Enhanced Weather Integration using CheckWX API
# Better data quality and parsing than raw FAA data
# Free tier: 400 requests/day

import requests
from typing import Dict, Optional
import os

# CheckWX API (Free tier: 400 requests/day)
# Sign up at: https://www.checkwxapi.com
CHECKWX_API_KEY = os.getenv("CHECKWX_API_KEY", "")  # Get free API key from CheckWX
CHECKWX_BASE_URL = "https://api.checkwx.com"


def get_metar_checkwx(station_code: str) -> Dict:
    """
    Get METAR data from CheckWX API (better parsing than raw FAA)
    
    Args:
        station_code: ICAO airport code (e.g., 'KLAX')
    
    Returns:
        dict with decoded weather data
    """
    if not CHECKWX_API_KEY:
        # Fallback to FAA if no API key
        from weather_integration import get_metar as get_metar_faa
        return get_metar_faa(station_code)
    
    try:
        headers = {"X-API-Key": CHECKWX_API_KEY}
        url = f"{CHECKWX_BASE_URL}/metar/{station_code}/decoded"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('results') > 0 and data.get('data'):
                metar_data = data['data'][0]
                
                # Extract key fields
                return {
                    "station": station_code,
                    "raw_text": metar_data.get('raw_text', ''),
                    "observed_time": metar_data.get('observed', ''),
                    
                    # Temperature
                    "temp_c": metar_data.get('temperature', {}).get('celsius'),
                    "temp_f": metar_data.get('temperature', {}).get('fahrenheit'),
                    "dewpoint_c": metar_data.get('dewpoint', {}).get('celsius'),
                    
                    # Wind
                    "wind_dir": metar_data.get('wind', {}).get('degrees'),
                    "wind_speed_kt": metar_data.get('wind', {}).get('speed_kts'),
                    "wind_gust_kt": metar_data.get('wind', {}).get('gust_kts'),
                    
                    # Visibility
                    "visibility_sm": metar_data.get('visibility', {}).get('miles'),
                    "visibility_m": metar_data.get('visibility', {}).get('meters'),
                    
                    # Pressure
                    "altimeter_inhg": metar_data.get('barometer', {}).get('hg'),
                    "altimeter_mb": metar_data.get('barometer', {}).get('mb'),
                    
                    # Conditions
                    "flight_category": metar_data.get('flight_category', 'UNKNOWN'),
                    "clouds": metar_data.get('clouds', []),
                    "conditions": metar_data.get('conditions', []),
                    
                    # Humidity
                    "humidity_percent": metar_data.get('humidity', {}).get('percent'),
                    
                    "error": None
                }
        
        return {"error": f"No METAR data available for {station_code}"}
    
    except Exception as e:
        return {"error": str(e)}


def get_taf_checkwx(station_code: str) -> Dict:
    """
    Get TAF (Terminal Area Forecast) from CheckWX
    
    Args:
        station_code: ICAO airport code
    
    Returns:
        dict with forecast data
    """
    if not CHECKWX_API_KEY:
        from weather_integration import get_taf as get_taf_faa
        return get_taf_faa(station_code)
    
    try:
        headers = {"X-API-Key": CHECKWX_API_KEY}
        url = f"{CHECKWX_BASE_URL}/taf/{station_code}/decoded"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('results') > 0 and data.get('data'):
                taf_data = data['data'][0]
                
                return {
                    "station": station_code,
                    "raw_text": taf_data.get('raw_text', ''),
                    "issued_time": taf_data.get('timestamp', {}).get('issued'),
                    "valid_from": taf_data.get('timestamp', {}).get('from'),
                    "valid_to": taf_data.get('timestamp', {}).get('to'),
                    "forecast": taf_data.get('forecast', []),
                    "error": None
                }
        
        return {"error": f"No TAF data available for {station_code}"}
    
    except Exception as e:
        return {"error": str(e)}


def get_winds_aloft_checkwx(station_code: str) -> Dict:
    """
    Get winds aloft forecast
    
    Args:
        station_code: ICAO airport code
    
    Returns:
        dict with winds aloft data
    """
    try:
        headers = {"X-API-Key": CHECKWX_API_KEY}
        url = f"{CHECKWX_BASE_URL}/windsaloft/{station_code}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data
        
        return {"error": f"No winds aloft data for {station_code}"}
    
    except Exception as e:
        return {"error": str(e)}


# ── INTEGRATION WITH EXISTING SYSTEM ──────────────────────────────────────────

def get_metar(station_code: str) -> Dict:
    """
    Get METAR with automatic fallback:
    1. Try CheckWX (if API key available)
    2. Fallback to FAA Aviation Weather
    """
    if CHECKWX_API_KEY:
        result = get_metar_checkwx(station_code)
        if not result.get('error'):
            return result
    
    # Fallback to FAA
    from weather_integration import get_metar as get_metar_faa
    return get_metar_faa(station_code)


def get_taf(station_code: str) -> Dict:
    """
    Get TAF with automatic fallback
    """
    if CHECKWX_API_KEY:
        result = get_taf_checkwx(station_code)
        if not result.get('error'):
            return result
    
    # Fallback to FAA
    from weather_integration import get_taf as get_taf_faa
    return get_taf_faa(station_code)


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 70)
    print("  CHECKWX API TEST")
    print("═" * 70)
    
    if not CHECKWX_API_KEY:
        print("\n⚠️  No CheckWX API key found!")
        print("   Sign up for free at: https://www.checkwxapi.com")
        print("   Then set: export CHECKWX_API_KEY=your-key")
        print("\n   Falling back to FAA Aviation Weather...\n")
    else:
        print(f"\n✅ Using CheckWX API (key: {CHECKWX_API_KEY[:10]}...)")
    
    # Test METAR
    print("\n📊 Test: METAR for KLAX")
    print("─" * 70)
    metar = get_metar("KLAX")
    
    if not metar.get('error'):
        print(f"Station: {metar.get('station')}")
        print(f"Temperature: {metar.get('temp_c')}°C / {metar.get('temp_f')}°F")
        print(f"Wind: {metar.get('wind_dir')}° at {metar.get('wind_speed_kt')} kt")
        print(f"Visibility: {metar.get('visibility_sm')} miles")
        print(f"Flight Category: {metar.get('flight_category')}")
        print(f"Humidity: {metar.get('humidity_percent')}%")
    else:
        print(f"Error: {metar.get('error')}")
    
    # Test TAF
    print("\n📊 Test: TAF for KJFK")
    print("─" * 70)
    taf = get_taf("KJFK")
    
    if not taf.get('error'):
        print(f"Station: {taf.get('station')}")
        print(f"Issued: {taf.get('issued_time')}")
        print(f"Valid: {taf.get('valid_from')} to {taf.get('valid_to')}")
        print(f"Periods: {len(taf.get('forecast', []))}")
    else:
        print(f"Error: {taf.get('error')}")
    
    print("\n✅ Weather test complete!\n")
