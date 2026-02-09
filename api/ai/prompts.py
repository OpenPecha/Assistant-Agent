PROMPT_TEMPLATE = """
{target_language_line}
text type: {text_type}
main rules: {user_rules_section}
additional_context: {context}
{source_text_block}
"""

def get_specialized_prompt(
    source_text: str | None = None,
    target_language: str | None = None,
    text_type: str = "Buddhist text",
    user_rules: str | None = None,
    contexts: str | None = None,
) -> str:
    target_language_line = f"target language: {target_language}" if target_language else ""
    source_text_clean = (source_text or "").strip()
    source_text_block = f"source text: {source_text_clean}" if source_text_clean else ""

    return PROMPT_TEMPLATE.format(
        target_language_line=target_language_line,
        text_type=(text_type or "").strip(),
        user_rules_section=(user_rules or "").strip(),
        context=(contexts or "").strip(),
        source_text_block=source_text_block,
    )
