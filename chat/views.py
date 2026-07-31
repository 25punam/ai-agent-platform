# import json

# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404, render
# from django.views.decorators.http import require_POST

# from agents.models import Agent
# from chat.models import Session, Message
# from agents.services import ChatService

# def chat_view(request, agent_slug):
#     agent = get_object_or_404(Agent, slug=agent_slug)

#     session = Session.objects.filter(agent=agent).first()

#     if not session:
#         session = Session.objects.create(agent=agent)

#     messages = session.messages.order_by("created_at")

#     return render(request, "index.html", {
#         "agent": agent,
#         "session": session,
#         "messages": messages
#     })

# @require_POST
# def send_message(request, agent_slug):
#     print("!!!! VIEWS.PY TRIGGERED FOR SEND MESSAGE !!!!")
#     agent = get_object_or_404(Agent, slug=agent_slug)

#     data = json.loads(request.body)
#     user_text = data.get("message", "").strip()

#     if not user_text:
#         return JsonResponse({"error": "Message required"}, status=400)

#     session = Session.objects.filter(agent=agent).first()

#     if not session:
#         session = Session.objects.create(agent=agent)

#     service = ChatService()

#     reply = service.chat(session, user_text)

#     return JsonResponse({
#         "reply": reply,
#         "session_id": session.id
#     })

# def session_list(request, agent_slug):
#     agent = get_object_or_404(Agent, slug=agent_slug)

#     sessions = Session.objects.filter(agent=agent).order_by("-created_at")

#     data = [
#         {
#             "id": s.id,
#             "title": s.title or f"Chat {s.id}"
#         }
#         for s in sessions
#     ]

#     return JsonResponse({"sessions": data})


import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from agents.models import Agent
from chat.models import Session, Message
from agents.services import ChatService


def chat_view(request, agent_slug, session_id=None):
    agent = get_object_or_404(Agent, slug=agent_slug)

    if session_id:
        session = get_object_or_404(Session, id=session_id, agent=agent)
    else:
        # naya session sirf tab banao jab koi empty session pehle se na ho
        session = Session.objects.filter(
            agent=agent, messages__isnull=True
        ).first()
        if not session:
            session = Session.objects.create(agent=agent)

    messages = session.messages.order_by("created_at")

    return render(request, "index.html", {
        "agent": agent,
        "session": session,
        "messages": messages
    })


@require_POST
def send_message(request, agent_slug):
    agent = get_object_or_404(Agent, slug=agent_slug)

    data = json.loads(request.body)
    user_text = data.get("message", "").strip()
    session_id = data.get("session_id")

    if not user_text:
        return JsonResponse({"error": "Message required"}, status=400)

    if session_id:
        session = get_object_or_404(Session, id=session_id, agent=agent)
    else:
        session = Session.objects.create(agent=agent)

    # pehla message hi session ka title ban jaye (jaise ChatGPT karta hai)
    if not session.title:
        session.title = user_text[:50]
        session.save(update_fields=["title"])

    service = ChatService()
    reply = service.chat(session, user_text)

    return JsonResponse({
        "reply": reply,
        "session_id": session.id
    })


def session_list(request, agent_slug):
    agent = get_object_or_404(Agent, slug=agent_slug)

    sessions = Session.objects.filter(agent=agent).order_by("-created_at")

    data = [
        {
            "id": s.id,
            "title": s.title or "New Chat"
        }
        for s in sessions
    ]

    return JsonResponse({"sessions": data})