# app_auth.py
# Authenticated Flight Planner with User Accounts
# Run with: streamlit run app_auth.py

import streamlit as st
import openai
from datetime import datetime
from database import (
    init_database, create_user, authenticate_user, get_user_by_id,
    save_flight_plan, get_user_flight_plans, get_flight_plan_by_id,
    delete_flight_plan, get_user_statistics
)
from aircraft_database import lookup_aircraft, AIRCRAFT_DATABASE
from airport_database import AIRPORTS, calculate_route
from fuel_calculator import calculate_fuel
from weather_integration import get_metar
from route_optimization import generate_route_waypoints
from airspace_restrictions import check_route_airspace_violations
from etops_compliance import check_etops_compliance

# Initialize database
init_database()

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Flight Planner - Login",
    page_icon="✈️",
    layout="wide"
)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# ── AUTHENTICATION UI ─────────────────────────────────────────────────────────
def show_login_page():
    """Display login/register page"""
    
    st.markdown("""
    <style>
        .login-header {
            font-size: 3rem;
            font-weight: 900;
            text-align: center;
            background: linear-gradient(135deg, #00d4ff, #7c6cff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .login-subtitle {
            text-align: center;
            color: #8b98b0;
            margin-bottom: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="login-header">✈️ Professional Flight Planner</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Sign in to access your flight planning dashboard</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### Sign In")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"✅ Welcome back, {user['full_name'] or user['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        st.markdown("### Create Account")
        
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            new_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
            
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name (optional)")
            with col2:
                pilot_license = st.text_input("Pilot License (optional)")
            
            register = st.form_submit_button("Create Account", use_container_width=True)
            
            if register:
                if new_password != new_password_confirm:
                    st.error("❌ Passwords do not match")
                elif not new_username or not new_email or not new_password:
                    st.warning("Please fill in all required fields")
                else:
                    result = create_user(new_username, new_email, new_password, full_name, pilot_license)
                    if result['success']:
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error(f"❌ {result['error']}")


# ── MAIN APPLICATION ──────────────────────────────────────────────────────────
def show_main_app():
    """Display main application for logged-in users"""
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        user = st.session_state.user
        st.markdown(f"**{user['full_name'] or user['username']}**")
        st.caption(f"@{user['username']}")
        if user.get('pilot_license'):
            st.caption(f"License: {user['pilot_license']}")
        
        st.markdown("---")
        
        # User statistics
        stats = get_user_statistics(user['user_id'])
        st.markdown("### 📊 Your Statistics")
        st.metric("Total Plans", stats.get('total_plans', 0))
        st.metric("Approved Plans", stats.get('approved_plans', 0))
        st.metric("Total Distance", f"{stats.get('total_distance_nm', 0):,.0f} nm")
        if stats.get('most_used_aircraft'):
            st.metric("Favorite Aircraft", stats['most_used_aircraft'])
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    
    # Main content
    st.markdown(f"# ✈️ Flight Planner - Welcome, {user['full_name'] or user['username']}!")
    
    tab1, tab2, tab3 = st.tabs(["📋 New Flight Plan", "📚 My Flight Plans", "📊 Dashboard"])
    
    # ── TAB 1: CREATE NEW FLIGHT PLAN ────────────────────────────────────────
    with tab1:
        st.markdown("### Create New Flight Plan")
        
        with st.form("new_flight_plan"):
            plan_name = st.text_input("Plan Name", placeholder="e.g., LAX to Tokyo Business Trip")
            
            col1, col2 = st.columns(2)
            with col1:
                aircraft = st.selectbox("Aircraft", options=list(AIRCRAFT_DATABASE.keys()))
                origin = st.selectbox("Origin", options=list(AIRPORTS.keys()),
                                    format_func=lambda x: f"{x} - {AIRPORTS[x]['name']}")
            with col2:
                altitude = st.number_input("Altitude (ft)", value=35000, step=1000)
                destination = st.selectbox("Destination", options=list(AIRPORTS.keys()),
                                         format_func=lambda x: f"{x} - {AIRPORTS[x]['name']}")
            
            headwind = st.slider("Headwind (kt)", -50, 100, 0, 5)
            
            submit_plan = st.form_submit_button("🚀 Generate Flight Plan", use_container_width=True)
        
        if submit_plan:
            with st.spinner("Generating comprehensive flight plan..."):
                # Calculate route
                route = calculate_route(origin, destination)
                
                # Generate route waypoints
                route_detail = generate_route_waypoints(origin, destination, num_waypoints=5)
                
                # Check airspace
                airspace_result = check_route_airspace_violations(
                    route_detail['waypoints'], altitude
                )
                
                # Check ETOPS
                etops_result = check_etops_compliance(aircraft, route_detail['waypoints'])
                
                # Get weather
                origin_wx = get_metar(origin)
                dest_wx = get_metar(destination)
                
                # Calculate fuel
                fuel_result = calculate_fuel(
                    aircraft_code=aircraft,
                    distance_nm=route['distance_nm'],
                    headwind_kt=headwind,
                    include_alternate=True
                )
                
                # Display results
                st.success("✅ Flight plan generated successfully!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Distance", f"{route['distance_nm']:,.0f} nm")
                with col2:
                    st.metric("Fuel Required", f"{fuel_result['total_fuel_kg']:,} kg")
                with col3:
                    st.metric("Flight Time", fuel_result['flight_time_formatted'])
                
                # Safety summary
                st.markdown("#### 🛡️ Safety Checks")
                checks = [
                    ("Airspace Clear", airspace_result['route_clear']),
                    ("ETOPS Compliant", etops_result.get('compliant', True)),
                    ("Fuel Adequate", fuel_result['safe_to_fly']),
                ]
                
                for label, passed in checks:
                    icon = "✅" if passed else "❌"
                    st.markdown(f"{icon} {label}")
                
                # Save to database
                all_approved = all(check[1] for check in checks)
                
                plan_data = {
                    "plan_name": plan_name or f"{origin} to {destination}",
                    "aircraft_code": aircraft,
                    "origin_icao": origin,
                    "destination_icao": destination,
                    "distance_nm": route['distance_nm'],
                    "altitude_ft": altitude,
                    "headwind_kt": headwind,
                    "fuel_required_kg": fuel_result['total_fuel_kg'],
                    "flight_time_hr": fuel_result['flight_time_hr'],
                    "route_data": route_detail,
                    "weather_data": {"origin": origin_wx, "destination": dest_wx},
                    "airspace_check": airspace_result,
                    "etops_check": etops_result,
                    "status": "approved" if all_approved else "review_required",
                    "approved": all_approved
                }
                
                result = save_flight_plan(user['user_id'], plan_data)
                if result['success']:
                    st.success(f"💾 Flight plan saved! Plan ID: {result['plan_id']}")
                else:
                    st.error(f"Failed to save: {result['error']}")
    
    # ── TAB 2: VIEW SAVED PLANS ──────────────────────────────────────────────
    with tab2:
        st.markdown("### My Saved Flight Plans")
        
        plans = get_user_flight_plans(user['user_id'])
        
        if plans:
            for plan in plans:
                with st.expander(f"✈️ {plan['plan_name']} ({plan['created_at'][:10]})"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Aircraft", plan['aircraft_code'])
                    with col2:
                        st.metric("Route", f"{plan['origin_icao']} → {plan['destination_icao']}")
                    with col3:
                        st.metric("Distance", f"{plan['distance_nm']:,.0f} nm")
                    with col4:
                        status_icon = "✅" if plan['approved'] else "⚠️"
                        st.metric("Status", f"{status_icon} {plan['status']}")
                    
                    col_a, col_b, col_c = st.columns([1, 1, 2])
                    with col_a:
                        if st.button("🔍 View Details", key=f"view_{plan['plan_id']}"):
                            full_plan = get_flight_plan_by_id(plan['plan_id'])
                            st.json(full_plan)
                    with col_b:
                        if st.button("🗑️ Delete", key=f"delete_{plan['plan_id']}"):
                            result = delete_flight_plan(plan['plan_id'], user['user_id'])
                            if result['success']:
                                st.success("Deleted!")
                                st.rerun()
        else:
            st.info("No flight plans yet. Create your first plan in the 'New Flight Plan' tab!")
    
    # ── TAB 3: DASHBOARD ──────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Dashboard & Analytics")
        
        stats = get_user_statistics(user['user_id'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Plans", stats.get('total_plans', 0), delta=None)
        with col2:
            st.metric("Approved", stats.get('approved_plans', 0))
        with col3:
            st.metric("Total Miles", f"{stats.get('total_distance_nm', 0):,.0f}")
        with col4:
            st.metric("Flights Logged", stats.get('total_flights_logged', 0))
        
        st.markdown("---")
        
        # Recent activity
        st.markdown("### 📅 Recent Activity")
        recent_plans = get_user_flight_plans(user['user_id'], limit=5)
        
        if recent_plans:
            for plan in recent_plans:
                icon = "✅" if plan['approved'] else "⚠️"
                st.markdown(f"{icon} **{plan['plan_name']}** - {plan['origin_icao']} → {plan['destination_icao']} ({plan['created_at'][:10]})")
        else:
            st.info("No recent activity")


# ── MAIN ROUTING ──────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    show_main_app()
else:
    show_login_page()
