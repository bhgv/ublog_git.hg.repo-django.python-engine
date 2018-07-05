from my_django.views.generic.base import View, TemplateView, RedirectView
from my_django.views.generic.dates import (ArchiveIndexView, YearArchiveView, MonthArchiveView,
                                     WeekArchiveView, DayArchiveView, TodayArchiveView,
                                     DateDetailView)
from my_django.views.generic.detail import DetailView
from my_django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from my_django.views.generic.list import ListView


class GenericViewError(Exception):
    """A problem in a generic view."""
    pass
