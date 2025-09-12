from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response_data = chat_service.get_random_response(request.message)
    return ChatResponse(**response_data)