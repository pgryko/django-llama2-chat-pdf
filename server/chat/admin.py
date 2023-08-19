# Register your models here.
from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from chat.models import ChromaDBCollection
from chat.singleton import ChromaDBSingleton


@admin.register(ChromaDBCollection)
class ChromaDBCollectionAdmin(admin.ModelAdmin):
    list_display = ("uuid",)

    def get_queryset(self, request):
        # Return a dummy QuerySet for the admin interface
        return ChromaDBCollection.objects.none()

    def changelist_view(self, request, extra_context=None):
        client = ChromaDBSingleton().get_client()
        collections = client.peek()  # Get the first 10 items
        extra_context = extra_context or {}
        extra_context["collections"] = collections
        return super().changelist_view(request, extra_context=extra_context)

    def count(self, obj):
        client = ChromaDBSingleton().get_client()
        return client.get_collection(name=obj.name).count()

    count.short_description = "Count"

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
