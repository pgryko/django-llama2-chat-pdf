# Register your models here.
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect

from chat.models import ChromaDBCollection, Conversation, Message
from chat.singleton import ChromaDBSingleton


@admin.register(ChromaDBCollection)
class ChromaDBCollectionAdmin(admin.ModelAdmin):
    list_display = ("chroma_id", "name", "count")

    readonly_fields = [f.name for f in ChromaDBCollection._meta.get_fields()]

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing, but the change view will still be accessible
        return (
            False if obj else True
        )  # This will allow adding new objects if needed, but won't allow editing existing ones

    def has_delete_permission(self, request, obj=None):
        # Return True to allow deletion. Adjust as necessary.
        return True

    @transaction.atomic
    def get_queryset(self, request):
        # fake_qs = FakeQuerySet(model=ChromaDBCollection, using="default")
        #
        # tmp_list = list(fake_qs)  # Force the queryset to be evaluated
        # return fake_qs
        client = ChromaDBSingleton().get_client()
        collections = client.list_collections()
        # collections are a list of dicts containing
        # {'name': '66af9efe-1e99-40d2-9799-c1cf99d9f969',
        #  'id': UUID('02fa98e2-806c-4aa9-9913-b45cbd96e413'),
        #  'metadata': None}
        # Fetch existing rows based on ChromaDB IDs
        existing_ids = {col.id: col for col in collections}
        existing_rows = ChromaDBCollection.objects.filter(
            chroma_id__in=existing_ids.keys()
        )

        to_update = []
        to_create = []

        # Check for updates or new rows
        for row in existing_rows:
            collection = existing_ids.pop(
                row.chroma_id
            )  # Remove from the dict to keep track of new vs. existing
            row.name = collection.name
            row.count = collection.count()
            row.peek = collection.peek()
            to_update.append(row)

        # Any remaining collections in existing_ids dict are new and need to be created
        for collection in existing_ids.values():
            new_row = ChromaDBCollection(
                chroma_id=collection.id,
                name=collection.name,
                count=collection.count(),
                peek=collection.peek(),
            )
            to_create.append(new_row)

        # Perform bulk update and bulk create operations
        if to_update:
            ChromaDBCollection.objects.bulk_update(to_update, ["name", "count", "peek"])
        if to_create:
            ChromaDBCollection.objects.bulk_create(to_create)

        # Delete rows that no longer exist in ChromaDB
        ChromaDBCollection.objects.exclude(
            chroma_id__in=[col.id for col in collections]
        ).delete()

        return ChromaDBCollection.objects.all()

    def custom_delete_selected(self, request, queryset):
        # Custom delete logic.
        # Use the queryset to get the list of items selected in the admin
        for obj in queryset:
            # Your custom delete logic here. For example:
            client = ChromaDBSingleton().get_client()
            client.delete_collection(name=obj.name)
            obj.delete()  # Optional: If you want to delete the item from the Django-managed table

        # Provide a success message
        self.message_user(
            request, "Selected collections have been successfully deleted."
        )

    custom_delete_selected.short_description = "Delete selected collections"

    actions = [custom_delete_selected]

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove the default delete_selected action
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def delete_model(self, request, obj):
        client = ChromaDBSingleton().get_client()
        client.delete_collection(name=obj.name)

    def response_delete(self, request, obj_display, obj_id):
        messages.success(request, "Collection successfully deleted.")
        return HttpResponseRedirect(request.path)


class MessageInline(admin.TabularInline):  # or admin.StackedInline if you prefer
    model = Message
    extra = 0  # Number of empty forms to display
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fields = ("message_type", "content", "created_at", "updated_at")
    ordering = ("updated_at",)


class ConversationAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "collection", "created_at", "updated_at")
    search_fields = (
        "user__username",
        "collection",
    )
    list_filter = (
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = [MessageInline]


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "conversation",
        "message_type",
        "content",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "conversation__uuid",
        "message_type",
        "content",
    )
    list_filter = (
        "message_type",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


# Register the admin classes with the models
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
