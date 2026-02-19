# training_data_generator.py
# Generate training data for fine-tuning GPT-4o on aviation flight planning

import json
import random
from aircraft_database import AIRCRAFT_DATABASE, lookup_aircraft
from airport_database import AIRPORTS, calculate_route
from fuel_calculator import calculate_fuel

# ── SYSTEM PROMPT FOR FINE-TUNED MODEL ───────────────────────────────────────
SYSTEM_PROMPT = """You are an expert AI flight planning assistant for professional pilots.

You have deep knowledge of:
- Aircraft performance (MTOW, MLW, fuel capacity, range, ETOPS ratings)
- Airport locations and distances worldwide
- ICAO fuel planning standards
- Aviation safety procedures

You provide accurate, safety-focused flight planning assistance with precise calculations.
Always present fuel breakdowns clearly and flag any safety concerns."""


# ── TRAINING EXAMPLE TEMPLATES ───────────────────────────────────────────────

def generate_aircraft_lookup_examples(count=10):
    """Generate examples of aircraft information queries"""
    examples = []
    aircraft_list = list(AIRCRAFT_DATABASE.keys())
    
    templates = [
        "What's the MTOW of a {aircraft}?",
        "Tell me about the {aircraft}",
        "What are the specs for a {aircraft}?",
        "Is the {aircraft} ETOPS rated?",
        "What's the maximum fuel capacity of a {aircraft}?",
        "What's the range of a {aircraft}?",
        "Can you give me the MLW for a {aircraft}?",
    ]
    
    for _ in range(count):
        aircraft_code = random.choice(aircraft_list)
        aircraft_data = AIRCRAFT_DATABASE[aircraft_code]
        query = random.choice(templates).format(aircraft=aircraft_code)
        
        # Generate response
        response = f"""The {aircraft_data['full_name']} has the following specifications:

**Weight Limits:**
- MTOW (Maximum Takeoff Weight): {aircraft_data['mtow_kg']:,} kg
- MLW (Maximum Landing Weight): {aircraft_data['mlw_kg']:,} kg

**Fuel & Range:**
- Maximum Fuel Capacity: {aircraft_data['max_fuel_kg']:,} kg
- Range: {aircraft_data['range_nm']:,} nautical miles
- Cruise Fuel Burn: ~{aircraft_data['fuel_burn_kgh']:,} kg/hour

**Operations:**
- Typical Cruise Speed: {aircraft_data['typical_cruise_ktas']} KTAS"""

        if aircraft_data['etops_minutes']:
            response += f"\n- ETOPS Rating: {aircraft_data['etops_minutes']} minutes ✅"
        else:
            response += "\n- ETOPS Rating: Not ETOPS certified (twin-engine long-range overwater operations not authorized)"
        
        response += f"\n- Typical Passenger Capacity: {aircraft_data['pax_typical']} passengers"
        
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
                {"role": "assistant", "content": response}
            ]
        })
    
    return examples


def generate_route_distance_examples(count=15):
    """Generate examples of route distance queries"""
    examples = []
    airport_codes = list(AIRPORTS.keys())
    
    templates = [
        "What's the distance from {origin} to {dest}?",
        "How far is it from {origin} to {dest}?",
        "Calculate distance between {origin} and {dest}",
        "Distance {origin} to {dest}",
    ]
    
    for _ in range(count):
        origin = random.choice(airport_codes)
        dest = random.choice([a for a in airport_codes if a != origin])
        
        route = calculate_route(origin, dest)
        if "error" in route:
            continue
        
        query = random.choice(templates).format(
            origin=route['origin']['city'], 
            dest=route['destination']['city']
        )
        
        response = f"""**Route: {route['origin']['city']} → {route['destination']['city']}**

- Origin: {route['origin']['name']} ({route['origin']['icao']})
- Destination: {route['destination']['name']} ({route['destination']['icao']})
- Great Circle Distance: {route['distance_nm']:,.0f} nautical miles ({route['distance_km']:,.0f} km)"""
        
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
                {"role": "assistant", "content": response}
            ]
        })
    
    return examples


def generate_fuel_planning_examples(count=30):
    """Generate comprehensive flight planning examples"""
    examples = []
    aircraft_list = list(AIRCRAFT_DATABASE.keys())
    airport_codes = list(AIRPORTS.keys())
    
    templates = [
        "Plan a flight from {origin} to {dest} with a {aircraft}",
        "Calculate fuel for {aircraft} from {origin} to {dest}",
        "I need a fuel plan for {aircraft}, flying {origin} to {dest}",
        "Help me plan a flight: {aircraft} from {origin} to {dest}",
        "{aircraft} flight from {origin} to {dest}, what fuel do I need?",
    ]
    
    for _ in range(count):
        aircraft_code = random.choice(aircraft_list)
        origin = random.choice(airport_codes)
        dest = random.choice([a for a in airport_codes if a != origin])
        
        route = calculate_route(origin, dest)
        if "error" in route:
            continue
        
        # Random headwind between -20 and +40 knots
        headwind = random.randint(-20, 40)
        
        # Calculate fuel
        fuel_result = calculate_fuel(
            aircraft_code=aircraft_code,
            distance_nm=route['distance_nm'],
            headwind_kt=headwind,
            include_alternate=True
        )
        
        if "error" in fuel_result:
            continue
        
        query = random.choice(templates).format(
            aircraft=aircraft_code,
            origin=route['origin']['city'],
            dest=route['destination']['city']
        )
        
        # Generate detailed response
        wind_text = f"{abs(headwind)} kt {'headwind' if headwind > 0 else 'tailwind'}" if headwind != 0 else "No wind"
        
        response = f"""**Flight Plan: {route['origin']['city']} → {route['destination']['city']}**

**Aircraft:** {fuel_result['aircraft']}
**Route:** {route['origin']['icao']} → {route['destination']['icao']}
**Distance:** {fuel_result['distance_nm']:,.0f} nm
**Conditions:** {wind_text}
**Estimated Flight Time:** {fuel_result['flight_time_formatted']}

**Fuel Requirements (ICAO Standard):**
- Trip Fuel: {fuel_result['trip_fuel_kg']:,} kg
- Contingency (5%): {fuel_result['contingency_fuel_kg']:,} kg
- Alternate Fuel: {fuel_result['alternate_fuel_kg']:,} kg
- Final Reserve (30 min): {fuel_result['reserve_fuel_kg']:,} kg
- Taxi Fuel: {fuel_result['taxi_fuel_kg']:,} kg

**Total Fuel Required: {fuel_result['total_fuel_kg']:,} kg**
(Tank capacity: {fuel_result['max_fuel_capacity_kg']:,} kg)

**Safety Checks:**"""

        checks = [
            ("Fuel fits in tanks", fuel_result['fuel_fits_in_tanks']),
            ("Under MTOW at takeoff", fuel_result['under_mtow']),
            ("Under MLW at landing", fuel_result['under_mlw']),
            ("Within aircraft range", fuel_result['within_range']),
        ]
        
        for label, passed in checks:
            response += f"\n- {'✅' if passed else '❌'} {label}"
        
        if fuel_result['etops_warning']:
            response += f"\n\n⚠️ {fuel_result['etops_warning']}"
        
        if fuel_result['safe_to_fly']:
            response += "\n\n✅ **All checks passed — this flight is safe to plan.**"
        else:
            response += "\n\n❌ **Warning: One or more safety checks failed. Review before proceeding.**"
        
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
                {"role": "assistant", "content": response}
            ]
        })
    
    return examples


def generate_safety_question_examples(count=10):
    """Generate safety-focused Q&A examples"""
    examples = []
    
    qa_pairs = [
        {
            "q": "Why do we need contingency fuel?",
            "a": "Contingency fuel (typically 5% of trip fuel per ICAO standards) accounts for unexpected factors like routing changes, holding patterns, or slightly higher-than-planned fuel burn. It's a safety buffer to ensure you never arrive with less fuel than planned."
        },
        {
            "q": "What is ETOPS and why does it matter?",
            "a": "ETOPS (Extended-range Twin-engine Operational Performance Standards) allows twin-engine aircraft to fly routes that are far from alternate airports. An ETOPS-180 rating means the aircraft can fly routes where it's up to 180 minutes flying time from the nearest suitable diversion airport. Non-ETOPS aircraft are restricted to staying closer to alternate airports."
        },
        {
            "q": "What's the difference between MTOW and MLW?",
            "a": "MTOW (Maximum Takeoff Weight) is the maximum weight at which an aircraft is certified to take off. MLW (Maximum Landing Weight) is the maximum weight for landing. MLW is lower because landing puts more stress on the airframe. The difference means you need to burn off fuel during flight to land safely."
        },
        {
            "q": "Why do we need alternate fuel?",
            "a": "Alternate fuel ensures that if you can't land at your destination (weather, runway closure, etc.), you have enough fuel to divert to an alternate airport. ICAO standards typically require 45 minutes of flight time to reach an alternate, plus reserves."
        },
        {
            "q": "What is final reserve fuel?",
            "a": "Final reserve fuel is the absolute minimum fuel you must have when landing — typically 30 minutes of holding fuel. This is your emergency buffer and should never be used in normal operations. If you're going to land with less than final reserve, you must declare a fuel emergency."
        },
        {
            "q": "Can I take off if I'm over MTOW?",
            "a": "Absolutely not. Taking off over MTOW is illegal and extremely dangerous. The aircraft's structural limits, performance guarantees, and certification are all based on MTOW. Exceeding it risks structural failure, runway overrun, and loss of control. You must either reduce fuel, reduce payload, or use a larger aircraft."
        },
        {
            "q": "What happens if I land over MLW?",
            "a": "Landing over MLW is dangerous and can cause structural damage to the landing gear and airframe. In emergencies where you must land overweight, expect a thorough aircraft inspection afterward. In normal operations, you must burn off or dump fuel to get below MLW before landing."
        },
        {
            "q": "How accurate is great circle distance vs actual flight distance?",
            "a": "Great circle distance is the shortest path between two points on Earth. Actual flight distance is typically 2-8% longer due to air traffic control routing, wind optimization, altitude restrictions, and airspace avoidance. Always add a buffer when using great circle estimates for fuel planning."
        },
    ]
    
    for qa in random.sample(qa_pairs, min(count, len(qa_pairs))):
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": qa["q"]},
                {"role": "assistant", "content": qa["a"]}
            ]
        })
    
    return examples


# ── MAIN GENERATION FUNCTION ──────────────────────────────────────────────────
def generate_training_dataset(
    aircraft_lookups=15,
    route_distances=20,
    fuel_plans=40,
    safety_qa=10,
    output_file="training_data.jsonl"
):
    """
    Generate a complete training dataset and save as JSONL.
    
    Recommended minimums for fine-tuning:
    - Small dataset: 50-100 examples
    - Medium dataset: 100-500 examples  
    - Large dataset: 500+ examples
    """
    
    print("\n" + "═" * 70)
    print("  GENERATING TRAINING DATA FOR FINE-TUNING")
    print("═" * 70 + "\n")
    
    all_examples = []
    
    print(f"📊 Generating {aircraft_lookups} aircraft lookup examples...")
    all_examples.extend(generate_aircraft_lookup_examples(aircraft_lookups))
    
    print(f"🗺️  Generating {route_distances} route distance examples...")
    all_examples.extend(generate_route_distance_examples(route_distances))
    
    print(f"⛽ Generating {fuel_plans} fuel planning examples...")
    all_examples.extend(generate_fuel_planning_examples(fuel_plans))
    
    print(f"❓ Generating {safety_qa} safety Q&A examples...")
    all_examples.extend(generate_safety_question_examples(safety_qa))
    
    # Shuffle for better training
    random.shuffle(all_examples)
    
    # Save as JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"\n✅ Generated {len(all_examples)} training examples")
    print(f"💾 Saved to: {output_file}")
    print("\n" + "═" * 70)
    print("  NEXT STEPS")
    print("═" * 70)
    print("1. Review the training data file to ensure quality")
    print("2. Upload it to OpenAI: client.files.create(file=open('training_data.jsonl'), purpose='fine-tune')")
    print("3. Start fine-tuning: client.fine_tuning.jobs.create(training_file=file_id, model='gpt-4o-mini-2024-07-18')")
    print("4. Monitor progress and use your custom model!")
    print("═" * 70 + "\n")
    
    return all_examples


# ── PREVIEW FUNCTION ──────────────────────────────────────────────────────────
def preview_examples(filename="training_data.jsonl", count=3):
    """Preview a few examples from the training data"""
    print("\n" + "═" * 70)
    print(f"  PREVIEW: First {count} examples")
    print("═" * 70 + "\n")
    
    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= count:
                break
            
            example = json.loads(line)
            messages = example['messages']
            
            print(f"EXAMPLE {i+1}:")
            print("─" * 70)
            for msg in messages:
                if msg['role'] == 'user':
                    print(f"👤 User: {msg['content'][:200]}...")
                elif msg['role'] == 'assistant':
                    print(f"🤖 Assistant: {msg['content'][:300]}...")
            print()


# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Generate training data
    # Adjust these numbers based on how much data you want:
    # - Minimum for fine-tuning: ~50 total examples
    # - Recommended: 100-200 examples
    # - Best results: 500+ examples
    
    generate_training_dataset(
        aircraft_lookups=15,
        route_distances=20,
        fuel_plans=50,      # Most important — give this the most examples
        safety_qa=10,
        output_file="training_data.jsonl"
    )
    
    # Preview the first few examples
    preview_examples("training_data.jsonl", count=3)
