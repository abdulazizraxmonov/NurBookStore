from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Message
from .forms import MessageForm, RoomForm

@login_required
def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'chat/room_list.html', {'rooms': rooms})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Message
from .forms import MessageForm
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def room_chat(request, room_id):
    room = Room.objects.get(id=room_id)
    messages = Message.objects.filter(room=room).order_by('-id') 
    form = MessageForm()
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.room = room
            message.save()
            return redirect('room_chat', room_id=room_id)
    
    return render(request, 'chat/room_chat.html', {'room': room, 'messages': messages, 'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Message
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User


@login_required
def reply_message(request, room_id, message_id):
    room = get_object_or_404(Room, id=room_id)  # Assuming you have a Room model
    if request.method == 'POST':
        message = get_object_or_404(Message, pk=message_id)
        content = request.POST.get('content')
        replied_to_user_id = request.POST.get('replied_to_user_id')

        if replied_to_user_id:
            replied_to_user = get_object_or_404(User, pk=replied_to_user_id)
            # Assuming Message model has user, content, replied_to, and room_id fields
            Message.objects.create(user=request.user, content=content, replied_to=replied_to_user, room_id=room.id)
            messages.success(request, 'Message sent successfully.')
            return redirect('room_detail', room_id=room_id)
        else:
            messages.error(request, 'Error: Could not send message.')

    return redirect('room_detail', room_id=room_id)

from django.shortcuts import get_object_or_404, render
from .models import Room  # Adjust import as per your actual model

def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    # Add any additional context or processing logic here
    return render(request, 'room_detail.html', {'room': room})

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            return redirect('room_chat', room_id=room.id)
    else:
        form = RoomForm()
    return render(request, 'chat/create_room.html', {'form': form})
