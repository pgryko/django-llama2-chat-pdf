# Create your views here.
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from chat.models import Conversation


@login_required
def chat_page(request, room_uuid):
    user = request.user
    sort_by = request.GET.get("sort_by", "-updated_at")

    conversations = (
        Conversation.objects.filter(user=user)
        .annotate(message_count=Count("messages"))
        .order_by(sort_by)
    )
    context = {"room_uuid": room_uuid, "conversations": conversations}

    if conversations.filter(uuid=room_uuid).exists() is False:
        return redirect("chatroom_list")

    return render(request, "chat/chat_and_upload.html", context)
