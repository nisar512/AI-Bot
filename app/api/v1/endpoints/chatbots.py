from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.chatbot import Chatbot, ChatbotCreate, ChatbotUpdate
from app.schemas.document import Document, DocumentCreate
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryResponse
from app.schemas.session import SessionList
from app.services.chatbot import (
    get_chatbot,
    get_chatbots_by_user,
    create_chatbot,
    update_chatbot,
    delete_chatbot
)
from app.services.document_processor import extract_text_from_file
from app.services.document import create_document
from app.services.elasticsearch import search_documents
from app.services.chat_history import create_chat_history, get_chat_history
from app.services.session import get_session, get_or_create_session, get_user_sessions_with_first_message
from app.core.config import settings
import os
import tempfile
import requests
from pydantic import BaseModel
import json

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    chatbot_id: int
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []
    session_id: str

@router.post("/", response_model=Chatbot, status_code=status.HTTP_201_CREATED)
def create_new_chatbot(chatbot: ChatbotCreate, db: Session = Depends(get_db)):
    """Create a new chatbot."""
    try:
        return create_chatbot(db=db, chatbot=chatbot)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chatbot: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[Chatbot])
def read_user_chatbots(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all chatbots for a specific user."""
    chatbots = get_chatbots_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return chatbots

@router.get("/{chatbot_id}", response_model=Chatbot)
def read_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    """Get a specific chatbot by ID."""
    db_chatbot = get_chatbot(db, chatbot_id=chatbot_id)
    if db_chatbot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    return db_chatbot

@router.put("/{chatbot_id}", response_model=Chatbot)
def update_existing_chatbot(
    chatbot_id: int,
    chatbot: ChatbotUpdate,
    db: Session = Depends(get_db)
):
    """Update a chatbot."""
    db_chatbot = update_chatbot(db=db, chatbot_id=chatbot_id, chatbot=chatbot)
    if db_chatbot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    return db_chatbot

@router.delete("/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    """Delete a chatbot."""
    if not delete_chatbot(db=db, chatbot_id=chatbot_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    return None

@router.post("/{chatbot_id}/upload-document", response_model=Document)
async def upload_document(
    chatbot_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document for a specific chatbot.
    Supported file types: docx, pptx, pdf, txt
    """
    try:
        # Verify chatbot exists
        chatbot = get_chatbot(db, chatbot_id=chatbot_id)
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )

        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lower().lstrip('.')
        if file_extension not in ['docx', 'pptx', 'pdf', 'txt']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Supported types: docx, pptx, pdf, txt"
            )

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Extract text from file
        content = extract_text_from_file(temp_file_path, file_extension)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the file"
            )

        # Create document in Elasticsearch
        document = create_document(
            db=db,
            document=DocumentCreate(
                chatbot_id=chatbot_id,
                content=content,
                metadata={
                    "filename": file.filename,
                    "file_type": file_extension,
                    "original_size": len(content)
                }
            )
        )

        return document

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@router.post("/{chatbot_id}/chat")
async def chat_with_bot(
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Chat with a specific chatbot using semantic search and OpenRouter with streaming response
    """
    try:
        # Verify chatbot exists
        chatbot = get_chatbot(db, chatbot_id=message.chatbot_id)
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )

        # Get or create session
        session = get_or_create_session(db, message.session_id, message.chatbot_id)

        # Get recent chat history for context
        recent_chats = get_chat_history(db, session_id=session.id, limit=5)
        recent_chats.sort(key=lambda x: x.created_at)
        chat_history = "\n".join([f"{chat.role}: {chat.message}" for chat in recent_chats])

        # Get relevant documents from Elasticsearch
        relevant_docs = search_documents(
            index_id=chatbot.index_id,
            query=message.message,
            size=3  # Get top 3 most relevant documents
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
                                    chatbot_id=message.chatbot_id,
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

@router.get("/{chatbot_id}/chat/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history_by_session(
    chatbot_id: int,
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get chat history for a specific session and chatbot
    """
    try:
        # Verify chatbot exists
        chatbot = get_chatbot(db, chatbot_id=chatbot_id)
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )

        # Verify session exists and belongs to the chatbot
        session = get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.chatbot_id != chatbot_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session does not belong to this chatbot"
            )

        # Get chat history
        messages = get_chat_history(db, session_id=session_id, skip=skip, limit=limit)
        
        # Order messages by created_at in ascending order for chronological display
        messages.sort(key=lambda x: x.created_at)
        
        return {"messages": messages}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@router.get("/user/{user_id}/sessions", response_model=SessionList)
def get_user_sessions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all sessions for a user with their first messages
    """
    try:
        sessions = get_user_sessions_with_first_message(db, user_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        ) 