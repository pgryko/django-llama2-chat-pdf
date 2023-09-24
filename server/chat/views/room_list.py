import uuid

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django import forms
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from ninja.errors import ValidationError
from pydantic import UUID4

from chat import services
from chat.models import Conversation, DocumentFile
from chat.services import (
    delete_document,
    delete_conversation,
)


# @login_required
# async def chatroom_delete(request, chatroom_uuid):
#     if request.method == "POST":
#         try:
#             conversation = Conversation.objects.aget(
#                 uuid=chatroom_uuid, user=request.user
#             )
#             await async_delete_conversation(conversation=conversation)
#         except Conversation.DoesNotExist:
#             pass  # Optionally, you can handle this case as needed.
#         # Trigger a reload of the current page
#         return redirect(
#             request.META.get("HTTP_REFERER", "redirect_if_referer_not_found")
#         )


@login_required
def chatroom_delete(request, chatroom_uuid):
    if request.method == "POST":
        try:
            conversation = Conversation.objects.get(
                uuid=chatroom_uuid, user=request.user
            )
            delete_conversation(conversation=conversation)
        except Conversation.DoesNotExist:
            pass  # Optionally, you can handle this case as needed.
        # Trigger a reload of the current page
        return redirect(
            request.META.get("HTTP_REFERER", "redirect_if_referer_not_found")
        )


@login_required
def chatroom_create(request):
    if request.method == "POST":
        Conversation.objects.create(user=request.user, collection=uuid.uuid4())
        return redirect(
            request.META.get("HTTP_REFERER", "redirect_if_referer_not_found")
        )


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

    return render(
        request,
        "chat/chatroom_list.html",
        {
            "conversations": conversations,
            "sort_by": sort_by,
            "is_sorted_by_newest": is_sorted_by_newest,
        },
    )


@login_required
def files_list(request, chatroom_uuid):
    user = request.user
    sort_by = request.GET.get("sort_by", "-updated_at")

    files = DocumentFile.objects.filter(
        conversation__user=user, conversation__uuid=chatroom_uuid
    ).order_by(sort_by)

    is_sorted_by_newest = True if sort_by == "-updated_at" else False

    return render(
        request,
        "chat/chatroom_list.html",
        {
            "files": files,
            "sort_by": sort_by,
            "is_sorted_by_newest": is_sorted_by_newest,
        },
    )


@login_required
def file_delete(request, chatroom_uuid, file_uuid):
    conversation = get_object_or_404(
        Conversation, uuid=chatroom_uuid, user=request.user
    )

    if request.method == "POST":
        file = get_object_or_404(
            DocumentFile, uuid=file_uuid, conversation=conversation
        )

        delete_document(file)

        return redirect(
            request.META.get("HTTP_REFERER", "redirect_if_referer_not_found")
        )

    return HttpResponseNotAllowed(["POST"])


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = DocumentFile
        fields = ["file"]


@login_required
def upload_file(request, chatroom_uuid: UUID4):
    room = get_object_or_404(Conversation, uuid=chatroom_uuid)

    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                services.add_unique_document(file=form.files["file"], conversation=room)
            except ValidationError as e:
                return JsonResponse({"detail": str(e.errors)}, status=400)

    return redirect(request.META.get("HTTP_REFERER", "redirect_if_referer_not_found"))
