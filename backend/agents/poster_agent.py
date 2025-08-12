import json
from utils.llama_generate_fields import call_llama_generate_fields
from utils.prompt_builder import build_image_generation_prompt
from utils.image_generator import generate_poster_image
from data.models import PosterRequest  # strict Pydantic input schema


def run(data: PosterRequest):
    print("🎯 Poster Agent received input:", data)

    try:
        print("🚀 Calling LLaMA via call_llama_generate_fields...")  # before
        # 🔍 Step 1: Generate poster content fields using LLaMA
        raw_response = call_llama_generate_fields(data)
        # print("📬 Got response from LLaMA:", raw_response[:80])

        try:
            # 🎯 Convert LLaMA response to dictionary (strict JSON expected)
            fields = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"🧠 LLaMA returned malformed JSON: {str(e)}",
                "raw_response": raw_response  # helpful for debugging bad LLM outputs
            }
        


        # 🧱 Step 2: Build enhanced image generation prompt
        final_prompt = build_image_generation_prompt(fields)
        print(final_prompt)

        # 🖼️ Step 3: Generate base64 poster image
        image = generate_poster_image(final_prompt)

        return {
            "status": "success",
            "poster_fields": fields,
            "image_base64": image,
            "message": "✅ Poster generated via MCP AI agent."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Poster generation failed: {str(e)}"
        }
    
