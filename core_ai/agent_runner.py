import json
import anthropic

from django.conf import settings

from chat.models import Message, Session
from tools.registry import get_tool_schemas_for, call_tool
from core_ai.memory import build_messages


def run_agent(agent, session: Session, user_message: str):

    # Save user message
    Message.objects.create(
        session=session,
        role="user",
        content=user_message
    )

    client = anthropic.Anthropic(
        api_key=settings.ANTHROPIC_API_KEY
    )

    tool_names = list(
        agent.tools.values_list("name", flat=True)
    )

    tools = get_tool_schemas_for(tool_names)

    messages = build_messages(session)

    print(f"--- Calling Claude (Model: {agent.model}) ---")

    response = client.messages.create(
        model=agent.model,
        max_tokens=4096,
        system=agent.system_prompt.strip(),
        messages=messages,
        tools=tools,
    )

    print("Stop Reason:", response.stop_reason)

    # Normal Claude response
    if response.stop_reason == "end_turn":

        text_content = ""

        for block in response.content:
            if block.type == "text":
                text_content += block.text

        Message.objects.create(
            session=session,
            role="assistant",
            content=text_content
        )

        return text_content

    # Tool call
    elif response.stop_reason == "tool_use":

        for block in response.content:

            if block.type != "tool_use":
                continue

            print("=" * 80)
            print("TOOL NAME:", block.name)
            print("TOOL INPUT:", block.input)
            print("=" * 80)

            result = call_tool(
                block.name,
                block.input
            )

            print("=" * 80)
            print("TOOL RESULT:")
            print(result)
            print("=" * 80)

            reply = json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            )

            Message.objects.create(
                session=session,
                role="assistant",
                content=reply
            )

            return reply

        return "Tool executed but no result returned."

    else:
        return f"Unexpected stop reason: {response.stop_reason}"