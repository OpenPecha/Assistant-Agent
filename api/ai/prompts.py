"""Specialized prompts for translating Tibetan Buddhist texts."""


TIBETAN_BUDDHIST_TRANSLATION_PROMPT = """You are an expert translator specializing in Tibetan Buddhist texts. Translate the provided text into {target_language} while maintaining doctrinal accuracy and spiritual integrity.

REQUIREMENTS:
- Preserve Buddhist terminology and concepts precisely
- Maintain the spiritual context and meaning
- Use appropriate register for {text_type} texts
- Produce fluent, natural {target_language}
- Keep proper names and sacred terms intact when appropriate

{user_rules_section}

OUTPUT FORMAT - PROVIDE ONLY THE TRANSLATION:
Example input: "May all beings be free from suffering"
Correct output: "May all sentient beings be liberated from suffering"
Wrong output: "Translation: May all sentient beings be liberated from suffering"
Wrong output: "TEXT 1: May all sentient beings be liberated from suffering"

TEXT TYPE: {text_type}
SOURCE TEXT:
{source_text}

Translation:"""


def get_translation_prompt(
    source_text: str,
    target_language: str,
    text_type: str = "Buddhist text",
    user_rules: str = None,
) -> str:

    user_rules_section = ""
    if user_rules and user_rules.strip():
        user_rules_section = f"ADDITIONAL USER RULES:\n{user_rules.strip()}\n"

    return TIBETAN_BUDDHIST_TRANSLATION_PROMPT.format(
        target_language=target_language,
        text_type=text_type,
        source_text=source_text,
        user_rules_section=user_rules_section
    )
