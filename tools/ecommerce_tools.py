# tools/ecommerce_tools.py
from decimal import Decimal
from ecommerce.models import Order
from .registry import register_tool

@register_tool
def list_orders(status: str = None) -> dict:
    """
    List all orders. Pass an optional status filter like 'cancelled', 'delivered', 'pending'.
    """
    # By default, hide cancelled orders unless explicitly requested
    qs = Order.objects.all()
    if status:
        qs = qs.filter(status__iexact=status)
    else:
        qs = qs.exclude(status__iexact="cancelled")

    orders = list(qs.values("order_id", "status", "total_amount", "customer__name"))

    # Decimal to float conversion safety check
    for o in orders:
        if isinstance(o.get("total_amount"), Decimal):
            o["total_amount"] = float(o["total_amount"])

    return {"success": True, "orders": orders}


@register_tool
def find_order(order_id: str) -> dict:
    """
    Find a specific order by its order_id string and return detailed items and status.
    """
    try:
        order = Order.objects.get(order_id=order_id)
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
        return {"success": False, "message": f"Order with ID {order_id} not found."}


@register_tool
def confirm_cancel_order(order_id: str) -> dict:
    """
    Cancel an order using its order_id after confirmation.
    """
    try:
        order = Order.objects.get(order_id=order_id)
        if order.status in ["delivered", "cancelled"]:
            return {
                "success": False,
                "message": f"Cannot cancel. Order is already {order.status}."
            }
        order.status = "cancelled"
        order.save()
        return {
            "success": True,
            "message": f"Order {order.order_id} has been cancelled successfully."
        }
    except Order.DoesNotExist:
        return {"success": False, "message": "Order not found."}