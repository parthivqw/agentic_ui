from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from service.router_logic import detect_intent
from data.models import PromptRequest

app = FastAPI(
    title="Agentic MCP UI Backend",
    description="AI Agent backend to route user intent to various services",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate")
async def generate(payload: PromptRequest):
    print("🔁 Incoming request to /generate...")

    prompt = payload.prompt
    print(f"📥 User prompt: {prompt}")

    if not prompt:
        return {"status": "error", "message": "No prompt provided in request."}

    # Step 1: Detect Intent
    print("🔍 Step 1: Detecting intent and recommended app...")
    intent_data = detect_intent(prompt)

    print(f"🔥 FINAL RESULT BEING RETURNED: {intent_data}")
    print(f"🔥 RESULT TYPE: {type(intent_data)}")

    if intent_data is None:
        print("❌ CRITICAL: intent_data is None!")
        return {
            "status": "error",
            "message": "Router returned None - check your agent logic"
        }

    if not isinstance(intent_data, dict):
        print(f"❌ CRITICAL: intent_data is not dict, it's {type(intent_data)}")
        return {
            "status": "error",
            "message": f"Invalid response type: {type(intent_data)}"
        }

    return intent_data
