# database.py
# User Authentication & Flight History Database  
# CLEAN SQLite version - NO PostgreSQL complexity

import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Optional, List, Dict

# Database file
DB_PATH = "flight_planner.db"


# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


# ── DATABASE INITIALIZATION ───────────────────────────────────────────────────

def init_database():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            pilot_license TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # Flight plans table - CLEAN VERSION
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
    
    # Flight history table
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


# ── USER MANAGEMENT ───────────────────────────────────────────────────────────

def create_user(username: str, email: str, password: str, 
               full_name: str = None, pilot_license: str = None) -> Dict:
    """Create a new user account"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, pilot_license)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password_hash, full_name, pilot_license))
        
        user_id = cursor.lastrowid
        
        # Create default preferences
        cursor.execute("""
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
    
    except sqlite3.IntegrityError:
        return {
            "success": False,
            "error": "Username or email already exists"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user with username and password"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute("""
            SELECT user_id, username, email, full_name, pilot_license, created_at
            FROM users
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (result[0],))
            conn.commit()
            
            conn.close()
            
            return {
                "user_id": result[0],
                "username": result[1],
                "email": result[2],
                "full_name": result[3],
                "pilot_license": result[4],
                "created_at": result[5]
            }
        
        conn.close()
        return None
    
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user information by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, email, full_name, pilot_license, created_at
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
                "created_at": result[5]
            }
        return None
    
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


# ── FLIGHT PLAN MANAGEMENT ────────────────────────────────────────────────────

def save_flight_plan(user_id: int, plan_data: Dict) -> Dict:
    """Save a flight plan"""
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
            plan_data.get('plan_name'),
            plan_data.get('aircraft_code'),
            plan_data.get('origin_icao'),
            plan_data.get('destination_icao'),
            plan_data.get('distance_nm'),
            plan_data.get('altitude_ft'),
            plan_data.get('headwind_kt'),
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
        
        return {"success": True, "plan_id": plan_id}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_flight_plans(user_id: int, limit: int = 50) -> List[Dict]:
    """Get all flight plans for a user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plan_id, plan_name, aircraft_code, origin_icao, destination_icao,
                   distance_nm, status, approved, created_at
            FROM flight_plans
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    except Exception as e:
        print(f"Error fetching flight plans: {e}")
        return []


def get_flight_plan_by_id(plan_id: int) -> Optional[Dict]:
    """Get a specific flight plan"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM flight_plans WHERE plan_id = ?
        """, (plan_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            plan = dict(result)
            # Parse JSON fields
            if plan.get('route_data'):
                plan['route_data'] = json.loads(plan['route_data'])
            if plan.get('weather_data'):
                plan['weather_data'] = json.loads(plan['weather_data'])
            if plan.get('airspace_check'):
                plan['airspace_check'] = json.loads(plan['airspace_check'])
            if plan.get('etops_check'):
                plan['etops_check'] = json.loads(plan['etops_check'])
            return plan
        return None
    
    except Exception as e:
        print(f"Error fetching flight plan: {e}")
        return None


def delete_flight_plan(plan_id: int, user_id: int) -> Dict:
    """Delete a flight plan"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM flight_plans
            WHERE plan_id = ? AND user_id = ?
        """, (plan_id, user_id))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            return {"success": True}
        else:
            return {"success": False, "error": "Plan not found or unauthorized"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── STATISTICS ────────────────────────────────────────────────────────────────

def get_user_statistics(user_id: int) -> Dict:
    """Get user statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total plans
        cursor.execute("""
            SELECT COUNT(*), SUM(distance_nm), 
                   SUM(CASE WHEN approved = 1 THEN 1 ELSE 0 END)
            FROM flight_plans
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        total_plans = result[0] or 0
        total_distance = result[1] or 0
        approved_plans = result[2] or 0
        
        # Most used aircraft
        cursor.execute("""
            SELECT aircraft_code, COUNT(*) as count
            FROM flight_plans
            WHERE user_id = ?
            GROUP BY aircraft_code
            ORDER BY count DESC
            LIMIT 1
        """, (user_id,))
        
        aircraft_result = cursor.fetchone()
        most_used_aircraft = aircraft_result[0] if aircraft_result else None
        
        # Flight history count
        cursor.execute("""
            SELECT COUNT(*) FROM flight_history WHERE user_id = ?
        """, (user_id,))
        
        flights_logged = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_plans": total_plans,
            "total_distance_nm": total_distance,
            "approved_plans": approved_plans,
            "most_used_aircraft": most_used_aircraft,
            "total_flights_logged": flights_logged
        }
    
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {}


def log_actual_flight(user_id: int, plan_id: int, flight_data: Dict) -> Dict:
    """Log an actual flight"""
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
            flight_data.get('flight_date'),
            flight_data.get('actual_fuel_used_kg'),
            flight_data.get('actual_flight_time_hr'),
            flight_data.get('notes')
        ))
        
        flight_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"success": True, "flight_id": flight_id}
    
    except Exception as e:
        return {"success": False, "error": str(e)}
