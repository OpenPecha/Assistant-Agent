PROMPT_TEMPLATE = """
{target_language_line}
main rules: {user_rules_section}
Do not wrap the output in quotation marks.
{user_prompt_section}
{instruction_section}
{additional_context_section}
{source_text_block}
"""

def get_specialized_prompt(
    source_text: str | None = None,
    target_language: str | None = None,
    user_rules: str | None = None,
    user_prompt: str | None = None,
    instruction: str | None = None,
    contexts: list[str] | None = None,
) -> str:
    target_language_line = f"target language: {target_language}" if target_language else ""
    source_text_clean = (source_text or "").strip()
    source_text_block = f"source text: {source_text_clean}" if source_text_clean else ""

    user_prompt_section = ""
    if user_prompt:
        user_prompt_section = f"user instructions: {user_prompt.strip()}"

    instruction_section = ""
    if instruction:
        instruction_section = f"instruction: {instruction.strip()}"

    additional_context_section = ""
    if contexts:
        context_parts = []
        for idx, context in enumerate(contexts, 1):
            context_parts.append(f"Context {idx}:\n{context.strip()}")
        additional_context_section = f"additional_context:\n{chr(10).join(context_parts)}"
    else:
        additional_context_section = "additional_context:"

    return PROMPT_TEMPLATE.format(
        target_language_line=target_language_line,
        user_rules_section=(user_rules or "").strip(),
        user_prompt_section=user_prompt_section,
        instruction_section=instruction_section,
        additional_context_section=additional_context_section,
        source_text_block=source_text_block,
    )


ENHANCE_META_PROMPT = """You are an expert prompt engineer. Your task is to enhance and improve the given system prompt while preserving the user's original intent and purpose.

Guidelines for enhancement:
- Make the instructions clearer and more specific
- Add structure (e.g., role definition, constraints, output format) where beneficial
- Remove ambiguity and vagueness
- Maintain the original language and tone the user intended
- Keep it concise — don't add unnecessary verbosity
- If the prompt references specific domains or tasks, sharpen those references

Return ONLY the enhanced system prompt text. Do not include any explanation, commentary, or markdown formatting around it.

Original system prompt to enhance:
{prompt}"""