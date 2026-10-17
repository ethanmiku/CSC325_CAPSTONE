from django.urls import path
from . import views

urlpatterns = [
    path("clues/", views.get_clues, name="get_clues"),
]