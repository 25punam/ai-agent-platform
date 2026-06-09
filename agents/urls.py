from django.urls import path
from . import views

urlpatterns = [
    # Home — agent list
    path("", views.index, name="index"),

    # Conversations list for an agent
    path(
        "agent/<slug:agent_slug>/history/",
        views.conversation_list_json,
        name="conversation_list",
    ),

    # Chat — latest / session conversation
    path("chat/<slug:agent_slug>/", views.chat_view, name="chat"),

    # Chat — specific conversation
    path(
        "chat/<slug:agent_slug>/<int:conversation_id>/",
        views.chat_view,
        name="chat_detail",
    ),

    # AJAX send message
    path(
        "chat/<slug:agent_slug>/send/",
        views.send_message,
        name="send_message",
    ),

    # Start new conversation
    path(
        "chat/<slug:agent_slug>/new/",
        views.new_conversation,
        name="new_conversation",
    ),

    # Delete a conversation
    path(
        "chat/<slug:agent_slug>/delete/<int:conversation_id>/",
        views.delete_conversation,
        name="delete_conversation",
    ),
]