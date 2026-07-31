import os
import json
import anthropic
from decimal import Decimal
from chat.models import Message, Session
from core_ai.agent_runner import run_agent
from ecommerce.models import Order


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# ─────────────────────────────────────────────
# TOOL DEFINITIONS
# ─────────────────────────────────────────────
TOOLS = [
    {
        "name": "find_order",
        "description": "Find an order by ID and return details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "confirm_cancel_order",
        "description": "Cancel an order after confirmation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "list_orders",
        "description": "List all orders. Pass an optional status filter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter by order status e.g. 'cancelled', 'delivered', 'pending'"
                }
            },
            "required": []
        }
    }
]


# ─────────────────────────────────────────────
# TOOL EXECUTION LAYER
# ─────────────────────────────────────────────
def execute_tool(tool_name: str, tool_input: dict) -> dict:

    # ── FIND ORDER ──────────────────────────────
    if tool_name == "find_order":
        try:
            order = Order.objects.get(order_id=tool_input["order_id"])
            return {
                "success": True,
                "order_id": order.order_id,
                "status": order.status,
                "items": [
                    {
                        "product": item.product.name,
                        "quantity": item.quantity,
                        "price": float(item.price),
                    }
                    for item in order.items.all()
                ],
                "total": float(order.total_amount),
            }
        except Order.DoesNotExist:
            return {"success": False, "message": "Order not found."}

    # ── CANCEL ORDER ────────────────────────────
    elif tool_name == "confirm_cancel_order":
        try:
            order = Order.objects.get(order_id=tool_input["order_id"])
            if order.status in ["delivered", "cancelled"]:
                return {
                    "success": False,
                    "message": f"Cannot cancel. Order already {order.status}."
                }
            order.status = "cancelled"
            order.save()
            return {
                "success": True,
                "message": f"Order {order.order_id} cancelled successfully."
            }
        except Order.DoesNotExist:
            return {"success": False, "message": "Order not found."}

    # ── LIST ORDERS ─────────────────────────────
    elif tool_name == "list_orders":
        # By default, hide cancelled orders unless the caller explicitly
        # requests them. This prevents deleted/cancelled orders from
        # appearing in "Show me all orders" unless desired.
        include_cancelled = bool(tool_input.get("include_cancelled"))

        qs = Order.objects.all()

        # Optional status filter (explicit override)
        status_filter = tool_input.get("status")
        if status_filter:
            qs = qs.filter(status__iexact=status_filter)
        else:
            if not include_cancelled:
                qs = qs.exclude(status__iexact="cancelled")

        # Include customer name to improve frontend rendering
        orders = list(qs.values("order_id", "status", "total_amount", "customer__name"))

        # Decimal → float safety fix
        for o in orders:
            if isinstance(o.get("total_amount"), Decimal):
                o["total_amount"] = float(o["total_amount"])

        return {"success": True, "orders": orders}

    # ── UNKNOWN TOOL ────────────────────────────
    return {"success": False, "message": "Unknown tool requested."}


# ─────────────────────────────────────────────
# CHAT SERVICE
# ─────────────────────────────────────────────
class ChatService:

    def _generate_title(self, user_text):
        title = user_text.strip().split("\n", 1)[0]
        if len(title) > 50:
            title = title[:50].rsplit(" ", 1)[0]
        return title.strip() or f"Chat {user_text[:50].strip()}"

    def _ensure_unique_title(self, agent, title, exclude_session_id=None):
        # Avoid ugly numeric suffixes like "(2)" for duplicate titles.
        # If two conversations begin with the same first user message, show the same meaningful title.
        return title

    def get_or_create_session(
        self,
        agent,
        session_id=None,
    ):
        if session_id:
            try:
                return Session.objects.get(
                    id=session_id,
                    agent=agent,
                )
            except Session.DoesNotExist:
                pass

        return Session.objects.create(
            agent=agent,
        )

    def set_title_from_message(self, session, user_text):
        if session.title and session.title != "New Chat":
            return

        title = self._generate_title(user_text)
        title = self._ensure_unique_title(
            session.agent,
            title,
            exclude_session_id=session.id,
        )
        session.title = title
        session.save(update_fields=["title"])

    def get_session_title(self, session):
        first_user_message = session.messages.filter(role="user").order_by("created_at").first()
        if first_user_message and first_user_message.content.strip():
            return self._generate_title(first_user_message.content)

        if session.title and session.title != "New Chat":
            return session.title

        return f"Chat {session.id}"

    def chat(self, session, user_text):
        return run_agent(
            session.agent,
            session,
            user_text,
        )
    


