import time
from ai_assistant.core_ai.memory import build_messages
import anthropic
from django.conf import settings

from chat.models import Message, Session
from tools.registry import get_tool_schemas_for, call_tool


def run_agent(agent, session: Session, user_message: str):
    Message.objects.create(session=session, role="user", content=user_message)

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    tool_names = list(agent.tools.values_list("name", flat=True))
    tools = get_tool_schemas_for(tool_names)

    messages = build_messages(session)

    start_time = time.monotonic()

    while True:

        response = client.messages.create(
            model=agent.model,
            max_tokens=4096,
            system=agent.system_prompt,
            messages=messages,
            tools=tools if tools else None,
        )

        # CASE 1: FINAL ANSWER
        if response.stop_reason == "end_turn":
            text = next(
                (b.text for b in response.content if b.type == "text"),
                ""
            )

            Message.objects.create(
                session=session,
                role="assistant",
                content=text
            )

            return text

        # CASE 2: TOOL USE
        if response.stop_reason == "tool_use":

            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": b.type,
                        "text": getattr(b, "text", ""),
                        "name": getattr(b, "name", None),
                        "input": getattr(b, "input", None),
                        "id": getattr(b, "id", None),
                    }
                    for b in response.content
                ]
            })

            tool_results = []

            for block in response.content:
                if block.type == "tool_use":

                    result = call_tool(block.name, block.input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })

            continue