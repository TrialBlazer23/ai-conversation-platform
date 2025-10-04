"""
Conversation management module with database integration
Enhanced with persistence and token tracking
"""
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from database import (
    db,
    Conversation as ConversationModel,
    Message as MessageModel,
    ModelConfig as ModelConfigModel,
)
from utils.token_counter import TokenCounter
from utils.helpers import calculate_cost


class ConversationManager:
    """
    Manages conversations with database persistence
    Follows Single Responsibility Principle
    """

    def create_conversation(self, initial_prompt: str, model_configs: List[Dict]) -> str:
        """
        Create a new conversation with database persistence

        Args:
            initial_prompt: Starting prompt for the conversation
            model_configs: List of model configurations

        Returns:
            conversation_id: Unique identifier for the conversation
        """
        conversation_id = str(uuid.uuid4())

        # Create conversation in database
        conversation = ConversationModel(
            id=conversation_id,
            initial_prompt=initial_prompt,
            status='active',
            current_model_idx=0
        )

        # Add initial message
        initial_message = MessageModel(
            conversation_id=conversation_id,
            role='user',
            content=initial_prompt,
            model_name='User'
        )

        conversation.messages.append(initial_message)

        # Add model configurations
        for idx, config in enumerate(model_configs):
            model_config = ModelConfigModel(
                conversation_id=conversation_id,
                provider=config.get('provider'),
                model=config.get('model'),
                name=config.get('name', config.get('model')),
                temperature=config.get('temperature', 0.7),
                system_prompt=config.get('system_prompt', ''),
                order_index=idx
            )
            conversation.model_configs.append(model_config)

        db.session.add(conversation)
        db.session.commit()

        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Retrieve a conversation by ID

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation dictionary or None
        """
        conversation = db.session.get(ConversationModel, conversation_id)
        if not conversation:
            return None

        return conversation.to_dict()

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model_name: Optional[str] = None,
        tokens_used: int = 0,
        cost: float = 0.0,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Add a message to a conversation

        Args:
            conversation_id: Conversation identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            model_name: Name of the model that generated the message
            tokens_used: Number of tokens used
            cost: Cost of the message generation
            metadata: Additional metadata

        Returns:
            Success status
        """
        conversation = db.session.get(ConversationModel, conversation_id)
        if not conversation:
            return False

        message = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model_name=model_name,
            tokens_used=tokens_used,
            cost=cost,
            metadata=metadata
        )

        # Update conversation totals
        conversation.total_tokens += tokens_used
        conversation.total_cost += cost
        conversation.updated_at = datetime.utcnow()

        db.session.add(message)
        db.session.commit()

        return True

    def update_current_model(self, conversation_id: str, model_idx: int) -> bool:
        """
        Update the current model index

        Args:
            conversation_id: Conversation identifier
            model_idx: New model index

        Returns:
            Success status
        """
        conversation = db.session.get(ConversationModel, conversation_id)
        if not conversation:
            return False

        conversation.current_model_idx = model_idx
        conversation.updated_at = datetime.utcnow()
        db.session.commit()

        return True

    def get_messages(self, conversation_id: str) -> List[Dict]:
        """
        Get all messages from a conversation

        Args:
            conversation_id: Conversation identifier

        Returns:
            List of message dictionaries
        """
        conversation = db.session.get(ConversationModel, conversation_id)
        if not conversation:
            return []

        return [msg.to_dict() for msg in conversation.messages]

    def get_messages_for_api(self, conversation_id: str) -> List[Dict]:
        """
        Get messages formatted for API calls

        Args:
            conversation_id: Conversation identifier

        Returns:
            List of messages in API format
        """
        conversation = db.session.get(ConversationModel, conversation_id)
        if not conversation:
            return []

        return [
            {'role': msg.role, 'content': msg.content}
            for msg in conversation.messages
        ]

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation

        Args:
            conversation_id: Conversation identifier

        Returns:
            Success status
        """
        conversation = db.session.get(ConversationModel, conversation_id)
        if not conversation:
            return False

        db.session.delete(conversation)
        db.session.commit()

        return True

    def list_conversations(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        List all conversations

        Args:
            limit: Maximum number of conversations to return
            offset: Offset for pagination

        Returns:
            List of conversation summaries
        """
        conversations = (
            db.session.query(ConversationModel)
            .order_by(ConversationModel.updated_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [
            {
                'id': conv.id,
                'initial_prompt': conv.initial_prompt[:100] + '...'
                if len(conv.initial_prompt) > 100
                else conv.initial_prompt,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': len(conv.messages),
                'total_tokens': conv.total_tokens,
                'total_cost': conv.total_cost,
                'status': conv.status,
            }
            for conv in conversations
        ]

    def get_token_usage(self, conversation_id: str) -> Dict:
        """
        Get token usage statistics for a conversation

        Args:
            conversation_id: Conversation identifier

        Returns:
            Token usage statistics
        """
        conversation = db.session.get(ConversationModel, conversation_id)
        if not conversation:
            return {}

        # Get current model to determine token limits
        current_config = (
            conversation.model_configs[conversation.current_model_idx]
            if conversation.model_configs
            else None
        )

        if current_config:
            counter = TokenCounter(model=current_config.model)
            messages = self.get_messages_for_api(conversation_id)
            return counter.get_context_usage(messages)

        return {
            'used': conversation.total_tokens,
            'max': 0,
            'available': 0,
            'percentage': 0,
            'warning': False,
            'exceeded': False,
        }