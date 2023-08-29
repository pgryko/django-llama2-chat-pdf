# Create your views here.
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chat.services import get_replicate_stream


# Existing imports and views
@login_required
def chat_page(request, room_id):
    context = {"room_id": room_id}
    return render(request, "chat_and_upload.html", context)


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
