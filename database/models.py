"""
Database models for conversation persistence
Follows Single Responsibility and Separation of Concerns
"""
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from .session import db


class Conversation(db.Model):
    """
    Conversation entity - represents a complete AI conversation session
    """
    __tablename__ = 'conversations'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    initial_prompt: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default='active')
    current_model_idx: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    model_configs: Mapped[List["ModelConfig"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'initial_prompt': self.initial_prompt,
            'status': self.status,
            'current_model_idx': self.current_model_idx,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost,
            'messages': [msg.to_dict() for msg in self.messages],
            'model_configs': [cfg.to_dict() for cfg in self.model_configs]
        }


class Message(db.Model):
    """
    Message entity - individual messages in a conversation
    """
    __tablename__ = 'messages'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey('conversations.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    role: Mapped[str] = mapped_column(String(20))  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'model': self.model_name,
            'timestamp': self.created_at.isoformat(),
            'tokens_used': self.tokens_used,
            'cost': self.cost,
            'metadata': self.extra_metadata or {}
        }


class ModelConfig(db.Model):
    """
    Model configuration entity - stores model settings for a conversation
    """
    __tablename__ = 'model_configs'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey('conversations.id'))
    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="model_configs")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            'provider': self.provider,
            'model': self.model,
            'name': self.name,
            'temperature': self.temperature,
            'system_prompt': self.system_prompt,
            'order_index': self.order_index
        }