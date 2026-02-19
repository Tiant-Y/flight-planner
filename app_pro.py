# app_pro.py
# Professional Production-Ready Flight Planning Web Interface
# Integrates all Phase 1 & Phase 2 features
# Run with: streamlit run app_pro.py

import streamlit as st
import openai
import json
from datetime import datetime
from aircraft_database import lookup_aircraft, AIRCRAFT_DATABASE
from airport_database import lookup_airport, AIRPORTS, calculate_route
from fuel_calculator import calculate_fuel
from weather_integration import get_metar, get_route_weather_summary
from route_optimization import generate_route_waypoints, display_route
from airspace_restrictions import check_route_airspace_violations, format_airspace_report
from etops_compliance import check_etops_compliance, format_etops_report
from ai_flight_planner import chat_with_ai

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Professional Flight Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff 0%, #7c6cff 50%, #00ffb3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .subtitle {
        color: #8b98b0;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .phase-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00d4ff, #7c6cff);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-left: 8px;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #00d4ff;
    }
    
    /* Safety indicators */
    .safety-check {
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        font-weight: 500;
        border-left: 4px solid;
    }
    .check-pass {
        background-color: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    .check-fail {
        background-color: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }
    .check-warn {
        background-color: #fff3cd;
        border-color: #ffc107;
        color: #856404;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(124,108,255,0.1));
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Status indicators */
    .status-critical { color: #dc3545; font-weight: 700; }
    .status-warning { color: #ffc107; font-weight: 700; }
    .status-ok { color: #28a745; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INITIALIZATION ──────────────────────────────────────────────
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'flight_plan' not in st.session_state:
    st.session_state.flight_plan = None
if 'flight_history' not in st.session_state:
    st.session_state.flight_history = []

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # API Key
    api_key_input = st.text_input(
        "OpenAI API Key", 
        type="password",
        help="Required for AI features",
        key="api_key"
    )
    if api_key_input:
        openai.api_key = api_key_input
    
    st.markdown("---")
    
    # System Status
    st.markdown("## 📊 System Status")
    
    features = {
        "Aircraft Database": "✅ 18 types",
        "Airport Database": "✅ 60+ airports",
        "Weather Integration": "✅ Real-time",
        "Route Optimization": "✅ Active",
        "Airspace Checking": "✅ 12+ zones",
        "ETOPS Compliance": "✅ Enabled",
    }
    
    for feature, status in features.items():
        st.text(f"{feature}: {status}")
    
    st.markdown("---")
    
    # Quick Links
    st.markdown("## 🔗 Quick Access")
    
    if st.button("📋 View Flight History"):
        st.session_state.show_history = True
    
    if st.button("🔄 Clear Conversation"):
        st.session_state.conversation_history = None
        st.session_state.chat_messages = []
        st.session_state.flight_plan = None
        st.rerun()
    
    if st.button("💾 Export Current Plan"):
        if st.session_state.flight_plan:
            st.download_button(
                "Download as JSON",
                data=json.dumps(st.session_state.flight_plan, indent=2),
                file_name=f"flight_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    st.markdown("---")
    
    # System Info
    st.markdown("## ℹ️ About")
    st.markdown("""
    **Phase 2 Complete System**
    
    - ✈️ Professional flight planning
    - 🌐 Real-time weather data
    - 🗺️ Route optimization
    - 🚫 Airspace restrictions
    - ✓ ETOPS compliance
    - 🤖 AI-powered assistance
    
    Version 2.0.0 | Feb 2026
    """)

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">✈️ Professional Flight Planner<span class="phase-badge">PHASE 2</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Complete aviation flight planning with real-time data, route optimization, and safety verification</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 AI Assistant", 
    "📊 Manual Planner", 
    "🗺️ Route Builder",
    "📈 Flight History",
    "📖 Documentation"
])

# ── TAB 1: AI ASSISTANT ───────────────────────────────────────────────────────
with tab1:
    st.markdown("### AI-Powered Flight Planning")
    st.markdown("Ask anything about flight planning, and the AI will use all available tools to help you.")
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("e.g., Plan a complete flight from LAX to Tokyo with a B777, check weather, route, airspace, and ETOPS"):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your request..."):
                try:
                    result = chat_with_ai(prompt, st.session_state.conversation_history)
                    response = result["assistant_message"]
                    st.session_state.conversation_history = result["conversation_history"]
                    
                    st.markdown(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    
                    # Store flight plan data if generated
                    if result.get("function_calls"):
                        st.session_state.flight_plan = {
                            "timestamp": datetime.now().isoformat(),
                            "query": prompt,
                            "results": result["function_calls"]
                        }
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("💡 Make sure your OpenAI API key is set in the sidebar.")

# ── TAB 2: MANUAL PLANNER ─────────────────────────────────────────────────────
with tab2:
    st.markdown("### Manual Flight Planning Tool")
    st.markdown("Step-by-step flight planning with manual controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Flight Details")
        aircraft_input = st.selectbox(
            "Aircraft Type",
            options=list(AIRCRAFT_DATABASE.keys()),
            help="Select from 18 aircraft types"
        )
        
        origin_input = st.selectbox(
            "Origin Airport",
            options=list(AIRPORTS.keys()),
            format_func=lambda x: f"{x} - {AIRPORTS[x]['name']}"
        )
        
        dest_input = st.selectbox(
            "Destination Airport",
            options=[x for x in AIRPORTS.keys() if x != origin_input],
            format_func=lambda x: f"{x} - {AIRPORTS[x]['name']}"
        )
    
    with col2:
        st.markdown("#### Conditions")
        
        headwind_input = st.number_input(
            "Headwind (knots)",
            min_value=-200,
            max_value=200,
            value=0,
            step=5,
            help="Negative = tailwind"
        )
        
        altitude_input = st.number_input(
            "Cruise Altitude (feet)",
            min_value=20000,
            max_value=45000,
            value=35000,
            step=1000
        )
        
        include_alternate = st.checkbox("Include alternate airport fuel", value=True)
    
    st.markdown("---")
    
    if st.button("🚀 Generate Complete Flight Plan", type="primary", use_container_width=True):
        with st.spinner("Generating comprehensive flight plan..."):
            
            # Step 1: Calculate route
            route = calculate_route(origin_input, dest_input)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Distance", f"{route['distance_nm']:,.0f} nm")
            with col_b:
                st.metric("Origin", route['origin']['city'])
            with col_c:
                st.metric("Destination", route['destination']['city'])
            
            # Step 2: Generate route with waypoints
            st.markdown("#### 🗺️ Route Plan")
            route_detail = generate_route_waypoints(origin_input, dest_input, num_waypoints=5)
            
            if route_detail:
                waypoints_df = []
                for wp in route_detail['waypoints']:
                    waypoints_df.append({
                        "#": wp['number'],
                        "Name": wp['name'],
                        "Latitude": f"{wp['lat']:.4f}",
                        "Longitude": f"{wp['lon']:.4f}",
                        "Distance (nm)": f"{wp['distance_from_origin_nm']:.0f}",
                        "Bearing": f"{wp.get('bearing', 0):.0f}°"
                    })
                st.dataframe(waypoints_df, use_container_width=True)
            
            # Step 3: Check airspace
            st.markdown("#### 🚫 Airspace Analysis")
            airspace_result = check_route_airspace_violations(
                route_detail['waypoints'], 
                altitude_input
            )
            
            if airspace_result['route_clear']:
                st.success("✅ Route is clear of all restricted airspace")
            else:
                st.error(f"❌ {len(airspace_result['critical_violations'])} critical airspace violation(s) detected")
                for v in airspace_result['critical_violations']:
                    st.warning(f"Waypoint {v['waypoint_number']}: {v['zone_name']} ({v['type']})")
            
            # Step 4: Check ETOPS
            st.markdown("#### ✈️ ETOPS Compliance")
            etops_result = check_etops_compliance(aircraft_input, route_detail['waypoints'])
            
            if etops_result.get('reason') == 'not_required':
                st.info(etops_result['message'])
            elif etops_result.get('compliant'):
                st.success(f"✅ {etops_result['message']}")
            else:
                st.error(f"❌ {etops_result['message']}")
            
            # Step 5: Weather
            st.markdown("#### 🌤️ Weather Conditions")
            weather_col1, weather_col2 = st.columns(2)
            
            with weather_col1:
                origin_wx = get_metar(origin_input)
                if not origin_wx.get('error'):
                    st.markdown(f"**{origin_input}** (Origin)")
                    st.metric("Wind", f"{origin_wx.get('wind_dir', 'N/A')}° at {origin_wx.get('wind_speed_kt', 0)} kt")
                    st.metric("Temp", f"{origin_wx.get('temp_c', 'N/A')}°C")
                    flight_cat = origin_wx.get('flight_category', 'N/A')
                    cat_color = {"VFR": "🟢", "MVFR": "🟡", "IFR": "🟠", "LIFR": "🔴"}.get(flight_cat, "⚪")
                    st.metric("Conditions", f"{cat_color} {flight_cat}")
            
            with weather_col2:
                dest_wx = get_metar(dest_input)
                if not dest_wx.get('error'):
                    st.markdown(f"**{dest_input}** (Destination)")
                    st.metric("Wind", f"{dest_wx.get('wind_dir', 'N/A')}° at {dest_wx.get('wind_speed_kt', 0)} kt")
                    st.metric("Temp", f"{dest_wx.get('temp_c', 'N/A')}°C")
                    flight_cat = dest_wx.get('flight_category', 'N/A')
                    cat_color = {"VFR": "🟢", "MVFR": "🟡", "IFR": "🟠", "LIFR": "🔴"}.get(flight_cat, "⚪")
                    st.metric("Conditions", f"{cat_color} {flight_cat}")
            
            # Step 6: Fuel calculation
            st.markdown("#### ⛽ Fuel Requirements")
            fuel_result = calculate_fuel(
                aircraft_code=aircraft_input,
                distance_nm=route['distance_nm'],
                headwind_kt=headwind_input,
                include_alternate=include_alternate
            )
            
            fuel_col1, fuel_col2, fuel_col3 = st.columns(3)
            with fuel_col1:
                st.metric("Trip Fuel", f"{fuel_result['trip_fuel_kg']:,} kg")
                st.metric("Contingency", f"{fuel_result['contingency_fuel_kg']:,} kg")
            with fuel_col2:
                st.metric("Alternate", f"{fuel_result['alternate_fuel_kg']:,} kg")
                st.metric("Reserve", f"{fuel_result['reserve_fuel_kg']:,} kg")
            with fuel_col3:
                st.metric("**TOTAL REQUIRED**", f"**{fuel_result['total_fuel_kg']:,} kg**")
                st.metric("Flight Time", fuel_result['flight_time_formatted'])
            
            # Fuel capacity check
            fuel_pct = (fuel_result['total_fuel_kg'] / fuel_result['max_fuel_capacity_kg']) * 100
            st.progress(min(fuel_pct / 100, 1.0))
            st.caption(f"Using {fuel_pct:.1f}% of fuel capacity")
            
            # Final safety summary
            st.markdown("---")
            st.markdown("### 📋 Flight Plan Summary")
            
            all_checks_passed = (
                airspace_result['route_clear'] and
                (etops_result.get('compliant', True) or etops_result.get('reason') == 'not_required') and
                fuel_result['safe_to_fly']
            )
            
            if all_checks_passed:
                st.success("✅ **FLIGHT PLAN APPROVED** - All safety checks passed")
            else:
                st.error("❌ **FLIGHT PLAN REQUIRES REVIEW** - See warnings above")
            
            # Save to history
            st.session_state.flight_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "aircraft": aircraft_input,
                "route": f"{origin_input} → {dest_input}",
                "distance_nm": route['distance_nm'],
                "approved": all_checks_passed
            })

# ── TAB 3: ROUTE BUILDER ──────────────────────────────────────────────────────
with tab3:
    st.markdown("### Interactive Route Builder")
    st.markdown("Build and visualize custom flight routes")
    
    st.info("🚧 Enhanced route visualization with map integration coming soon!")
    
    rb_col1, rb_col2 = st.columns(2)
    
    with rb_col1:
        rb_origin = st.selectbox(
            "Origin",
            options=list(AIRPORTS.keys()),
            key="rb_origin",
            format_func=lambda x: f"{x} - {AIRPORTS[x]['city']}"
        )
    
    with rb_col2:
        rb_dest = st.selectbox(
            "Destination",
            options=[x for x in AIRPORTS.keys() if x != rb_origin],
            key="rb_dest",
            format_func=lambda x: f"{x} - {AIRPORTS[x]['city']}"
        )
    
    rb_waypoints = st.slider("Number of waypoints", 3, 10, 5)
    
    if st.button("Generate Route"):
        route = generate_route_waypoints(rb_origin, rb_dest, num_waypoints=rb_waypoints)
        
        st.markdown(f"**Total Distance:** {route['total_distance_nm']:,.0f} nm")
        st.markdown(f"**Initial Bearing:** {route['initial_bearing']:.0f}°")
        
        st.markdown("#### Waypoints")
        for wp in route['waypoints']:
            st.text(f"{wp['number']}. {wp['name']}: {wp['lat']:.4f}, {wp['lon']:.4f} ({wp['distance_from_origin_nm']:.0f} nm from origin)")

# ── TAB 4: FLIGHT HISTORY ─────────────────────────────────────────────────────
with tab4:
    st.markdown("### Flight Planning History")
    
    if st.session_state.flight_history:
        st.markdown(f"**Total Plans:** {len(st.session_state.flight_history)}")
        
        for i, flight in enumerate(reversed(st.session_state.flight_history[-10:])):
            with st.expander(f"✈️ {flight['route']} ({flight['aircraft']}) - {flight['timestamp']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Aircraft", flight['aircraft'])
                with col2:
                    st.metric("Distance", f"{flight['distance_nm']:,.0f} nm")
                with col3:
                    status = "✅ Approved" if flight['approved'] else "⚠️ Review Required"
                    st.markdown(f"**Status:** {status}")
    else:
        st.info("No flight plans in history yet. Create one in the Manual Planner or AI Assistant tabs!")

# ── TAB 5: DOCUMENTATION ──────────────────────────────────────────────────────
with tab5:
    st.markdown("### System Documentation")
    
    with st.expander("📖 Getting Started"):
        st.markdown("""
        **Quick Start Guide:**
        
        1. Enter your OpenAI API key in the sidebar
        2. Choose your planning method:
           - **AI Assistant**: Natural language queries
           - **Manual Planner**: Step-by-step guided planning
        3. Review all safety checks before flight
        
        **System Requirements:**
        - OpenAI API key (for AI features)
        - Internet connection (for weather data)
        """)
    
    with st.expander("✈️ Aircraft Database"):
        st.markdown(f"**{len(AIRCRAFT_DATABASE)} aircraft types available:**")
        for code, ac in list(AIRCRAFT_DATABASE.items())[:5]:
            st.text(f"• {code}: {ac['full_name']} (MTOW: {ac['mtow_kg']:,} kg)")
        st.text("... and 13 more")
    
    with st.expander("🌐 Airport Database"):
        st.markdown(f"**{len(AIRPORTS)} major airports worldwide**")
        st.text("Covering: North America, Europe, Asia, Oceania, Middle East, Africa, South America")
    
    with st.expander("🔧 Phase 2 Features"):
        st.markdown("""
        **Completed Features:**
        
        ✅ **Real-time Weather Integration**
        - METAR (current weather)
        - TAF (forecasts)
        - SIGMETs (hazardous weather)
        
        ✅ **Route Optimization**
        - Great circle routing
        - Waypoint generation
        - Wind optimization
        
        ✅ **Airspace Restrictions**
        - No-fly zones
        - Conflict zones
        - Restricted areas
        
        ✅ **ETOPS Compliance**
        - Twin-engine verification
        - Diversion airport checking
        - ETOPS-60 to ETOPS-240 support
        """)
    
    with st.expander("⚠️ Disclaimers"):
        st.markdown("""
        **Important Notes:**
        
        - This is a demonstration system for educational purposes
        - Always use certified flight planning tools for real operations
        - Weather data is for reference only
        - Verify all information with official sources
        - Not approved for commercial aviation use
        """)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
    '✈️ Professional Flight Planner v2.0 | Phase 2 Complete System | '
    'Built with Python, OpenAI, Streamlit | For Educational Use Only'
    '</div>',
    unsafe_allow_html=True
)
