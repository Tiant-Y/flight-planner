# ai_flight_planner.py
# Phase 1 - Part C: AI-Powered Flight Planning Assistant
# Connects GPT-4o with our aircraft database and fuel calculator

import openai
import json
from aircraft_database import lookup_aircraft, list_all_aircraft
from fuel_calculator import calculate_fuel, print_fuel_report
from airport_database import lookup_airport, calculate_route
from weather_integration import get_metar, get_route_weather_summary, format_metar_display
from route_optimization import generate_route_waypoints, optimize_route_for_winds, display_route
from airspace_restrictions import check_route_airspace_violations, get_airspace_summary, format_airspace_report
from etops_compliance import check_etops_compliance, find_etops_diversions_along_route, format_etops_report


# ── CONFIGURATION ──────────────────────────────────────────────────────────────
# Make sure your OPENAI_API_KEY environment variable is set, or pass it directly:
# client = openai.OpenAI(api_key="your-key-here")
client = openai.OpenAI()


# ── SYSTEM PROMPT FOR THE AI ──────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert AI flight planning assistant for professional pilots.

Your capabilities:
- You have access to a database of 18 aircraft types (Boeing, Airbus, Embraer)
- You have access to 60+ major airports worldwide with coordinates
- You can automatically calculate distances between airports
- You can generate optimized flight routes with waypoints
- You can check routes for airspace violations (no-fly zones, restricted areas)
- You can verify ETOPS compliance for twin-engine aircraft
- You can optimize routes for wind conditions
- You can fetch real-time weather (METAR) for any airport
- You can get route weather summaries
- You can calculate fuel requirements following ICAO standards
- You understand aviation terminology (ICAO codes, IATA codes, ETOPS, MTOW, MLW, etc.)
- You provide clear, safety-focused recommendations

Your tools:
1. lookup_aircraft(aircraft_code) - Get aircraft performance data
2. lookup_airport(code) - Get airport info by ICAO or IATA code
3. calculate_route(origin, destination) - Calculate distance between two airports
4. generate_flight_route(origin, destination, waypoints) - Generate optimized route with waypoints
5. check_airspace(waypoints, altitude_ft) - Check route for airspace violations
6. check_etops(aircraft_code, waypoints) - Verify ETOPS compliance for twin-engine aircraft
7. get_weather(airport_code) - Get current weather (METAR) for an airport
8. get_route_weather(origin, destination) - Get complete weather briefing for a route
9. calculate_fuel(aircraft_code, distance_nm, headwind_kt, include_alternate) - Calculate fuel for a flight

When a pilot asks you to plan a flight:
1. Extract: aircraft type, origin, destination, and any mentioned weather/wind
2. Use lookup_airport() to verify airports exist and get their info
3. Use generate_flight_route() to create a detailed route with waypoints
4. Use check_airspace() to verify the route doesn't violate restricted airspace
5. Use get_weather() or get_route_weather() to check current conditions
6. Extract headwind from weather data if available
7. Use lookup_aircraft() to verify the aircraft exists
8. Use calculate_fuel() with the calculated distance and weather data
9. Present results clearly with safety recommendations including airspace, weather, and routing considerations

CRITICAL: If check_airspace() shows any CRITICAL violations, warn the pilot immediately and suggest route replanning.

Always prioritize safety. If weather conditions are hazardous or airspace is violated, warn the pilot clearly.
Use aviation terminology naturally but explain technical points when needed.
"""


# ── TOOL DEFINITIONS FOR FUNCTION CALLING ─────────────────────────────────────
tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_aircraft",
            "description": "Look up aircraft performance data by type code or common name. Returns MTOW, MLW, fuel capacity, range, ETOPS rating, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "aircraft_code": {
                        "type": "string",
                        "description": "Aircraft type code or common name, e.g. 'B777-300ER', '777', 'A380', 'dreamliner'"
                    }
                },
                "required": ["aircraft_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_airport",
            "description": "Look up airport information by ICAO (4-letter) or IATA (3-letter) code. Returns name, city, country, and coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Airport code, e.g. 'KLAX', 'LAX', 'EGLL', 'LHR'"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_route",
            "description": "Calculate the great circle distance between two airports automatically. Use this whenever a pilot mentions origin and destination to get the exact distance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin airport code (ICAO or IATA), e.g. 'KLAX', 'LAX'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport code (ICAO or IATA), e.g. 'EGLL', 'LHR'"
                    }
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_flight_route",
            "description": "Generate optimized flight route with waypoints along great circle path. Returns detailed route with coordinates, bearings, and distances for each waypoint.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin airport code (ICAO or IATA), e.g. 'KLAX'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport code (ICAO or IATA), e.g. 'EGLL'"
                    },
                    "waypoints": {
                        "type": "integer",
                        "description": "Number of intermediate waypoints (default 5)",
                        "default": 5
                    }
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_airspace",
            "description": "Check if a route violates any restricted airspace, prohibited areas, or no-fly zones. CRITICAL: Always use this when generating routes to ensure flight safety and legal compliance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "waypoints": {
                        "type": "array",
                        "description": "List of waypoints with 'lat', 'lon', 'number', and 'name' fields",
                        "items": {
                            "type": "object",
                            "properties": {
                                "lat": {"type": "number"},
                                "lon": {"type": "number"},
                                "number": {"type": "integer"},
                                "name": {"type": "string"}
                            }
                        }
                    },
                    "altitude_ft": {
                        "type": "integer",
                        "description": "Cruise altitude in feet (default 35000)",
                        "default": 35000
                    }
                },
                "required": ["waypoints"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_etops",
            "description": "Verify ETOPS compliance for twin-engine aircraft on overwater routes. Checks that aircraft is within required time of suitable diversion airports at all waypoints.",
            "parameters": {
                "type": "object",
                "properties": {
                    "aircraft_code": {
                        "type": "string",
                        "description": "Aircraft type code, e.g. 'B777-300ER', 'A350-900'"
                    },
                    "waypoints": {
                        "type": "array",
                        "description": "List of waypoints with 'lat', 'lon', 'number', and 'name' fields",
                        "items": {
                            "type": "object",
                            "properties": {
                                "lat": {"type": "number"},
                                "lon": {"type": "number"},
                                "number": {"type": "integer"},
                                "name": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["aircraft_code", "waypoints"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather (METAR) for an airport. Returns temperature, wind, visibility, flight category, and conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": "Airport ICAO code, e.g. 'KLAX', 'EGLL'"
                    }
                },
                "required": ["airport_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_route_weather",
            "description": "Get comprehensive weather briefing for a route including origin weather, destination weather, and route hazards (SIGMETs).",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin airport ICAO code, e.g. 'KLAX'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport ICAO code, e.g. 'EGLL'"
                    }
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_fuel",
            "description": "Calculate complete fuel requirements for a flight following ICAO standards. Returns trip fuel, contingency, alternate, reserve, and safety checks (MTOW/MLW compliance, range verification).",
            "parameters": {
                "type": "object",
                "properties": {
                    "aircraft_code": {
                        "type": "string",
                        "description": "Aircraft type code, e.g. 'B777-300ER', 'A380'"
                    },
                    "distance_nm": {
                        "type": "number",
                        "description": "Flight distance in nautical miles"
                    },
                    "headwind_kt": {
                        "type": "number",
                        "description": "Headwind in knots (use negative for tailwind). Default 0.",
                        "default": 0
                    },
                    "include_alternate": {
                        "type": "boolean",
                        "description": "Whether to include alternate airport fuel (45 min). Default true.",
                        "default": True
                    }
                },
                "required": ["aircraft_code", "distance_nm"]
            }
        }
    }
]


# ── FUNCTION EXECUTION HANDLER ────────────────────────────────────────────────
def execute_function(function_name: str, arguments: dict):
    """Execute the requested function with given arguments."""
    
    if function_name == "lookup_aircraft":
        result = lookup_aircraft(arguments["aircraft_code"])
        return result if result else {"error": "Aircraft not found"}
    
    elif function_name == "lookup_airport":
        result = lookup_airport(arguments["code"])
        return result if result else {"error": "Airport not found"}
    
    elif function_name == "calculate_route":
        result = calculate_route(arguments["origin"], arguments["destination"])
        return result
    
    elif function_name == "generate_flight_route":
        result = generate_route_waypoints(
            arguments["origin"], 
            arguments["destination"],
            arguments.get("waypoints", 5)
        )
        return result
    
    elif function_name == "check_airspace":
        result = check_route_airspace_violations(
            arguments["waypoints"],
            arguments.get("altitude_ft", 35000),
            buffer_nm=50
        )
        return result
    
    elif function_name == "check_etops":
        result = check_etops_compliance(
            arguments["aircraft_code"],
            arguments["waypoints"]
        )
        return result
    
    elif function_name == "get_weather":
        result = get_metar(arguments["airport_code"])
        return result
    
    elif function_name == "get_route_weather":
        result = get_route_weather_summary(arguments["origin"], arguments["destination"])
        return result
    
    elif function_name == "calculate_fuel":
        result = calculate_fuel(
            aircraft_code=arguments["aircraft_code"],
            distance_nm=arguments["distance_nm"],
            headwind_kt=arguments.get("headwind_kt", 0),
            include_alternate=arguments.get("include_alternate", True)
        )
        return result
    
    else:
        return {"error": f"Unknown function: {function_name}"}


# ── MAIN AI CHAT FUNCTION ─────────────────────────────────────────────────────
def chat_with_ai(user_message: str, conversation_history: list = None) -> dict:
    """
    Send a message to the AI flight planner and get a response.
    
    Args:
        user_message: The pilot's query
        conversation_history: Optional list of previous messages for context
    
    Returns:
        dict with 'assistant_message', 'function_calls', and 'conversation_history'
    """
    
    # Initialize conversation if needed
    if conversation_history is None:
        conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add user message
    conversation_history.append({"role": "user", "content": user_message})
    
    # Call OpenAI API with function calling
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Fast and cheap for development
        messages=conversation_history,
        tools=tools,
        tool_choice="auto"  # Let AI decide when to use tools
    )
    
    assistant_message = response.choices[0].message
    
    # Handle function calls if AI wants to use them
    tool_calls = assistant_message.tool_calls
    function_results = []
    
    if tool_calls:
        # Add assistant's message with tool calls to history
        conversation_history.append(assistant_message)
        
        # Execute each function call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"🔧 AI is calling: {function_name}({arguments})")
            
            # Execute the function
            result = execute_function(function_name, arguments)
            function_results.append({
                "function": function_name,
                "arguments": arguments,
                "result": result
            })
            
            # Add function result to conversation
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
        
        # Get final response from AI after it sees the function results
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
        )
        
        final_message = final_response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": final_message})
        
        return {
            "assistant_message": final_message,
            "function_calls": function_results,
            "conversation_history": conversation_history
        }
    
    else:
        # No function calls, just return the response
        conversation_history.append({"role": "assistant", "content": assistant_message.content})
        return {
            "assistant_message": assistant_message.content,
            "function_calls": None,
            "conversation_history": conversation_history
        }


# ── INTERACTIVE CHAT LOOP ─────────────────────────────────────────────────────
def interactive_chat():
    """Run an interactive chat session with the AI flight planner."""
    
    print("\n" + "═" * 70)
    print("  ✈️  AI FLIGHT PLANNER — Phase 1 Complete System")
    print("═" * 70)
    print("  I can help you plan flights, calculate fuel, and check aircraft data.")
    print("  Type 'quit' or 'exit' to end the session.")
    print("  Type 'clear' to start a fresh conversation.")
    print("═" * 70 + "\n")
    
    conversation_history = None
    
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! Safe flights! ✈️\n")
            break
        
        if not user_input:
            continue
        
        # Handle special commands
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("\nGoodbye! Safe flights! ✈️\n")
            break
        
        if user_input.lower() == "clear":
            conversation_history = None
            print("\n[Conversation cleared — starting fresh]\n")
            continue
        
        # Get AI response
        print("\n🤖 AI Flight Planner: ", end="", flush=True)
        
        try:
            result = chat_with_ai(user_input, conversation_history)
            print(result["assistant_message"])
            
            # Update conversation history for context
            conversation_history = result["conversation_history"]
            
            # If fuel was calculated, offer to show detailed report
            if result["function_calls"]:
                for call in result["function_calls"]:
                    if call["function"] == "calculate_fuel" and "error" not in call["result"]:
                        show_report = input("\n📊 Show detailed fuel report? (y/n): ").strip().lower()
                        if show_report == "y":
                            print_fuel_report(call["result"])
            
            print()  # Extra newline for readability
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Please check your API key is set correctly.\n")


# ── QUICK TEST EXAMPLES ───────────────────────────────────────────────────────
def run_test_examples():
    """Run a few test queries to demonstrate the system."""
    
    print("\n" + "═" * 70)
    print("  🧪 RUNNING TEST EXAMPLES")
    print("═" * 70 + "\n")
    
    test_queries = [
        "What's the MTOW of a Boeing 777-300ER?",
        "Plan a flight from Los Angeles to London with a 777. Assume 5,400 nautical miles and 25 knot headwind.",
        "Can an A320 fly from Singapore to Tokyo? That's about 2,900 nautical miles.",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"TEST {i}: {query}")
        print("─" * 70)
        result = chat_with_ai(query)
        print(f"🤖 {result['assistant_message']}\n")
        
        # Show fuel report if calculated
        if result["function_calls"]:
            for call in result["function_calls"]:
                if call["function"] == "calculate_fuel" and "error" not in call["result"]:
                    print_fuel_report(call["result"])
        
        print()


# ── MAIN ENTRY POINT ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    
    # Check if running in test mode or interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test_examples()
    else:
        interactive_chat()
