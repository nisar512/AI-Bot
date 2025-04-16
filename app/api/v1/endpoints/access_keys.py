from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.access_key import AccessKey, AccessKeyCreate
from app.services.access_key import create_access_key, deactivate_access_key, validate_access_key
from app.services.chatbot import get_chatbot
from app.api.v1.endpoints.chatbots import ChatMessage, ChatResponse
from app.services.session import get_or_create_session
from app.services.chat_history import get_chat_history, create_chat_history
from app.services.elasticsearch import search_documents
from app.core.config import settings
import requests
import json
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/", response_model=AccessKey, status_code=status.HTTP_201_CREATED)
def create_new_access_key(
    access_key: AccessKeyCreate,
    db: Session = Depends(get_db)
):
    """Create a new access key for a chatbot"""
    try:
        return create_access_key(db=db, access_key=access_key)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating access key: {str(e)}"
        )

@router.post("/{key}/deactivate", response_model=AccessKey)
def deactivate_existing_access_key(
    key: str,
    db: Session = Depends(get_db)
):
    """Deactivate an access key"""
    try:
        return deactivate_access_key(db=db, key=key)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating access key: {str(e)}"
        )

@router.post("/{key}/chat")
async def chat_with_bot_using_key(
    key: str,
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Chat with a chatbot using an access key
    """
    try:
        # Validate access key and get chatbot
        access_key = validate_access_key(db, key)
        chatbot = get_chatbot(db, chatbot_id=access_key.chatbot_id)
        
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )

        # Get or create session
        session = get_or_create_session(db, message.session_id, chatbot.id)

        # Get recent chat history for context
        recent_chats = get_chat_history(db, session_id=session.id, limit=5)
        recent_chats.sort(key=lambda x: x.created_at)
        chat_history = "\n".join([f"{chat.role}: {chat.message}" for chat in recent_chats])

        # Get relevant documents from Elasticsearch
        relevant_docs = search_documents(
            index_id=chatbot.index_id,
            query=message.message,
            size=3
        )

        # Prepare context from relevant documents
        context = "\n\n".join([doc["content"] for doc in relevant_docs])

        # Prepare the prompt for OpenRouter
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.
If the answer cannot be found in the context, say that you don't know.

Previous conversation:
{chat_history}

Context:
{context}

User Question: {message.message}

Answer:"""

        # Call OpenRouter API with streaming
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/yourrepo",
            "X-Title": "Your App Name"
        }

        data = {
            "model": "openai/gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant that answers questions based on the provided context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": True
        }

        full_response = ""

        async def generate():
            nonlocal full_response
            with requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                stream=True
            ) as response:
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error calling OpenRouter API: {response.text}"
                    )

                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]  # Remove 'data: ' prefix
                            if line.strip() == '[DONE]':
                                # Store the complete chat history
                                create_chat_history(
                                    db=db,
                                    session_id=session.id,
                                    chatbot_id=chatbot.id,
                                    user_message=message.message,
                                    assistant_response=full_response
                                )
                                break
                            try:
                                chunk = json.loads(line)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    content = chunk['choices'][0].get('delta', {}).get('content', '')
                                    if content:
                                        full_response += content
                                        yield f"data: {json.dumps({'content': content, 'session_id': session.id})}\n\n"
                            except json.JSONDecodeError:
                                continue

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        ) 