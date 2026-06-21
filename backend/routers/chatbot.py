from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from chatbot.gemini_client import ask_gemini

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    context: Optional[Dict[str, Any]] = None

@router.post("/ask")
async def ask_chatbot(request: ChatRequest):
    try:
        response = ask_gemini(
            message=request.message,
            history=request.history,
            context=request.context
        )
        return {"response": response, "reply": response}
    except Exception as e:
        print(f"Error in ask_chatbot: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message.")
