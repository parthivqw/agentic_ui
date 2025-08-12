from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Ensure .env variables are loaded

def call_llama_generate_fields(data):
    print(f"🔍 DEBUG: Function started with data type: {type(data)}")
    print(f"🔍 DEBUG: Data attributes: {dir(data) if hasattr(data, '__dict__') else 'Not an object'}")
    
    try:
        print(f"📡 Calling LLaMA (Groq) with prompt:\n{data.main_prompt}")
        print(f"🔍 DEBUG: Theme: {getattr(data, 'theme', 'No theme attr')}")
    except AttributeError as e:
        print(f"❌ ERROR accessing data attributes: {e}")
        return '{"error": "Cannot access data attributes"}'

    print("🔍 DEBUG: Creating OpenAI client...")
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    print("✅ OpenAI client created successfully")

    # 🛠️ Coerce all checkbox fields to boolean
    def to_bool(val):
        return str(val).lower() == "true" or val is True

    print("🔍 DEBUG: Building selected fields...")
    # ✅ Build selected fields list (CTA freedom enabled)
    selected_fields = []
    try:
        if to_bool(data.include_hero_headline):
            selected_fields.append("hero_headline")
        if to_bool(data.include_hero_subline):
            selected_fields.append("hero_subline")
        if to_bool(data.include_description):
            selected_fields.append("description")
        if to_bool(data.include_cta):
            selected_fields.append("cta")
        if to_bool(data.include_cta_link):
            selected_fields.append("cta_link")
        if to_bool(data.include_testimonial):
            selected_fields.append("testimonial")
        if to_bool(data.include_success_metrics):
            selected_fields.append("success_metrics")
        if to_bool(data.include_target_audience):
            selected_fields.append("target_audience")
        
        print(f"✅ Selected fields: {selected_fields}")
    except AttributeError as e:
        print(f"❌ ERROR building selected fields: {e}")
        return '{"error": "Cannot access boolean fields"}'

    # 🎨 Theme Expansion Instruction (ALWAYS Generate Suggested Theme unless Claude already did)
    theme_msg = (
        "The theme is already provided by Claude as part of the payload. Simply include it as 'suggested_theme'."
        if data.theme
        else (
            "The user did not provide a theme. "
            "Based on the enhanced main prompt's intent, generate a vivid scene composition and return it in 'suggested_theme'. "
            "Include background details like mood, lighting, color palette, and visual motifs."
        )
    )

    # 🧠 Compose System Prompt with all Fields in FORMAT EXAMPLE
    system_prompt = f"""
You are a professional poster content generation AI specializing in educational and marketing visuals.

TASK FLOW:
1. Take the user's raw main prompt and expand it into a **vivid, visually-rich, and action-oriented 'custom_prompt'**.
    - The custom_prompt should describe the poster's intent with immersive scene details.
    - Include actions, participants, environment, mood-setting phrases, and visual motifs.
    - Avoid generic terms like "Create a poster for X". Be vivid, descriptive, and scene-aware.
2. Based on the juiced-up custom_prompt, generate content for ONLY the following fields: {', '.join(selected_fields)}.
3. {theme_msg}
4. Output a JSON object with EXACTLY these keys:
    - "custom_prompt"
    - {', '.join([f'"{field}"' for field in selected_fields])}
    - "suggested_theme"

RULES:
- The custom_prompt must be vivid, action-driven, and feel like a visual storyboard.
- For any unselected fields, do NOT include them.
- All field content must strictly follow token limits.
- Do not add headers, explanations, or markdown.
- Strictly Return the JSON File Only

FIELD CONSTRAINTS:
- "hero_headline": max 12 tokens
- "hero_subline": max 15 tokens
- "description": max 25 tokens
- "testimonial": max 25 tokens (short single-quote quote)
- "success_metrics": max 20 tokens (pipe-separated stats)
- "target_audience": max 15 tokens
- "cta" and "cta_link": very short and clean
- 'cta' and 'cta_link' are independent fields.

FORMAT EXAMPLE:
{{
  "custom_prompt": "Design a vibrant poster capturing a dynamic Python Bootcamp scene, where students collaborate on laptops, sharing ideas in a high-energy tech workspace filled with neon code overlays and team brainstorming sessions.",
  "hero_headline": "Code. Collaborate. Succeed!",
  "hero_subline": "Unlock Your Potential in 6 Weeks",
  "description": "Master Python through hands-on projects guided by industry mentors in an intensive 6-week program.",
  "success_metrics": "95% Job Placement | 4.5/5 Rating | 1000+ Alumni",
  "testimonial": "'This bootcamp transformed my career!'",
  "target_audience": "Aspiring developers and data scientists",
  "cta": "Apply Now",
  "cta_link": "https://pythonbootcamp.io",
  "suggested_theme": "A bustling startup workspace with glass walls, digital screens, and energetic collaboration zones bathed in warm lighting and bold color accents."
}}
"""

    print("🔍 DEBUG: About to make API call...")
    print(f"🔍 DEBUG: Model: moonshotai/kimi-k2-instruct")
    print(f"🔍 DEBUG: System prompt length: {len(system_prompt)} chars")

    # 🧠 Call LLaMA Model
    try:
        response = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.main_prompt}
            ],
            temperature=0.7
        )
        print("✅ Received response from Groq LLaMA")
        
        response_content = response.choices[0].message.content
        print(f"📬 Raw response (first 200 chars): {response_content[:200]}...")
        print(f"🔍 DEBUG: Response type: {type(response_content)}")
        
        return response_content
        
    except Exception as e:
        print(f"❌ API CALL ERROR: {e}")
        print(f"🔍 DEBUG: Error type: {type(e)}")
        return f'{{"error": "API call failed: {str(e)}"}}'