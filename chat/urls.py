from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.room_list, name='room_list'),
    path('room/<int:room_id>/', views.room_chat, name='room_chat'),
    path('create_room/', views.create_room, name='create_room'),
    path('room/<int:room_id>/reply/<int:message_id>/', views.reply_message, name='reply_message'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),  # Example URL pattern for room_detail
]
