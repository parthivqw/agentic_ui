from agents import poster_agent, sales_agent
from agents.claude_agent import (
    process_user_prompt,
    generate_input_payload_for_app,
    generate_sales_payload_for_app
)
from data.models import PosterRequest
from data.models import SalesRequest

def detect_intent(prompt: str):
    print("🔍 detect_intent called")
    
    # Step 1: Extract intent and recommended app
    intent_data = process_user_prompt(prompt)
    print(f"🎯 Intent data: {intent_data}")

    if intent_data["status"] != "ok":
        print(f"❌ Intent extraction failed: {intent_data}")
        return intent_data

    app_name = intent_data["recommended_app"]
    print(f"🎯 Recommended app: {app_name}")

    # Step 2 + 3: Route based on detected app
    if app_name == "Poster Generator":
        print("🎨 Routing to Poster Generator...")
        
        payload_data = generate_input_payload_for_app(intent_data)
        print(f"📦 Payload data: {payload_data}")

        if payload_data["status"] != "ok":
            print(f"❌ Payload generation failed: {payload_data}")
            return payload_data

        poster_payload = PosterRequest(**payload_data['input_payload'])
        print(f"✅ Created PosterRequest: {poster_payload}")
        
        # THIS IS THE CRITICAL PART - Make sure we return the result
        print("🚀 Calling poster_agent.run...")
        result = poster_agent.run(poster_payload)
        
        print(f"🔥 POSTER AGENT RETURNED: {result}")
        print(f"🔥 RESULT TYPE: {type(result)}")
        
        # Safety check
        if result is None:
            print("❌ CRITICAL: poster_agent.run returned None!")
            return {
                "status": "error",
                "message": "Poster agent returned None"
            }
        
        if not isinstance(result, dict):
            print(f"❌ CRITICAL: poster_agent.run returned {type(result)}, not dict!")
            return {
                "status": "error",
                "message": f"Poster agent returned invalid type: {type(result)}"
            }
        
        print("✅ Returning poster result...")
        return result

    elif app_name == "Lead/Sales Intent Generator":
        print("💼 Routing to Sales Generator...")
        
        payload_data = generate_sales_payload_for_app(intent_data)
        print(f"📦 Sales payload: {payload_data}")

        if payload_data["status"] != "ok":
            print(f"❌ Sales payload failed: {payload_data}")
            return payload_data
            
        sales_payload = SalesRequest(**payload_data['input_payload'])
        print(f"✅ Created SalesRequest: {sales_payload}")
        
        print("🚀 Calling sales_agent.run...")
        result = sales_agent.run(sales_payload.dict())
        
        print(f"🔥 SALES AGENT RETURNED: {result}")
        print(f"🔥 RESULT TYPE: {type(result)}")
        
        # Safety check
        if result is None:
            print("❌ CRITICAL: sales_agent.run returned None!")
            return {
                "status": "error",
                "message": "Sales agent returned None"
            }
        
        return result

    # Handle undefined apps
    print(f"❌ No handler for app: {app_name}")
    return {
        "status": "error",
        "message": f"No agent handler defined for '{app_name}'."
    }