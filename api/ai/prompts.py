TRANSLATION_PROMPT = """
target language: {target_language}
main rules: {user_rules_section}
text type: {text_type}
source text: {source_text}
Response:"""

CHATBOT_QA_PROMPT = """
text type: {text_type}
source text: {source_text}
main rules: {user_rules_section}
Response:"""

def get_specialized_prompt(
    source_text: str,
    target_language: str = None,
    text_type: str = "Buddhist text",
    user_rules: str = None,
) -> str:

    if target_language is None:
        return CHATBOT_QA_PROMPT.format(
            text_type=text_type,
            source_text=source_text,
            user_rules_section=user_rules
        )

    return TRANSLATION_PROMPT.format(
        target_language=target_language,
        text_type=text_type,
        source_text=source_text,
        user_rules_section=user_rules
    )
