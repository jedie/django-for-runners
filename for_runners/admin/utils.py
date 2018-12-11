"""
    created 19.07.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic import TemplateView


class ChangelistViewMixin:

    def dispatch(self, request, change_list, *args, **kwargs):
        self.change_list = change_list
        return super().dispatch(request, *args, **kwargs)


class BaseChangelistView(ChangelistViewMixin, TemplateView):
    """
    Baseclass for chnagelist views without forms.
    """
    pass


class BaseFormChangelistView(ChangelistViewMixin, generic.FormView):
    """
    Baseclass for changelist views with forms.
    """
    form_class = None

    def form_valid(self, form):
        # Don't redirect, if form is valid ;)
        return self.render_to_response(self.get_context_data(form=form))


# def export_as_json(modeladmin, request, queryset):
#     response = HttpResponse(content_type="application/json")
#     serializers.serialize("json", queryset, stream=response)
#     return response
#
#
# def export_selected_objects(modeladmin, request, queryset):
#     selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
#     ct = ContentType.objects.get_for_model(queryset.model)
#     return HttpResponseRedirect("/export/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))

def export_as_json(modeladmin, request, queryset):
    """
    from:
    http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages
    """
    # response = HttpResponse(content_type="text/javascript")
    response = HttpResponse(content_type="application/json")
    serializers.serialize("json", queryset, stream=response, indent=4)
    return response
