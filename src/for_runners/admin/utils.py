"""
    created 19.07.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

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
