from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import Conversation, Message
from .services import get_ai_response

def home(request):
    conversations = Conversation.objects.all().order_by('-created_at')
    return render(request, 'chatbot/home.html', {'conversations': conversations})

def conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = conversation.messages.all().order_by('timestamp')
    conversations = Conversation.objects.all().order_by('-created_at')
    return render(request, 'chatbot/conversation.html', {
        'conversation': conversation,
        'messages': messages,
        'conversations': conversations
    })

def new_conversation(request):
    conversation = Conversation.objects.create(title="New Conversation")
    return redirect('conversation', conversation_id=conversation.id)

@csrf_exempt
@require_POST
def send_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    data = json.loads(request.body)
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    # Save user message
    Message.objects.create(
        conversation=conversation,
        role='user',
        content=user_message
    )
    
    # Get conversation history
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation.messages.all().order_by('timestamp')
    ]
    
    # Get AI response
    ai_response = get_ai_response(messages)
    
    # Save AI response
    Message.objects.create(
        conversation=conversation,
        role='assistant',
        content=ai_response
    )
    
    # Update conversation title if it's the first message
    if conversation.title == "New Conversation" and len(messages) <= 2:
        conversation.title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        conversation.save()
    
    return JsonResponse({
        'response': ai_response
    })