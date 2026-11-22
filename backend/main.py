from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend import models, crud, schemas
from backend.ai_service import get_ai_response


# Create database tables
Base.metadata.create_all(bind=engine)


# FastAPI application
app = FastAPI(
    title="Vijay AI Chatbot API",
    description="A full-stack AI chatbot built with FastAPI and PostgreSQL",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Vijay AI Chatbot!",
        "status": "Running"
    }


# Create conversation
@app.post("/conversations", response_model=schemas.ConversationResponse)
def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_conversation(db, conversation)


# Get all conversations
@app.get("/conversations")
def get_all_conversations(db: Session = Depends(get_db)):
    return crud.get_all_conversations(db)


# Get one conversation
@app.get(
    "/conversations/{conversation_id}",
    response_model=schemas.ConversationResponse
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation(db, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conversation


# Delete conversation
@app.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_conversation(db, conversation_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {"message": "Conversation deleted successfully"}


# Add message to conversation
@app.post("/conversations/{conversation_id}/messages")
def add_message(
    conversation_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation(db, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    if message.role not in ["user", "assistant"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid message role"
        )

    return crud.create_message(db, conversation_id, message)


# Get conversation messages
@app.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[schemas.MessageResponse]
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation(db, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return crud.get_messages(db, conversation_id)
    # Rename conversation
@app.patch("/conversations/{conversation_id}/title")
def rename_conversation(
    conversation_id: int,
    title: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation(db, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    new_title = title.strip()

    if not new_title:
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    conversation.title = new_title[:40]
    db.commit()
    db.refresh(conversation)

    return {
        "message": "Chat renamed successfully",
        "id": conversation.id,
        "title": conversation.title
    }


# Chat with AI and remember conversation history
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db)
):
    # Create a new conversation if needed
    if request.conversation_id is None:
        conversation = crud.create_conversation(
            db,
            schemas.ConversationCreate(title="New Chat")
        )
        conversation_id = conversation.id

    else:
        conversation_id = request.conversation_id
        conversation = crud.get_conversation(db, conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

    # Save the user's new message
    user_message = schemas.MessageCreate(
        role="user",
        content=request.message
    )
    crud.create_message(db, conversation_id, user_message)

    # Generate automatic conversation title
    conversation = crud.get_conversation(db, conversation_id)

    if conversation and conversation.title == "New Chat":
        title = " ".join(request.message.strip().split())
        conversation.title = title[:40]
        db.commit()

    # Load conversation history from database
    conversation_messages = crud.get_messages(
        db,
        conversation_id
    )

    # Prepare the last 10 messages for Ollama
    messages = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in conversation_messages[-10:]
    ]

    # Generate AI response using conversation memory
    bot_response = get_ai_response(messages)

    # Save AI response
    assistant_message = schemas.MessageCreate(
        role="assistant",
        content=bot_response
    )

    crud.create_message(db, conversation_id, assistant_message)

    return schemas.ChatResponse(
        conversation_id=conversation_id,
        user_message=request.message,
        bot_response=bot_response
    )
