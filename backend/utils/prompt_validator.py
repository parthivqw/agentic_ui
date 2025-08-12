def is_prompt_vague(prompt:str)->bool:
    vague_keywords=[
        "make a poster",
        "create a  poster",
        "desgin something",
        " i want a banner",
        "help me with a poster",
        
        "generate me a psoter"

    ]
    prompt_lower=prompt.lower()
    vague_hits=[kw for kw in vague_keywords if kw in prompt_lower]

    return len(vague_hits) > 0