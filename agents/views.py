import json
import traceback
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from chat.models import Message, Session
from .models import Agent
from .services import ChatService

logger = logging.getLogger(__name__)


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
        print("!!!! agents/views.py send_message TRIGGERED !!!!")
        print("AGENT_SLUG=", agent_slug)
        print("RAW_BODY=", request.body[:500])
        data = json.loads(request.body)


        user_text = data.get(
            "message",
            "",
        ).strip()

        session_id = (
            data.get("session_id")
            or data.get("conversation_id")
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

        session = (
            service.get_or_create_session(
                agent,
                session_id,
            )
        )

        request.session[
            f"conv_{agent_slug}"
        ] = session.id

        service.set_title_from_message(
            session,
            user_text,
        )

        reply = service.chat(
            session,
            user_text,
        )

        return JsonResponse(
            {
                "reply": reply,
                "__backend_marker": "agents/views.py",
                "session_id": session.id,
                "conversation_id": session.id,
                "session_title":
                    session.title or f"Chat {session.id}",
                "conversation_title":
                    session.title or f"Chat {session.id}",
            }
        )

    except Exception as exc:
        tb_str = traceback.format_exc()
        print("=" * 80)
        print("EXCEPTION IN agents/views.py send_message")
        print("=" * 80)
        print(tb_str)
        print("=" * 80)
        logger.error(f"Exception in send_message: {tb_str}")
        
        return JsonResponse(
            {
                "error": str(exc),
                "traceback": tb_str,
                "exception_type": type(exc).__name__
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

    sessions = (
        agent.sessions
        .order_by("-created_at")
    )

    data = []

    service = ChatService()

    for session in sessions:
        data.append(
            {
                "id": session.id,
                "title":
                    service.get_session_title(session),
                "created_at":
                    session.created_at.strftime(
                        "%d %b %Y %H:%M"
                    ),
                "message_count": session.messages.count(),
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

    session = (
        get_object_or_404(
            Session,
            id=conversation_id,
            agent=agent,
        )
    )

    session.delete()

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

def chat_view(
    request,
    agent_slug,
    conversation_id=None,
):
    agent = get_object_or_404(
        Agent,
        slug=agent_slug,
    )

    session = None
    messages = []

    if conversation_id:
        session = get_object_or_404(
            Session,
            id=conversation_id,
            agent=agent,
        )
        messages = session.messages.order_by("created_at")

    return render(
        request,
        "index.html",
        {
            "agent": agent,
            "conversation": session,
            "messages": messages,
        },
    )