from tools.registry import register_tool
from ecommerce.models import Order


@register_tool
def find_order(order_id: str):
    """Find order by ID"""
    order = Order.objects.get(order_id=order_id)

    return {
        "order_id": order.order_id,
        "status": order.status,
        "total": float(order.total_amount),
    }


@register_tool
def list_orders(status: str = None):
    """List all orders (optional filter)"""
    qs = Order.objects.all()

    if status:
        qs = qs.filter(status=status)

    return list(qs.values("order_id", "status", "total_amount"))


@register_tool
def confirm_cancel_order(order_id: str):
    """Cancel order after confirmation"""
    order = Order.objects.get(order_id=order_id)

    if order.status in ["delivered", "cancelled"]:
        return {"error": "Cannot cancel"}

    order.status = "cancelled"
    order.save()

    return {"success": True}