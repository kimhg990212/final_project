def build_logo_prompt(keyword:dict):
    return f"""
    Create a professional logo design based on this description:
    {keyword.get("raw_text")}
    
    Style: clean, simple, vector logo, brand identity, high quality
    """