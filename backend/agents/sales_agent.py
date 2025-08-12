import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),  # or your actual Groq key
    base_url="https://api.groq.com/openai/v1"  # Example: adjust if needed
)

def run(payload: dict):
    print("🧠 Sales agent triggered successfully")
    try:
        conversation = payload["conversation"]
        predicted_intent = payload["predicted_intent"]

        # 💡 Compose Groq prompt
        final_prompt = f"""
You are a sales assistant.

Here is a multi-day sales conversation:

{conversation}

The predicted buyer intent is: **{predicted_intent}**

🎯 Based on the above, suggest the next best step for the sales team to take. Be direct and concise.
Your response should be 1–2 sentences only.
""" 
        model = "llama-3.3-70b-versatile"
        print("📡 Calling Groq with model:", model, " prompt excerpt:", final_prompt[:80])
        # 🧠 Groq LLM Call (LLaMA 3, Mixtral, etc)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Replace with actual Groq-supported model
            messages=[{"role": "user", "content": final_prompt}],
            temperature=0.3
        )
        print("✅ Groq response received:", response)

        next_action = response.choices[0].message.content.strip()

        return {
            "status": "ok",
            "next_best_action": next_action,
            "intent": predicted_intent
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
