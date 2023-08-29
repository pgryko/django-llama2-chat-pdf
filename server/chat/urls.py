from django.urls import path
from . import views

urlpatterns = [
    path("room/<uuid:room_id>/", views.chat_page, name="chat_room"),
    # path('streaming/<uuid:room_id>/', views.chat_streaming, name='chat_streaming'),
    # ... (Your other URL patterns for chat and upload, updated to handle room UUIDs)
]
