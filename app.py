"""
Enhanced Flask application with streaming, database persistence, and advanced features
"""
from flask import Flask, render_template, request, jsonify, session, Response, stream_with_context, g
from flask_cors import CORS
import json
import os
import time
from datetime import datetime
from pathlib import Path
from functools import wraps

from database import init_db, db
from models.conversation import ConversationManager
from models.ai_provider import AIProviderFactory
from utils.token_counter import TokenCounter
from utils.helpers import calculate_cost
from utils.config_validator import ConfigValidator
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize database
init_db(app)

# Initialize conversation manager
conversation_manager = ConversationManager()


# --- Middleware for Request Validation and Timing ---

@app.before_request
def before_request():
    """Track request start time for response time measurement"""
    g.start_time = time.time()


@app.after_request
def after_request(response):
    """Add response time header and CORS headers"""
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        response.headers['X-Response-Time'] = f'{elapsed:.3f}s'
    
    # Additional security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    
    return response


def validate_json_request(required_fields=None):
    """Decorator to validate JSON requests"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'status': 'error',
                    'message': 'Content-Type must be application/json'
                }), 400
            
            if required_fields:
                data = request.get_json()
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'status': 'error',
                        'message': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


# --- Conversation Search/Filter Endpoint ---
from database.models import Conversation, Message, ModelConfig
from sqlalchemy import or_, and_

@app.route('/api/conversations/search', methods=['GET'])
def search_conversations():
    """Search and filter conversations by text, model, date, tokens, and cost"""
    query = request.args.get('q', '').strip()
    model = request.args.get('model')
    status = request.args.get('status')
    favorites_only = request.args.get('favorites_only', '').lower() == 'true'
    min_tokens = request.args.get('min_tokens', type=int)
    max_tokens = request.args.get('max_tokens', type=int)
    min_cost = request.args.get('min_cost', type=float)
    max_cost = request.args.get('max_cost', type=float)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    filters = []
    if query:
        filters.append(or_(Conversation.initial_prompt.ilike(f'%{query}%'),
                           Conversation.status.ilike(f'%{query}%'),
                           Conversation.id.ilike(f'%{query}%')))
    if model:
        filters.append(Conversation.model_configs.any(model_name=model))
    if status:
        filters.append(Conversation.status == status)
    if favorites_only:
        filters.append(Conversation.is_favorite == True)
    if min_tokens is not None:
        filters.append(Conversation.total_tokens >= min_tokens)
    if max_tokens is not None:
        filters.append(Conversation.total_tokens <= max_tokens)
    if min_cost is not None:
        filters.append(Conversation.total_cost >= min_cost)
    if max_cost is not None:
        filters.append(Conversation.total_cost <= max_cost)
    if start_date:
        filters.append(Conversation.created_at >= start_date)
    if end_date:
        filters.append(Conversation.created_at <= end_date)

    qset = Conversation.query
    if filters:
        qset = qset.filter(and_(*filters))
    # Sorting
    if sort_by in ['created_at', 'updated_at', 'total_tokens', 'total_cost']:
        sort_col = getattr(Conversation, sort_by)
        if sort_order == 'desc':
            qset = qset.order_by(sort_col.desc())
        else:
            qset = qset.order_by(sort_col.asc())
    conversations = qset.limit(100).all()
    return jsonify([conv.to_dict() for conv in conversations])


@app.route('/api/conversations/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history with optional filters"""
    favorites_only = request.args.get('favorites_only', '').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    qset = Conversation.query
    if favorites_only:
        qset = qset.filter(Conversation.is_favorite == True)
    
    # Always sort by most recent first
    qset = qset.order_by(Conversation.updated_at.desc())
    
    # Get total count for pagination
    total = qset.count()
    
    # Apply pagination
    conversations = qset.limit(limit).offset(offset).all()
    
    return jsonify({
        'conversations': [conv.to_dict() for conv in conversations],
        'total': total,
        'limit': limit,
        'offset': offset,
        'has_more': (offset + limit) < total
    })


@app.route('/')
def index():
    """Render main application page"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Handle configuration management"""
    if request.method == 'POST':
        config_data = request.json
        session['config'] = config_data
        return jsonify({'status': 'success', 'message': 'Configuration saved'})
    else:
        config = session.get('config', {})
        return jsonify(config)


@app.route('/api/config/validate', methods=['POST'])
def validate_config():
    """Validate API keys and model configurations"""
    try:
        data = request.json
        api_keys = data.get('api_keys', {})
        models = data.get('models', [])
        
        # Perform comprehensive validation
        results = ConfigValidator.validate_all_configs(api_keys, models)
        
        # Also check Ollama if any models use it
        uses_ollama = any(m.get('provider') == 'ollama' for m in models)
        if uses_ollama:
            ollama_available, ollama_msg = ConfigValidator.check_ollama_connection()
            results['ollama'] = {
                'available': ollama_available,
                'message': ollama_msg
            }
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'message': 'Validation failed'
        }), 500


@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Return available AI providers with their models"""
    providers = AIProviderFactory.get_available_providers()
    return jsonify(providers)


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Return available conversation templates"""
    templates = []
    templates_dir = Config.TEMPLATES_PATH
    
    if templates_dir.exists():
        for template_file in templates_dir.glob('*.json'):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    template_data['id'] = template_file.stem
                    templates.append(template_data)
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
    
    return jsonify(templates)


@app.route('/api/conversation/start', methods=['POST'])
def start_conversation():
    """Initialize a new conversation"""
    try:
        data = request.json
        initial_prompt = data.get('initial_prompt', '')
        model_configs = data.get('models', [])
        
        if not initial_prompt:
            return jsonify({'status': 'error', 'message': 'Initial prompt required'}), 400
        
        if not model_configs:
            return jsonify({'status': 'error', 'message': 'At least one model required'}), 400
        
        conversation_id = conversation_manager.create_conversation(
            initial_prompt=initial_prompt,
            model_configs=model_configs
        )
        
        return jsonify({
            'status': 'success',
            'conversation_id': conversation_id,
            'message': 'Conversation started'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversation/<conversation_id>/next', methods=['POST'])
def next_turn(conversation_id):
    """Process next turn in conversation (non-streaming)"""
    try:
        data = request.json
        config = session.get('config', {})
        edited_message = data.get('edited_message')
        
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        # Get next model in rotation
        current_model_idx = conversation.get('current_model_idx', 0)
        model_configs = conversation.get('model_configs', [])
        
        if not model_configs:
            return jsonify({'status': 'error', 'message': 'No models configured'}), 400
        
        current_model = model_configs[current_model_idx]
        
        # Create provider instance
        provider = AIProviderFactory.create_provider(
            provider_type=current_model.get('provider'),
            api_key=config.get('api_keys', {}).get(current_model.get('provider')),
            model=current_model.get('model'),
            temperature=current_model.get('temperature', 0.7),
            system_prompt=current_model.get('system_prompt', '')
        )
        
        # Get conversation history for API
        messages = conversation_manager.get_messages_for_api(conversation_id)
        
        # Use edited message if provided
        if edited_message and messages:
            messages[-1]['content'] = edited_message
        
        # Count tokens before generation
        counter = TokenCounter(model=current_model.get('model'))
        input_tokens = counter.count_messages_tokens(messages)
        
        # Generate response
        response = provider.generate_response(messages)
        
        # Debug: Log the response
        print(f"DEBUG: Generated response type: {type(response)}")
        print(f"DEBUG: Generated response length: {len(response) if response else 0}")
        print(f"DEBUG: Generated response preview: {response[:200] if response else 'None'}")
        
        # Count output tokens
        output_tokens = counter.count_tokens(response)
        
        # Calculate cost
        cost = calculate_cost(
            current_model.get('model'),
            input_tokens,
            output_tokens
        )
        
        # Add response to conversation
        conversation_manager.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=response,
            model_name=current_model.get('name', current_model.get('model')),
            tokens_used=input_tokens + output_tokens,
            cost=cost
        )
        
        # Update current model index
        next_model_idx = (current_model_idx + 1) % len(model_configs)
        conversation_manager.update_current_model(conversation_id, next_model_idx)
        
        # Get token usage
        token_usage = conversation_manager.get_token_usage(conversation_id)
        
        response_data = {
            'status': 'success',
            'message': {
                'role': 'assistant',
                'content': response,
                'model': current_model.get('name', current_model.get('model')),
                'timestamp': datetime.utcnow().isoformat(),
                'tokens_used': input_tokens + output_tokens,
                'cost': cost
            },
            'next_model': model_configs[next_model_idx].get('name', model_configs[next_model_idx].get('model')),
            'token_usage': token_usage
        }
        
        # Debug: Log the response data
        print(f"DEBUG: Response data: {json.dumps(response_data, indent=2)}")
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversation/<conversation_id>/next/stream', methods=['POST'])
def next_turn_stream(conversation_id):
    """Process next turn with streaming response"""
    
    def generate():
        try:
            data = request.json
            config = session.get('config', {})
            edited_message = data.get('edited_message')
            
            conversation = conversation_manager.get_conversation(conversation_id)
            if not conversation:
                yield f"data: {json.dumps({'error': 'Conversation not found'})}\n\n"
                return
            
            # Get next model in rotation
            current_model_idx = conversation.get('current_model_idx', 0)
            model_configs = conversation.get('model_configs', [])
            
            if not model_configs:
                yield f"data: {json.dumps({'error': 'No models configured'})}\n\n"
                return
            
            current_model = model_configs[current_model_idx]
            
            # Send metadata first
            yield f"data: {json.dumps({'type': 'metadata', 'model': current_model.get('name'), 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            
            # Create provider instance
            provider = AIProviderFactory.create_provider(
                provider_type=current_model.get('provider'),
                api_key=config.get('api_keys', {}).get(current_model.get('provider')),
                model=current_model.get('model'),
                temperature=current_model.get('temperature', 0.7),
                system_prompt=current_model.get('system_prompt', '')
            )
            
            # Get conversation history
            messages = conversation_manager.get_messages_for_api(conversation_id)
            
            # Use edited message if provided
            if edited_message and messages:
                messages[-1]['content'] = edited_message
            
            # Count input tokens
            counter = TokenCounter(model=current_model.get('model'))
            input_tokens = counter.count_messages_tokens(messages)
            
            # Stream response
            full_response = ""
            for chunk in provider.generate_response_stream(messages):
                full_response += chunk
                print(f"DEBUG STREAM: Chunk received: {chunk[:50]}")
                yield f"data: {json.dumps({'type': 'content', 'chunk': chunk})}\n\n"
            
            print(f"DEBUG STREAM: Full response length: {len(full_response)}")
            print(f"DEBUG STREAM: Full response preview: {full_response[:200]}")
            
            # Count output tokens
            output_tokens = counter.count_tokens(full_response)
            
            # Calculate cost
            cost = calculate_cost(
                current_model.get('model'),
                input_tokens,
                output_tokens
            )
            
            # Save to database
            conversation_manager.add_message(
                conversation_id=conversation_id,
                role='assistant',
                content=full_response,
                model_name=current_model.get('name', current_model.get('model')),
                tokens_used=input_tokens + output_tokens,
                cost=cost
            )
            
            # Update current model index
            next_model_idx = (current_model_idx + 1) % len(model_configs)
            conversation_manager.update_current_model(conversation_id, next_model_idx)
            
            # Get token usage
            token_usage = conversation_manager.get_token_usage(conversation_id)
            
            # Send completion metadata
            yield f"data: {json.dumps({'type': 'done', 'tokens_used': input_tokens + output_tokens, 'cost': cost, 'next_model': model_configs[next_model_idx].get('name'), 'token_usage': token_usage})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Retrieve conversation history"""
    conversation = conversation_manager.get_conversation(conversation_id)
    if not conversation:
        return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
    
    return jsonify({
        'status': 'success',
        'conversation': conversation
    })


@app.route('/api/conversation/<conversation_id>/export', methods=['GET'])
def export_conversation(conversation_id):
    """Export conversation to JSON"""
    conversation = conversation_manager.get_conversation(conversation_id)
    if not conversation:
        return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
    
    return jsonify(conversation)


@app.route('/api/conversation/<conversation_id>/export/markdown', methods=['GET'])
def export_conversation_markdown(conversation_id):
    """Export conversation to Markdown format"""
    try:
        # Get conversation from database
        from database.session import db
        conversation = db.session.get(Conversation, conversation_id)
        if not conversation:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        # Get messages for this conversation
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
        
        # Generate Markdown content
        markdown_content = f"""# Conversation Export

**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {conversation.status}  
**Total Tokens:** {conversation.total_tokens:,}  
**Total Cost:** ${conversation.total_cost:.4f}

## Initial Prompt

{conversation.initial_prompt}

---

## Conversation Messages

"""
        
        for i, message in enumerate(messages, 1):
            # Format timestamp
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            # Add message header
            markdown_content += f"### Message {i}: {message.role.title()}"
            if message.model_name:
                markdown_content += f" ({message.model_name})"
            markdown_content += f"\n\n**Time:** {timestamp}  \n"
            
            if message.tokens_used > 0:
                markdown_content += f"**Tokens:** {message.tokens_used:,}  \n"
            if message.cost > 0:
                markdown_content += f"**Cost:** ${message.cost:.4f}  \n"
            
            markdown_content += "\n"
            
            # Add message content
            markdown_content += f"{message.content}\n\n---\n\n"
        
        # Add summary
        markdown_content += f"""## Summary

- **Total Messages:** {len(messages)}
- **Total Tokens:** {conversation.total_tokens:,}
- **Total Cost:** ${conversation.total_cost:.4f}
- **Duration:** {(conversation.updated_at - conversation.created_at).total_seconds() / 60:.1f} minutes

*Exported from AI Conversation Platform on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
        
        # Return as downloadable file
        response = app.response_class(
            markdown_content,
            mimetype='text/markdown',
            headers={
                'Content-Disposition': f'attachment; filename="conversation_{conversation_id[:8]}.md"'
            }
        )
        return response
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversation/<conversation_id>/tokens', methods=['GET'])
def get_token_usage(conversation_id):
    """Get token usage for conversation"""
    token_usage = conversation_manager.get_token_usage(conversation_id)
    if not token_usage:
        return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
    
    return jsonify({
        'status': 'success',
        'token_usage': token_usage
    })


@app.route('/api/conversation/<conversation_id>/favorite', methods=['POST'])
def toggle_favorite(conversation_id):
    """Toggle favorite status of a conversation"""
    try:
        from database.session import db
        conversation = db.session.get(Conversation, conversation_id)
        if not conversation:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        # Toggle favorite status
        conversation.is_favorite = not conversation.is_favorite
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'is_favorite': conversation.is_favorite,
            'message': f"Conversation {'added to' if conversation.is_favorite else 'removed from'} favorites"
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversation/<conversation_id>/title', methods=['PUT'])
def update_title(conversation_id):
    """Update conversation title"""
    try:
        data = request.json
        new_title = data.get('title', '').strip()
        
        from database.session import db
        conversation = db.session.get(Conversation, conversation_id)
        if not conversation:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        # Update title (empty string will use initial_prompt as fallback)
        conversation.title = new_title if new_title else None
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        display_title = conversation.title or conversation.initial_prompt[:60] + ('...' if len(conversation.initial_prompt) > 60 else '')
        
        return jsonify({
            'status': 'success',
            'title': conversation.title,
            'display_title': display_title,
            'message': 'Title updated successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversation/<conversation_id>/duplicate', methods=['POST'])
def duplicate_conversation(conversation_id):
    """Duplicate a conversation"""
    try:
        from database.session import db
        import uuid
        
        original = db.session.get(Conversation, conversation_id)
        if not original:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        # Create new conversation
        new_id = str(uuid.uuid4())
        new_conversation = Conversation(
            id=new_id,
            initial_prompt=original.initial_prompt,
            status='active',
            title=f"Copy of {original.title or 'Conversation'}"
        )
        
        # Copy model configs
        for config in original.model_configs:
            new_config = ModelConfig(
                conversation_id=new_id,
                provider=config.provider,
                model=config.model,
                name=config.name,
                temperature=config.temperature,
                system_prompt=config.system_prompt,
                order_index=config.order_index
            )
            new_conversation.model_configs.append(new_config)
        
        db.session.add(new_conversation)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'new_conversation_id': new_id,
            'message': 'Conversation duplicated successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation and all associated data"""
    try:
        from database.session import db
        
        conversation = db.session.get(Conversation, conversation_id)
        if not conversation:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        # SQLAlchemy will handle cascading deletes for messages and model_configs
        # if configured in the models (which should be set up)
        db.session.delete(conversation)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Conversation deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversations', methods=['GET'])
def list_conversations():
    """List all conversations"""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    conversations = conversation_manager.list_conversations(limit=limit, offset=offset)
    
    return jsonify({
        'status': 'success',
        'conversations': conversations,
        'count': len(conversations)
    })


@app.route('/api/health/providers', methods=['POST'])
def check_providers_health():
    """Check health status of AI providers"""
    try:
        api_keys = request.json.get('api_keys', {})
        results = {}
        
        for provider_name, api_key in api_keys.items():
            if not api_key:
                results[provider_name] = {
                    'status': 'not_configured',
                    'message': 'API key not provided'
                }
                continue
            
            try:
                # Quick validation check
                if provider_name == 'openai':
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key, timeout=5.0)
                    # Quick models list call
                    client.models.list()
                    results[provider_name] = {
                        'status': 'healthy',
                        'message': 'API key is valid'
                    }
                elif provider_name == 'anthropic':
                    import anthropic
                    client = anthropic.Anthropic(api_key=api_key)
                    # Note: Anthropic doesn't have a quick validation endpoint
                    # We just check if the client can be created
                    results[provider_name] = {
                        'status': 'unknown',
                        'message': 'API key format accepted (validation requires API call)'
                    }
                elif provider_name == 'google':
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    results[provider_name] = {
                        'status': 'healthy',
                        'message': 'API key configured'
                    }
                elif provider_name == 'cohere':
                    import cohere
                    client = cohere.Client(api_key=api_key)
                    results[provider_name] = {
                        'status': 'healthy',
                        'message': 'API key configured'
                    }
                elif provider_name == 'ollama':
                    import requests
                    try:
                        response = requests.get('http://localhost:11434/api/tags', timeout=2)
                        if response.status_code == 200:
                            results[provider_name] = {
                                'status': 'healthy',
                                'message': 'Ollama is running',
                                'models': [m['name'] for m in response.json().get('models', [])]
                            }
                        else:
                            results[provider_name] = {
                                'status': 'unhealthy',
                                'message': 'Ollama responded with error'
                            }
                    except Exception:
                        results[provider_name] = {
                            'status': 'unhealthy',
                            'message': 'Ollama is not running'
                        }
                else:
                    results[provider_name] = {
                        'status': 'unknown',
                        'message': 'Provider not supported for health check'
                    }
                    
            except Exception as e:
                results[provider_name] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        return jsonify({
            'status': 'success',
            'providers': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    try:
        from utils.cache import get_cache
        cache = get_cache()
        stats = cache.get_stats()
        
        return jsonify({
            'status': 'success',
            'cache': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the response cache"""
    try:
        from utils.cache import get_cache
        cache = get_cache()
        cache.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/conversation/<conversation_id>/export/text', methods=['GET'])
def export_conversation_text(conversation_id):
    """Export conversation to plain text format"""
    try:
        conv = Conversation.query.get(conversation_id)
        if not conv:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        text = f"{conv.display_title or 'Conversation'}\n"
        text += f"Created: {conv.created_at}\n"
        text += "=" * 80 + "\n\n"
        
        for msg in conv.messages:
            role = msg.role.upper()
            model = f" ({msg.model_name})" if msg.model_name else ""
            text += f"{role}{model}:\n"
            text += f"{msg.content}\n"
            if msg.tokens_used:
                text += f"[Tokens: {msg.tokens_used}]\n"
            text += "\n" + "-" * 80 + "\n\n"
        
        text += f"\nTotal Tokens: {conv.total_tokens}\n"
        text += f"Total Cost: ${conv.total_cost:.4f}\n"
        
        return Response(
            text,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename=conversation_{conversation_id}.txt'
            }
        )
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # Ensure directories exist
    Config.init_app(app)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)