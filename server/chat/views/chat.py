# Create your views here.
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from chat.models import Conversation, DocumentFile


@login_required
def chat_page(request, room_uuid):
    user = request.user
    sort_by = request.GET.get("sort_by", "-updated_at")

    conversations = (
        Conversation.objects.filter(user=user)
        .annotate(message_count=Count("messages"))
        .order_by(sort_by)
    )

    files = DocumentFile.objects.filter(
        conversation__user=user, conversation__uuid=room_uuid
    ).order_by(sort_by)

    context = {
        "room_uuid": room_uuid,
        "conversations": conversations,
        "files": files,
    }

    if conversations.filter(uuid=room_uuid).exists() is False:
        return redirect("chatroom_list")

    return render(request, "chat/chat_and_upload.html", context)


@login_required
def file_view(request, room_uuid, file_uuid):
    file_obj = get_object_or_404(DocumentFile, uuid=file_uuid)

    if file_obj.file.url.endswith(".pdf"):
        # For PDFs, redirecting to the file URL is a common practice as most browsers have built-in PDF viewers
        return redirect(file_obj.file.url)
    elif file_obj.file.url.endswith((".txt", ".html")):
        # For text files, you can render the content in a basic view
        with open(file_obj.file.path, "r") as f:
            content = f.read()
        return render(
            request,
            "chat/text_file_view.html",
            {"content": content, "room_uuid": room_uuid},
        )
    elif file_obj.file.url.endswith((".jpg", ".jpeg", ".png", ".gif")):
        # For images, again redirecting to the file URL is common as the browser can display images
        return redirect(file_obj.file.url)
    else:
        return HttpResponse("Unsupported file type.")
