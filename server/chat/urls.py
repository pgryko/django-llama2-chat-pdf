from django.urls import path
from . import views

urlpatterns = [
    path("rooms/", views.chatroom_list, name="chatroom_list"),
    path("room/<uuid:room_id>/", views.chat_page, name="chat_room"),
    path(
        "room/delete/<uuid:chatroom_id>/", views.chatroom_delete, name="delete_chatroom"
    )
    # path('streaming/<uuid:room_id>/', views.chat_streaming, name='chat_streaming'),
    # ... (Your other URL patterns for chat and upload, updated to handle room UUIDs)
]
