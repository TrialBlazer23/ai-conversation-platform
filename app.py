"""
Enhanced Flask application with streaming, database persistence, and advanced features
"""
from flask import Flask, render_template, request, jsonify, session, Response, stream_with_context
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path

from database import init_db, db
from models.conversation import ConversationManager
from models.ai_provider import AIProviderFactory
from utils.token_counter import TokenCounter
from utils.helpers import calculate_cost
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize database
init_db(app)

# Initialize conversation manager
conversation_manager = ConversationManager()


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
        
        return jsonify({
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
        })
        
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
                yield f"data: {json.dumps({'type': 'content', 'chunk': chunk})}\n\n"
            
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


@app.route('/api/conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    success = conversation_manager.delete_conversation(conversation_id)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Conversation deleted'})
    else:
        return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404


if __name__ == '__main__':
    # Ensure directories exist
    Config.init_app(app)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)