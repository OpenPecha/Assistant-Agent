import re

def clean_translation_text(text: str) -> str:
    """
    Clean and normalize translated text.
    
    Args:
        text: Raw translated text
        
    Returns:
        Cleaned text
    """
    text = re.sub(r'\s+', ' ', text.strip())
    
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith('\u201c') and text.endswith('\u201d')):
        text = text[1:-1].strip()
    
    prefixes_to_remove = [
        "Translation:",
        "Translation 1:",
        "Translation 2:",
        "Translation 3:",
        "Translation 4:",
        "Translation 5:",
        "Here is the translation:",
        "The translation is:",
        "As an expert translator",
        "I'll translate",
        "Here is",
        "TRANSLATION 1:",
        "TRANSLATION 2:",
        "TRANSLATION 3:",
    ]
    
    for prefix in prefixes_to_remove:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break
    
    # Remove trailing explanatory text (anything after lines starting with common markers)
    explanatory_markers = [
        "\n\nTranslation note",
        "\n\nNote:",
        "\n\nTranslator's",
        "\n\n*Translation",
        "\n\nDeeper meaning",
        "\n\n[Anmerkung",
        "\n\nWould you like",
    ]
    
    for marker in explanatory_markers:
        if marker in text:
            text = text.split(marker)[0].strip()
    
    return text
