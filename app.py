# app.py
# Streamlit Web Interface for AI Flight Planner
# Run with: streamlit run app.py

import streamlit as st
import openai
from aircraft_database import lookup_aircraft, AIRCRAFT_DATABASE
from fuel_calculator import calculate_fuel
from ai_flight_planner import chat_with_ai
import json

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Flight Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stAlert {
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .safety-check {
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        font-weight: 500;
    }
    .check-pass {
        background-color: #d4edda;
        color: #155724;
    }
    .check-fail {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# ── INITIALIZE SESSION STATE ──────────────────────────────────────────────────
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'last_fuel_result' not in st.session_state:
    st.session_state.last_fuel_result = None

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # API Key input (optional if environment variable is set)
    api_key_input = st.text_input(
        "OpenAI API Key", 
        type="password",
        help="Leave empty if using environment variable",
        key="api_key"
    )
    
    if api_key_input:
        openai.api_key = api_key_input
    
    st.markdown("---")
    
    # Quick aircraft lookup
    st.markdown("### 🔍 Quick Aircraft Lookup")
    aircraft_query = st.text_input("Enter aircraft code", placeholder="e.g., 777, A380")
    
    if aircraft_query:
        result = lookup_aircraft(aircraft_query)
        if result:
            st.success(f"**{result['full_name']}**")
            st.metric("MTOW", f"{result['mtow_kg']:,} kg")
            st.metric("MLW", f"{result['mlw_kg']:,} kg")
            st.metric("Max Fuel", f"{result['max_fuel_kg']:,} kg")
            st.metric("Range", f"{result['range_nm']:,} nm")
            if result['etops_minutes']:
                st.info(f"ETOPS: {result['etops_minutes']} min")
        else:
            st.error("Aircraft not found")
    
    st.markdown("---")
    
    # Available aircraft
    with st.expander("📋 Available Aircraft"):
        for code in sorted(AIRCRAFT_DATABASE.keys()):
            st.text(f"• {code}")
    
    st.markdown("---")
    
    # Clear conversation button
    if st.button("🔄 Clear Conversation"):
        st.session_state.conversation_history = None
        st.session_state.chat_messages = []
        st.session_state.last_fuel_result = None
        st.rerun()

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">✈️ AI Flight Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Professional flight planning powered by AI • Phase 1 System</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "📊 Manual Calculator", "ℹ️ About"])

# ── TAB 1: AI CHAT ────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Chat with AI Flight Planner")
    st.markdown("Ask me anything about flight planning, fuel calculations, or aircraft data!")
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("e.g., Plan a flight from KLAX to EGLL with a 777"):
        # Add user message to chat
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    result = chat_with_ai(prompt, st.session_state.conversation_history)
                    response = result["assistant_message"]
                    st.session_state.conversation_history = result["conversation_history"]
                    
                    st.markdown(response)
                    
                    # Store response
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    
                    # If fuel was calculated, store it for display
                    if result["function_calls"]:
                        for call in result["function_calls"]:
                            if call["function"] == "calculate_fuel" and "error" not in call["result"]:
                                st.session_state.last_fuel_result = call["result"]
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("💡 Make sure your OpenAI API key is set correctly in the sidebar or as an environment variable.")
    
    # Display detailed fuel report if available
    if st.session_state.last_fuel_result:
        st.markdown("---")
        st.markdown("### 📊 Detailed Fuel Report")
        display_fuel_report(st.session_state.last_fuel_result)

# ── TAB 2: MANUAL CALCULATOR ──────────────────────────────────────────────────
with tab2:
    st.markdown("### Manual Fuel Calculator")
    st.markdown("Calculate fuel requirements without AI assistance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        aircraft_input = st.selectbox(
            "Aircraft Type",
            options=list(AIRCRAFT_DATABASE.keys()),
            help="Select aircraft from database"
        )
        
        distance_input = st.number_input(
            "Distance (nautical miles)",
            min_value=0,
            max_value=15000,
            value=5400,
            step=100
        )
    
    with col2:
        headwind_input = st.number_input(
            "Headwind (knots)",
            min_value=-200,
            max_value=200,
            value=0,
            step=5,
            help="Negative = tailwind"
        )
        
        include_alternate = st.checkbox("Include alternate airport fuel", value=True)
    
    if st.button("Calculate Fuel", type="primary"):
        with st.spinner("Calculating..."):
            result = calculate_fuel(
                aircraft_code=aircraft_input,
                distance_nm=distance_input,
                headwind_kt=headwind_input,
                include_alternate=include_alternate
            )
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("✅ Calculation complete!")
                display_fuel_report(result)

# ── TAB 3: ABOUT ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### About This System")
    
    st.markdown("""
    This is a **Phase 1 AI Flight Planner** built with:
    - 🤖 OpenAI GPT-4o for natural language understanding
    - ✈️ 18 aircraft performance database (Boeing, Airbus, Embraer)
    - 📊 ICAO-compliant fuel calculation engine
    - 🌐 Streamlit web interface
    
    #### Current Capabilities
    - Aircraft performance data lookup (MTOW, MLW, fuel capacity, range)
    - Complete fuel planning (trip, contingency, alternate, reserve, taxi)
    - Safety checks (MTOW/MLW compliance, range verification)
    - ETOPS rating awareness
    - Natural language query processing
    
    #### Fuel Calculation Standards
    - **Trip Fuel**: Distance ÷ Speed × Burn Rate
    - **Contingency**: 5% of trip fuel (ICAO minimum)
    - **Alternate**: 45 minutes flight time
    - **Reserve**: 30 minutes holding
    - **Taxi**: 200 kg fixed
    
    #### Coming in Phase 2
    - Real-time weather integration
    - Route optimization algorithms
    - Airspace restriction checks
    - ETOPS diversion airport verification
    - Multi-leg flight planning
    
    ---
    
    **⚠️ Disclaimer**: This is a demonstration system for educational purposes. 
    Always use certified flight planning tools for real operations.
    """)

# ── HELPER FUNCTION: DISPLAY FUEL REPORT ──────────────────────────────────────
def display_fuel_report(result):
    """Display a formatted fuel report in Streamlit"""
    
    # Header with aircraft info
    col1, col2, col3 = st.columns(3)
    col1.metric("Aircraft", result['aircraft'])
    col2.metric("Distance", f"{result['distance_nm']:,.0f} nm")
    col3.metric("Flight Time", result['flight_time_formatted'])
    
    st.markdown("---")
    
    # Fuel breakdown
    st.markdown("#### 💧 Fuel Breakdown")
    
    fuel_col1, fuel_col2 = st.columns(2)
    
    with fuel_col1:
        st.metric("Trip Fuel", f"{result['trip_fuel_kg']:,} kg")
        st.metric("Contingency (5%)", f"{result['contingency_fuel_kg']:,} kg")
        st.metric("Alternate", f"{result['alternate_fuel_kg']:,} kg")
    
    with fuel_col2:
        st.metric("Reserve (30 min)", f"{result['reserve_fuel_kg']:,} kg")
        st.metric("Taxi", f"{result['taxi_fuel_kg']:,} kg")
        st.metric("**TOTAL REQUIRED**", f"**{result['total_fuel_kg']:,} kg**")
    
    # Progress bar for fuel capacity
    fuel_percentage = (result['total_fuel_kg'] / result['max_fuel_capacity_kg']) * 100
    st.progress(min(fuel_percentage / 100, 1.0))
    st.caption(f"Using {fuel_percentage:.1f}% of fuel capacity ({result['max_fuel_capacity_kg']:,} kg max)")
    
    st.markdown("---")
    
    # Safety checks
    st.markdown("#### ✓ Safety Checks")
    
    checks = [
        ("Fuel fits in tanks", result['fuel_fits_in_tanks']),
        ("Under MTOW at takeoff", result['under_mtow']),
        ("Under MLW at landing", result['under_mlw']),
        ("Within aircraft range", result['within_range']),
    ]
    
    for label, passed in checks:
        if passed:
            st.markdown(f'<div class="safety-check check-pass">✅ {label}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="safety-check check-fail">❌ {label}</div>', unsafe_allow_html=True)
    
    # ETOPS warning
    if result['etops_warning']:
        st.warning(result['etops_warning'])
    
    # Overall status
    st.markdown("---")
    if result['safe_to_fly']:
        st.success("✅ **ALL CHECKS PASSED — SAFE TO PLAN THIS FLIGHT**")
    else:
        st.error("❌ **ONE OR MORE CHECKS FAILED — REVIEW BEFORE FLIGHT**")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
    'Built with Python + OpenAI + Streamlit | Phase 1 System | For Educational Use Only'
    '</div>',
    unsafe_allow_html=True
)
