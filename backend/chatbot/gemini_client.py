import os
import json
import google.generativeai as genai
from .knowledge_base import SCORESEVA_PROJECT_KNOWLEDGE
from config import get_settings

settings = get_settings()
api_key = settings.gemini_api_key

if api_key:
    genai.configure(api_key=api_key)

def ask_gemini(message: str, history: list, context: dict = None) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        system_prompt = f"""You are the ScoreSeva Assistant, embedded in a
live demo of the ScoreSeva alternative credit scoring platform.

{SCORESEVA_PROJECT_KNOWLEDGE}

RULES:
1. You may answer general questions about ScoreSeva freely using the
   project knowledge above.
2. If a persona's score data is provided below, you may discuss ONLY
   the specific numbers and facts given — never compute, estimate,
   or guess a number that isn't explicitly provided.
3. If asked something about a specific persona's score and no context
   is provided below, say so plainly: "I don't have an active score
   loaded right now — load a persona on the Score page first."
4. If asked something outside ScoreSeva's scope (general life advice,
   unrelated topics), politely redirect to what you can help with.
5. Keep answers concise — 2-4 sentences unless the user asks for more
   detail. This is a live demo; long responses break the pace.

CURRENT PERSONA CONTEXT (use only these facts for persona-specific questions):
{json.dumps(context, indent=2) if context else "No persona is currently loaded."}
"""

        # Build conversation history
        # Gemini expects roles to be 'user' or 'model'
        formatted_history = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg.get("content", "")]})
            
        chat = model.start_chat(history=formatted_history)
        
        # Combine system prompt with user message for the current turn if needed?
        # Actually Gemini has system_instruction, but it might require specific SDK usage.
        # Wait, the instruction says:
        # "call model.generate_content() with the system prompt prepended"
        
        # If we use generate_content with prepended prompt:
        # It's better to just build the full prompt string for generate_content if we don't use chat history directly in generate_content.
        # But the user asked to build the conversation as alternating turns.
        # Let's prepend the system prompt to the user's message.
        
        full_message = f"{system_prompt}\n\nUser Message:\n{message}"
        
        response = chat.send_message(full_message)
        return response.text
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Sorry, I'm having trouble connecting to my knowledge base right now. Please try again in a moment."
