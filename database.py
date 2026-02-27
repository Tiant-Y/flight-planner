# database.py
# FIXED VERSION - 2026-02-27
# User Authentication & Flight History Database
# Supports both SQLite (local) and PostgreSQL (production)

import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Optional, List, Dict
import os

# Try to import PostgreSQL driver
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


# ── DATABASE CONFIGURATION ────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection string from Supabase

if DATABASE_URL and POSTGRES_AVAILABLE:
    USE_POSTGRES = True
    print("✅ Using PostgreSQL (persistent database)")
else:
    USE_POSTGRES = False
    DB_PATH = "flight_planner.db"
    print("⚠️ Using SQLite (local database - will reset on cloud deployment)")


# ── DATABASE CONNECTION ───────────────────────────────────────────────────────

def get_connection():
    """Get database connection (PostgreSQL or SQLite)"""
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


# ── DATABASE INITIALIZATION ───────────────────────────────────────────────────

def init_database():
    """Initialize database with required tables (works with SQLite or PostgreSQL)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Adjust SQL for PostgreSQL vs SQLite
    if USE_POSTGRES:
        # PostgreSQL uses SERIAL for auto-increment
        user_id_type = "SERIAL PRIMARY KEY"
        plan_id_type = "SERIAL PRIMARY KEY"
        flight_id_type = "SERIAL PRIMARY KEY"
        timestamp_default = "DEFAULT CURRENT_TIMESTAMP"
    else:
        # SQLite uses INTEGER PRIMARY KEY AUTOINCREMENT
        user_id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        plan_id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        flight_id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        timestamp_default = "DEFAULT CURRENT_TIMESTAMP"
    
    # Users table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            user_id {user_id_type},
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            pilot_license TEXT,
            created_at TIMESTAMP {timestamp_default},
            last_login TIMESTAMP
        )
    """)
    
    # Flight plans table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS flight_plans (
            plan_id {plan_id_type},
            user_id INTEGER NOT NULL,
            plan_name TEXT,
            aircraft_code TEXT NOT NULL,
            origin_icao TEXT NOT NULL,
            destination_icao TEXT NOT NULL,
            distance_nm REAL,
            altitude_ft INTEGER,
            headwind_kt REAL,
            fuel_required_kg REAL,
            flight_time_hr REAL,
            route_data TEXT,
            weather_data TEXT,
            airspace_check TEXT,
            etops_check TEXT,
            status TEXT DEFAULT 'draft',
            approved BOOLEAN DEFAULT false,
            created_at TIMESTAMP {timestamp_default},
            updated_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Flight history table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS flight_history (
            flight_id {flight_id_type},
            user_id INTEGER NOT NULL,
            plan_id INTEGER,
            flight_date DATE,
            actual_fuel_used_kg REAL,
            actual_flight_time_hr REAL,
            notes TEXT,
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (plan_id) REFERENCES flight_plans(plan_id)
        )
    """)
    
    # User preferences table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            preferred_units TEXT DEFAULT 'metric',
            default_aircraft TEXT,
            default_altitude_ft INTEGER DEFAULT 35000,
            enable_notifications BOOLEAN DEFAULT true,
            theme TEXT DEFAULT 'dark',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")
    
    # Flight plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flight_plans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_name TEXT,
            aircraft_code TEXT NOT NULL,
            origin_icao TEXT NOT NULL,
            destination_icao TEXT NOT NULL,
            distance_nm REAL,
            altitude_ft INTEGER,
            headwind_kt REAL,
            fuel_required_kg REAL,
            flight_time_hr REAL,
            route_data TEXT,
            weather_data TEXT,
            airspace_check TEXT,
            etops_check TEXT,
            status TEXT DEFAULT 'draft',
            approved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Flight history table (actual flights)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flight_history (
            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id INTEGER,
            flight_date DATE,
            actual_fuel_used_kg REAL,
            actual_flight_time_hr REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (plan_id) REFERENCES flight_plans(plan_id)
        )
    """)
    
    # User preferences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            preferred_units TEXT DEFAULT 'metric',
            default_aircraft TEXT,
            default_altitude_ft INTEGER DEFAULT 35000,
            enable_notifications BOOLEAN DEFAULT 1,
            theme TEXT DEFAULT 'dark',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


# ── USER AUTHENTICATION ───────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, email: str, password: str, 
               full_name: str = None, pilot_license: str = None) -> Dict:
    """
    Create a new user account
    
    Returns:
        dict with success status and user_id or error message
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, pilot_license)
            VALUES (%s, %s, %s, %s, %s) RETURNING user_id
        """ if USE_POSTGRES else """
            INSERT INTO users (username, email, password_hash, full_name, pilot_license)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password_hash, full_name, pilot_license))
        
        if USE_POSTGRES:
            user_id = cursor.fetchone()[0]
        else:
            user_id = cursor.lastrowid
        
        # Create default preferences
        cursor.execute("""
            INSERT INTO user_preferences (user_id)
            VALUES (%s)
        """ if USE_POSTGRES else """
            INSERT INTO user_preferences (user_id)
            VALUES (?)
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "user_id": user_id,
            "message": f"User '{username}' created successfully"
        }
    
    except Exception as e:
        error_msg = str(e)
        if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            return {
                "success": False,
                "error": "Username or email already exists"
            }
        return {
            "success": False,
            "error": str(e)
        }


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user with username and password
    
    Returns:
        User dict if successful, None if failed
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute("""
            SELECT user_id, username, email, full_name, pilot_license, created_at
            FROM users
            WHERE username = %s AND password_hash = %s
        """ if USE_POSTGRES else """
            SELECT user_id, username, email, full_name, pilot_license, created_at
            FROM users
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            if USE_POSTGRES:
                user_data = result
            else:
                user_data = dict(result)
            
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """ if USE_POSTGRES else """
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_data['user_id'] if USE_POSTGRES else user_data['user_id'],))
            conn.commit()
            
            conn.close()
            
            return {
                "user_id": user_data['user_id'] if USE_POSTGRES else user_data['user_id'],
                "username": user_data['username'] if USE_POSTGRES else user_data['username'],
                "email": user_data['email'] if USE_POSTGRES else user_data['email'],
                "full_name": user_data['full_name'] if USE_POSTGRES else user_data['full_name'],
                "pilot_license": user_data['pilot_license'] if USE_POSTGRES else user_data['pilot_license'],
                "created_at": str(user_data['created_at']) if USE_POSTGRES else user_data['created_at']
            }
        
        conn.close()
        return None
    
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user information by user ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, email, full_name, pilot_license, created_at, last_login
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "user_id": result[0],
                "username": result[1],
                "email": result[2],
                "full_name": result[3],
                "pilot_license": result[4],
                "created_at": result[5],
                "last_login": result[6]
            }
        return None
    
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


# ── FLIGHT PLANS ──────────────────────────────────────────────────────────────

def save_flight_plan(user_id: int, plan_data: Dict) -> Dict:
    """
    Save a flight plan to the database
    
    Args:
        user_id: User ID
        plan_data: dict with flight plan details
    
    Returns:
        dict with success status and plan_id
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO flight_plans (
                user_id, plan_name, aircraft_code, origin_icao, destination_icao,
                distance_nm, altitude_ft, headwind_kt, fuel_required_kg, flight_time_hr,
                route_data, weather_data, airspace_check, etops_check, status, approved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            plan_data.get('plan_name', f"Plan {datetime.now().strftime('%Y%m%d_%H%M')}"),
            plan_data['aircraft_code'],
            plan_data['origin_icao'],
            plan_data['destination_icao'],
            plan_data.get('distance_nm'),
            plan_data.get('altitude_ft', 35000),
            plan_data.get('headwind_kt', 0),
            plan_data.get('fuel_required_kg'),
            plan_data.get('flight_time_hr'),
            json.dumps(plan_data.get('route_data')),
            json.dumps(plan_data.get('weather_data')),
            json.dumps(plan_data.get('airspace_check')),
            json.dumps(plan_data.get('etops_check')),
            plan_data.get('status', 'draft'),
            plan_data.get('approved', False)
        ))
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "plan_id": plan_id,
            "message": "Flight plan saved successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_user_flight_plans(user_id: int, limit: int = 50) -> List[Dict]:
    """Get all flight plans for a user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plan_id, plan_name, aircraft_code, origin_icao, destination_icao,
                   distance_nm, fuel_required_kg, flight_time_hr, status, approved,
                   created_at, updated_at
            FROM flight_plans
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        plans = []
        for row in results:
            plans.append({
                "plan_id": row[0],
                "plan_name": row[1],
                "aircraft_code": row[2],
                "origin_icao": row[3],
                "destination_icao": row[4],
                "distance_nm": row[5],
                "fuel_required_kg": row[6],
                "flight_time_hr": row[7],
                "status": row[8],
                "approved": bool(row[9]),
                "created_at": row[10],
                "updated_at": row[11]
            })
        
        return plans
    
    except Exception as e:
        print(f"Error fetching flight plans: {e}")
        return []


def get_flight_plan_by_id(plan_id: int) -> Optional[Dict]:
    """Get detailed flight plan by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plan_id, user_id, plan_name, aircraft_code, origin_icao, destination_icao,
                   distance_nm, altitude_ft, headwind_kt, fuel_required_kg, flight_time_hr,
                   route_data, weather_data, airspace_check, etops_check, status, approved,
                   created_at, updated_at
            FROM flight_plans
            WHERE plan_id = ?
        """, (plan_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "plan_id": row[0],
                "user_id": row[1],
                "plan_name": row[2],
                "aircraft_code": row[3],
                "origin_icao": row[4],
                "destination_icao": row[5],
                "distance_nm": row[6],
                "altitude_ft": row[7],
                "headwind_kt": row[8],
                "fuel_required_kg": row[9],
                "flight_time_hr": row[10],
                "route_data": json.loads(row[11]) if row[11] else None,
                "weather_data": json.loads(row[12]) if row[12] else None,
                "airspace_check": json.loads(row[13]) if row[13] else None,
                "etops_check": json.loads(row[14]) if row[14] else None,
                "status": row[15],
                "approved": bool(row[16]),
                "created_at": row[17],
                "updated_at": row[18]
            }
        return None
    
    except Exception as e:
        print(f"Error fetching flight plan: {e}")
        return None


def delete_flight_plan(plan_id: int, user_id: int) -> Dict:
    """Delete a flight plan (user can only delete their own plans)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM flight_plans
            WHERE plan_id = ? AND user_id = ?
        """, (plan_id, user_id))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            return {"success": True, "message": "Flight plan deleted"}
        else:
            return {"success": False, "error": "Flight plan not found or access denied"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── FLIGHT HISTORY ────────────────────────────────────────────────────────────

def log_actual_flight(user_id: int, plan_id: int, flight_data: Dict) -> Dict:
    """Log an actual flight execution"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO flight_history (
                user_id, plan_id, flight_date, actual_fuel_used_kg,
                actual_flight_time_hr, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            plan_id,
            flight_data.get('flight_date', datetime.now().date()),
            flight_data.get('actual_fuel_used_kg'),
            flight_data.get('actual_flight_time_hr'),
            flight_data.get('notes')
        ))
        
        flight_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "flight_id": flight_id,
            "message": "Flight logged successfully"
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_statistics(user_id: int) -> Dict:
    """Get statistics for a user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total flight plans
        cursor.execute("SELECT COUNT(*) FROM flight_plans WHERE user_id = ?", (user_id,))
        total_plans = cursor.fetchone()[0]
        
        # Approved plans
        cursor.execute("SELECT COUNT(*) FROM flight_plans WHERE user_id = ? AND approved = 1", (user_id,))
        approved_plans = cursor.fetchone()[0]
        
        # Total distance
        cursor.execute("SELECT SUM(distance_nm) FROM flight_plans WHERE user_id = ?", (user_id,))
        total_distance = cursor.fetchone()[0] or 0
        
        # Total flights logged
        cursor.execute("SELECT COUNT(*) FROM flight_history WHERE user_id = ?", (user_id,))
        total_flights = cursor.fetchone()[0]
        
        # Most used aircraft
        cursor.execute("""
            SELECT aircraft_code, COUNT(*) as count
            FROM flight_plans
            WHERE user_id = ?
            GROUP BY aircraft_code
            ORDER BY count DESC
            LIMIT 1
        """, (user_id,))
        most_used = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_plans": total_plans,
            "approved_plans": approved_plans,
            "total_distance_nm": round(total_distance, 1),
            "total_flights_logged": total_flights,
            "most_used_aircraft": most_used[0] if most_used else None
        }
    
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return {}


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 70)
    print("  DATABASE MODULE TEST")
    print("═" * 70 + "\n")
    
    # Initialize database
    init_database()
    
    # Test user creation
    print("📊 Test 1: Create User")
    print("─" * 70)
    result = create_user(
        username="pilot123",
        email="pilot@example.com",
        password="securepassword",
        full_name="John Doe",
        pilot_license="ATP-12345"
    )
    print(f"Result: {result}\n")
    
    # Test authentication
    print("📊 Test 2: Authenticate User")
    print("─" * 70)
    user = authenticate_user("pilot123", "securepassword")
    if user:
        print(f"✅ Authenticated: {user['username']} (ID: {user['user_id']})")
        user_id = user['user_id']
    else:
        print("❌ Authentication failed")
        user_id = None
    print()
    
    # Test save flight plan
    if user_id:
        print("📊 Test 3: Save Flight Plan")
        print("─" * 70)
        plan_data = {
            "plan_name": "Test Flight LAX-JFK",
            "aircraft_code": "B777-300ER",
            "origin_icao": "KLAX",
            "destination_icao": "KJFK",
            "distance_nm": 2475,
            "fuel_required_kg": 85000,
            "flight_time_hr": 5.5,
            "approved": True
        }
        result = save_flight_plan(user_id, plan_data)
        print(f"Result: {result}\n")
        
        # Test get flight plans
        print("📊 Test 4: Retrieve Flight Plans")
        print("─" * 70)
        plans = get_user_flight_plans(user_id)
        print(f"Found {len(plans)} flight plan(s)")
        for plan in plans:
            print(f"  • {plan['plan_name']}: {plan['origin_icao']} → {plan['destination_icao']}")
        print()
        
        # Test statistics
        print("📊 Test 5: User Statistics")
        print("─" * 70)
        stats = get_user_statistics(user_id)
        print(f"Total Plans: {stats['total_plans']}")
        print(f"Approved Plans: {stats['approved_plans']}")
        print(f"Total Distance: {stats['total_distance_nm']} nm")
        print()
    
    print("✅ Database module test complete!")
    print(f"📁 Database file: {DB_PATH}\n")
