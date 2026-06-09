from django.urls import path
from . import views

urlpatterns = [
    path("<str:agent_slug>/", views.chat_view, name="chat_view"),
    path("send/<str:agent_slug>/", views.send_message, name="send_message"),
]