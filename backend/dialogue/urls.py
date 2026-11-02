from django.urls import path

from .views import DialogueMessageView, HealthView

app_name = 'dialogue'

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('dialogue/message/', DialogueMessageView.as_view(), name='message'),
]
