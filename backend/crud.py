
from sqlalchemy.orm import Session

from backend import models
from backend.schemas import ConversationCreate, MessageCreate


def create_conversation(db: Session, conversation: ConversationCreate):
    db_conversation = models.Conversation(
        title=conversation.title or "New Chat"
    )

    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation


def get_conversation(db: Session, conversation_id: int):
    return (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id)
        .first()
    )


def get_all_conversations(db: Session):
    return (
        db.query(models.Conversation)
        .order_by(models.Conversation.created_at.desc())
        .all()
    )


def create_message(
    db: Session,
    conversation_id: int,
    message: MessageCreate
):
    db_message = models.Message(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message


def get_messages(db: Session, conversation_id: int):
    return (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )


def delete_conversation(db: Session, conversation_id: int):
    conversation = get_conversation(db, conversation_id)

    if conversation:
        db.delete(conversation)
        db.commit()
        return True

    return False
