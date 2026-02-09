TRANSLATION_PROMPT = """
target language: {target_language}
main rules: {user_rules_section}
text type: {text_type}
additional_context: {context}
source text: {source_text}
Response:"""

CHATBOT_QA_PROMPT = """
text type: {text_type}
main rules: {user_rules_section}
additional_context: {context}
source text: {source_text}
Response:"""

def get_specialized_prompt(
    source_text: str,
    target_language: str = None,
    text_type: str = "Buddhist text",
    user_rules: str = None,
    contexts: str = None,
) -> str:

    if target_language is None:
        return CHATBOT_QA_PROMPT.format(
            text_type=text_type,
            source_text=source_text,
            user_rules_section=user_rules,
            context=contexts or ""
        )

    return TRANSLATION_PROMPT.format(
        target_language=target_language,
        text_type=text_type,
        source_text=source_text,
        user_rules_section=user_rules,
        context=contexts or ""
    )
