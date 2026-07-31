from django.urls import path
from . import views

urlpatterns = [
    # path("<str:agent_slug>/", views.chat_view, name="chat_view"),
    path("<slug:agent_slug>/chat/<int:session_id>/", views.chat_view, name="chat_with_session"),
    path("<slug:agent_slug>/chat/", views.chat_view, name="chat_new"),
    path("send/<str:agent_slug>/", views.send_message, name="send_message"),
]