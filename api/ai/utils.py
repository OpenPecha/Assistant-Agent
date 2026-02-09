import re

def clean_translation_text(text: str) -> str:
    """
    Clean and normalize translated text.
    
    Args:
        text: Raw translated text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common prefixes from model responses
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
