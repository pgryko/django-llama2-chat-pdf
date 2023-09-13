# Register your models here.
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect

from chat.models import ChromaDBCollection, Conversation, Message
from chat.singleton import ChromaDBSingleton


@admin.register(ChromaDBCollection)
class ChromaDBCollectionAdmin(admin.ModelAdmin):
    list_display = ("chroma_id", "name", "count", "peek")

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
        ChromaDBCollection.objects.all().delete()

        instances = [
            ChromaDBCollection(
                chroma_id=col.id, name=col.name, count=col.count(), peek=col.peek()
            )
            for col in collections
        ]

        ChromaDBCollection.objects.bulk_create(instances)

        return ChromaDBCollection.objects.all()

    # def changelist_view(self, request, extra_context=None):
    #     client = ChromaDBSingleton().get_client()
    #     collections = client.list_collections()
    #     # collections = client.peek()  # Get the first 10 items
    #     extra_context = extra_context or {}
    #     extra_context["collections"] = collections
    #     return super().changelist_view(request, extra_context=extra_context)
    #
    # def count(self, obj):
    #     client = ChromaDBSingleton().get_client()
    #     return client.get_collection(name=obj.name).count()
    #
    # count.short_description = "Count"

    def save_model(self, request, obj, form, change):
        client = ChromaDBSingleton().get_client()
        if change:
            collection = client.get_collection(name=obj.name)
            collection.modify(name=form.cleaned_data["name"])
        else:
            client.create_collection(name=form.cleaned_data["name"])

    def delete_model(self, request, obj):
        client = ChromaDBSingleton().get_client()
        client.delete_collection(name=obj.name)

    def response_add(self, request, obj, post_url_continue=None):
        messages.success(request, "Collection successfully created.")
        return HttpResponseRedirect(request.path)

    def response_change(self, request, obj):
        messages.success(request, "Collection successfully modified.")
        return HttpResponseRedirect(request.path)

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
