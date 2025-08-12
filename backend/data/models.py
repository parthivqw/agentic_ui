from pydantic import BaseModel
from typing import Optional


class PromptRequest(BaseModel):
    prompt: str


class PosterRequest(BaseModel):
    # Step 1: Raw prompt describing what the poster is about
    main_prompt: str

    # Step 2: Optional theme override
    theme: Optional[str] = None  # If None, AI generates theme

    # Step 3: Field toggles (checkboxes)
    include_hero_headline: bool = False
    include_hero_subline: bool = False
    include_description: bool = False
    include_cta: bool = False
    include_cta_link: bool = False
    include_testimonial: bool = False
    include_success_metrics: bool = False
    include_target_audience: bool = False

    # Step 4: Optional enhanced prompt override (very rare)
    custom_prompt: Optional[str] = None
    
class SalesRequest(BaseModel):
    conversation: str
    predicted_intent: str
