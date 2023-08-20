from django.http import Http404
from django.shortcuts import _get_queryset


async def aget_object_or_404(klass, *args, **kwargs):
    """
    Use aget() to return an object, or raise an Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the aget() query.

    Like with QuerySet.aget(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, "aget"):
        klass__name = (
            klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to aget_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return await queryset.aget(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404(
            "No %s matches the given query." % queryset.model._meta.object_name
        )
