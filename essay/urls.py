# essays/urls.py

from django.urls import path
from .views import submit_essay, essay_history


urlpatterns = [
    path('', submit_essay, name='submit_essay'),
    path('history/', essay_history, name='history_essay'),
]




