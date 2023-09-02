# Create your views here.
import uuid
from django.db.models import Count
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from chat.models import Conversation
from chat.services import get_replicate_stream


# Existing imports and views
@login_required
def chat_page(request, room_uuid):
    context = {"room_uuid": room_uuid}
    return render(request, "chat/chat_and_upload.html", context)


@login_required
def chatroom_delete(request, chatroom_uuid):
    try:
        chatroom = Conversation.objects.get(uuid=chatroom_uuid, user=request.user)
        chatroom.delete()
    except Conversation.DoesNotExist:
        pass  # Optionally, you can handle this case as needed.
    return redirect("chatroom_list")


@login_required
def chatroom_list(request):
    user = request.user
    sort_by = request.GET.get("sort_by", "-updated_at")

    conversations = (
        Conversation.objects.filter(user=user)
        .annotate(message_count=Count("messages"))
        .order_by(sort_by)
    )

    is_sorted_by_newest = True if sort_by == "-updated_at" else False

    if request.method == "POST":
        Conversation.objects.create(user=request.user, collection=uuid.uuid4())
        return redirect("chatroom_list")

    return render(
        request,
        "chat/chatroom_list.html",
        {
            "conversations": conversations,
            "sort_by": sort_by,
            "is_sorted_by_newest": is_sorted_by_newest,
        },
    )


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
