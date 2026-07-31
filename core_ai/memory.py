import json
def build_messages(session):
    messages = []

    for msg in session.messages.all().order_by("created_at"):
        if msg.role not in ["user", "assistant"]:
            continue

        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    return messages