from utils.prompt_validator import is_prompt_vague
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from utils.bert_intent import predict_sales_intent

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.a4f.co/v1"
)

# Regex cleaner
def clean_json_response(text: str) -> str:
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return cleaned.strip()

# STEP 1: Extract Intent & App
def process_user_prompt(prompt: str):
    if is_prompt_vague(prompt):
        return {
            "status": "vague",
            "message": "🤖 GPT: Could you please describe the poster's theme or purpose in more detail?"
        }

    try:
        intent_extraction_prompt = f"""
You are a helpful AI assistant. The user has provided this prompt:

\"{prompt}\"

Your job is to:
1. Extract the user's **true intent** in one sentence.
2. Based on the intent, **recommend the most suitable app** from the list below.
3. Also return the **raw prompt** from the user as a separate field.

Available apps:
- Poster Generator — for visual banner/poster/image creation.
- Lead/Sales Intent Generator — for marketing copy and lead capture flows.
- Content Cluster Analyzer — for breaking topics into content clusters.

Return ONLY valid JSON:
{{
  "intent": "...",
  "recommended_app": "...",
  "prompt": "..."
}}
"""

        response = client.chat.completions.create(
            model="provider-6/kimi-k2-instruct",
            messages=[{"role": "user", "content": intent_extraction_prompt}],
            temperature=0.3
        )

        raw_response = response.choices[0].message.content
        cleaned = clean_json_response(raw_response)
        claude_json = json.loads(cleaned)

        # Load registry
        registry_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app_registry.json'))
        with open(registry_path, 'r') as f:
            registry = json.load(f)

        app_name = claude_json["recommended_app"]
        if app_name not in registry:
            return {"status": "error", "message": f"App '{app_name}' not found in registry."}

        return {
            "status": "ok",
            "intent": claude_json["intent"],
            "recommended_app": app_name,
            "raw_prompt": claude_json["prompt"],
            "entrypoint": registry[app_name]["entrypoint"],
            "required_fields": registry[app_name]["required_fields"]
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "AI response was not valid JSON. Could not parse intent."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# STEP 2: Prepare Input Payload for App
def generate_input_payload_for_app(intent_data: dict):
    try:
        raw_prompt = intent_data["raw_prompt"]
        fields = intent_data["required_fields"]
        field_template = json.dumps({field: False for field in fields}, indent=2)

        prompt_to_ai = f"""
You are an expert prompt enhancer and visual layout assistant.

A user wants to generate a poster using the following raw prompt:
\"{raw_prompt}\"

Your tasks:
1. Rewrite the prompt into a **vivid, visually-rich version** for 'main_prompt' within 12 words .
2. Decide whether to override the theme. If yes, write a creative theme within 30 words. If not, leave it as an empty string.
3. Choose only the **essential fields** from the list below to avoid poster gibberish during image generation.
4. Leave 'custom_prompt' as an empty string.

Available fields (return them as true/false):
{field_template}

Respond ONLY with valid JSON:
{{
  "main_prompt": "...",
  "theme": "...",
  "custom_prompt": "",
  "include_hero_headline": true,
  "include_hero_subline": false,
  "include_description": true,
  "include_cta": false,
  "include_cta_link": true,
  "include_testimonial": true,
  "include_success_metrics": false,
  "include_target_audience": false
}}
"""

        response = client.chat.completions.create(
            model="provider-6/kimi-k2-instruct",
            messages=[{"role": "user", "content": prompt_to_ai}],
            temperature=0.5
        )

        raw_output = response.choices[0].message.content
        cleaned = clean_json_response(raw_output)
        app_payload = json.loads(cleaned)

        return {
            "status": "ok",
            "input_payload": app_payload
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
def generate_sales_payload_for_app(intent_data: dict):
    try:
        raw_text = intent_data["raw_prompt"]

        # 🔁 Prompt to GPT-4o — STRICT JSON ONLY
        input_cleaning_prompt = f"""
You are a helpful AI assistant.

The user has pasted a messy multi-day sales conversation copied from emails or chat.

👉 Your job:
1. Extract only the sales conversation (ignore any unrelated fluff or greetings).
2. Flatten it into this exact format:
    Day 1: ...
    Day 2: ...
    Day 3: ...

⚠️ IMPORTANT: Return your response ONLY as strict JSON, like:
{{
  "conversation": "Day 1: ...\\nDay 2: ...\\nDay 3: ..."
}}

No commentary. No markdown. No explanations.
Text:
\"\"\"{raw_text}\"\"\"
"""

        response = client.chat.completions.create(
            model="provider-6/kimi-k2-instruct",
            messages=[{"role": "user", "content": input_cleaning_prompt}],
            temperature=0.2
        )

        cleaned_response = clean_json_response(response.choices[0].message.content)
        convo_json = json.loads(cleaned_response)
        flattened_convo = convo_json["conversation"]

        # 🧠 Predict sales intent using fine-tuned BERT
        predicted_intent = predict_sales_intent(flattened_convo)

        return {
            "status": "ok",
            "input_payload": {
                "conversation": flattened_convo,
                "predicted_intent": predicted_intent
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }