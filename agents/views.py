import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Agent, Conversation
from .services import ChatService


# ─────────────────────────────────────────────
# Home
# ─────────────────────────────────────────────
def index(request):
    agents = Agent.objects.all()

    if agents.exists():
        return redirect("chat", agent_slug=agents.first().slug)

    return render(
        request,
        "index.html",
        {
            "agents": agents,
        },
    )


# ─────────────────────────────────────────────
# Send Message
# ─────────────────────────────────────────────
@require_POST
def send_message(request, agent_slug):

    agent = get_object_or_404(
        Agent,
        slug=agent_slug,
    )

    service = ChatService()

    try:
        data = json.loads(request.body)

        user_text = data.get(
            "message",
            "",
        ).strip()

        conv_id = (
            data.get("conversation_id")
            or request.session.get(
                f"conv_{agent_slug}"
            )
        )

        if not user_text:
            return JsonResponse(
                {
                    "error":
                    "Message cannot be empty."
                },
                status=400,
            )

        conversation = (
            service.get_or_create_conversation(
                agent,
                conv_id,
            )
        )

        request.session[
            f"conv_{agent_slug}"
        ] = conversation.id

        reply = service.chat(
            conversation,
            user_text,
        )

        return JsonResponse(
            {
                "reply": reply,
                "conversation_id": conversation.id,
                "conversation_title":
                    conversation.title or "",
            }
        )

    except Exception as exc:
        return JsonResponse(
            {
                "error": str(exc)
            },
            status=500,
        )


# ─────────────────────────────────────────────
# Conversation History JSON
# ─────────────────────────────────────────────
def conversation_list_json(
    request,
    agent_slug,
):
    agent = get_object_or_404(
        Agent,
        slug=agent_slug,
    )

    conversations = (
        agent.conversations
        .order_by("-created_at")
    )

    data = []

    for conversation in conversations:

        data.append(
            {
                "id": conversation.id,
                "title":
                    conversation.title
                    or f"Chat {conversation.id}",
                "created_at":
                    conversation.created_at.strftime(
                        "%d %b %Y %H:%M"
                    ),
                "message_count":
                    conversation.messages.count(),
            }
        )

    return JsonResponse(
        {
            "conversations": data
        }
    )


# ─────────────────────────────────────────────
# New Chat
# ─────────────────────────────────────────────
def new_conversation(
    request,
    agent_slug,
):
    session_key = (
        f"conv_{agent_slug}"
    )

    if session_key in request.session:
        del request.session[
            session_key
        ]

    return JsonResponse(
        {
            "success": True,
        }
    )


# ─────────────────────────────────────────────
# Delete Chat
# ─────────────────────────────────────────────
@require_POST
def delete_conversation(
    request,
    agent_slug,
    conversation_id,
):

    agent = get_object_or_404(
        Agent,
        slug=agent_slug,
    )

    conversation = (
        get_object_or_404(
            Conversation,
            id=conversation_id,
            agent=agent,
        )
    )

    conversation.delete()

    session_key = (
        f"conv_{agent_slug}"
    )

    if (
        request.session.get(
            session_key
        )
        == conversation_id
    ):
        del request.session[
            session_key
        ]

    return JsonResponse(
        {
            "success": True,
            "status": "deleted",
        }
    )