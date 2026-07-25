from ai_agent.gemini_client import ask_gemini

def chat_turn(user_message: str, conversation_history: list[dict] = None) -> tuple[str, list[dict]]:
    """
    Handles a single conversational turn with Kritiq.
    Keeps prompts reasonable by including only the last 5-10 turns of history.
    """
    if conversation_history is None:
        conversation_history = []

    # Limit to the last 10 turns (user + assistant pairs) to keep prompt size reasonable
    recent_history = conversation_history[-10:]

    # Build the prompt with history format
    prompt_parts = [
        "You are Kritiq, a helpful AI code review and development assistant.",
        "Answer the developer's questions about code, reviews, and general software development.",
        "Below is the conversation history followed by the user's latest message.\n"
    ]

    for turn in recent_history:
        role = "Developer" if turn.get("role") == "user" else "Kritiq"
        prompt_parts.append(f"{role}: {turn.get('content', '')}")

    prompt_parts.append(f"Developer: {user_message}")
    prompt_parts.append("Kritiq:")

    combined_prompt = "\n\n".join(prompt_parts)

    # Call the primary AI model (with fallback logic embedded)
    response_text = ask_gemini(combined_prompt)

    # Append the new turn to history
    updated_history = list(conversation_history)
    updated_history.append({"role": "user", "content": user_message})
    updated_history.append({"role": "assistant", "content": response_text})

    return response_text, updated_history
