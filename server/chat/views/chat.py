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


# async def chat_streaming(request, room_id):
#
#     chat_input = request.GET.get('chat_input', '')
#     response = StreamingHttpResponse(
#         streaming_content=get_replicate_stream(chat_input),
#         content_type="text/event-stream",
#     )
#     response["Cache-Control"] = "no-cache"
#     response["Transfer-Encoding"] = "chunked"
#     return response
