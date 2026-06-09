import json

def build_messages(session):
    messages = []

    for msg in session.messages.all():

        if msg.role not in ["user", "assistant"]:
            continue

        try:
            messages.append({
                "role": msg.role,
                "content": json.loads(msg.content)
                if msg.role == "assistant" else msg.content
            })
        except:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

    return messages