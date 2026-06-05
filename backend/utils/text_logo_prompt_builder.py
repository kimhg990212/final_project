

def build_logo_prompt(keywords: dict):
    business_type = keywords.get("business_type", "general")
    colors = keywords.get("color", ["auto"])
    moods = keywords.get("mood", ["auto"])
    style = keywords.get("style", "auto")
    complexity = keywords.get("complexity", "balanced")
    logo_type = keywords.get("logo_type", "auto")
    raw_text = keywords.get("raw_text", "")

    color_text = ", ".join(colors) if colors != ["auto"] else "appropriate color palette"
    mood_text = ", ".join(moods) if moods != ["auto"] else "professional mood"

    if style == "auto":
        style_text = "modern brand identity"
    else:
        style_text = f"{style} style"

    complexity_text = {
        "simple": "simple and clean design, minimal details",
        "balanced": "balanced design with moderate detail",
        "ornate": "ornate and decorative design, premium details"
    }.get(complexity, "balanced design")

    logo_type_text = {
        "emblem": "emblem logo, badge style, circular composition",
        "text": "typography logo, wordmark style",
        "symbol_text": "symbol and text logo, icon with brand text",
        "auto": "professional logo design"
    }.get(logo_type, "professional logo design")

    prompt = f"""
Professional logo design for a {business_type} business.
{logo_type_text}.
{style_text}.
Color palette: {color_text}.
Mood: {mood_text}.
{complexity_text}.
Clean vector logo, brand identity, high quality, centered composition, white background.
Based on user request: {raw_text}
""".strip()

    return prompt