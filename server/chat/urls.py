from django.urls import path
from chat.views import chat as chat_views, room_list as room_list_views

urlpatterns = [
    path("room/<uuid:room_uuid>/", chat_views.chat_page, name="chat_room"),
    path("rooms/", room_list_views.chatroom_list, name="chatroom_list"),
    path(
        "room/delete/<uuid:chatroom_uuid>/",
        room_list_views.chatroom_delete,
        name="chatroom_delete",
    ),
    path("room/create/", room_list_views.chatroom_create, name="chatroom_create"),
    # path('streaming/<uuid:room_id>/', views.chat_streaming, name='chat_streaming'),
    # ... (Your other URL patterns for chat and upload, updated to handle room UUIDs)
]
