# Create your views here.
from django.db.models import Count
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

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
        return redirect(reverse("serve_file", kwargs={"file_uuid": file_uuid}))
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
        return redirect(reverse("serve_file", kwargs={"file_uuid": file_uuid}))
    else:
        return HttpResponse("Unsupported file type.")


# Don't use this on production, use S3 type bucket storage with proper user specific permissions
@login_required
def serve_file(request, file_uuid):
    user_file = get_object_or_404(
        DocumentFile, uuid=file_uuid, conversation__user=request.user
    )

    return FileResponse(user_file.file)
