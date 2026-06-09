from django.http import JsonResponse

from .models import (
    Customer,
    Product,
    Order,
)


def customer_list(request):
    customers = list(
        Customer.objects.values(
            "id",
            "name",
            "email",
            "phone",
        )
    )

    return JsonResponse({
        "customers": customers
    })


def product_list(request):
    products = list(
        Product.objects.values(
            "id",
            "name",
            "price",
            "stock",
        )
    )

    return JsonResponse({
        "products": products
    })


def order_list(request):

    orders_data = []

    orders = Order.objects.select_related(
        "customer"
    ).prefetch_related(
        "items__product"
    )

    for order in orders:

        items = []

        for item in order.items.all():
            items.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "price": float(item.price),
            })

        orders_data.append({
            "order_id": order.order_id,
            "customer": order.customer.name,
            "status": order.status,
            "total_amount": float(order.total_amount),
            "items": items,
        })

    return JsonResponse({
        "orders": orders_data
    })