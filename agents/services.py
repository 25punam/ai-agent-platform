import os
import json
import anthropic
from decimal import Decimal
from .models import Conversation, Message
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
        qs = Order.objects.all()

        # Optional status filter
        status_filter = tool_input.get("status")
        if status_filter:
            qs = qs.filter(status__iexact=status_filter)

        orders = list(qs.values("order_id", "status", "total_amount"))

        # Decimal → float safety fix
        for o in orders:
            if isinstance(o.get("total_amount"), Decimal):
                o["total_amount"] = float(o["total_amount"])

        return {"success": True, "orders": orders}

    # ── UNKNOWN TOOL ────────────────────────────
    return {"success": False, "message": "Unknown tool requested."}


# ─────────────────────────────────────────────
# CHAT SERVICE
# ─────────────────────────────────────────────from core_ai.agent_runner import run_agent

class ChatService:

    def chat(self, conversation, user_text):
        return run_agent(
            conversation.agent,
            conversation,
            user_text
        )