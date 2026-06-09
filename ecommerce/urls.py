from django.urls import path
from .views import (
    customer_list,
    product_list,
    order_list,
)

urlpatterns = [
    path("customers/", customer_list, name="customer-list"),
    path("products/", product_list, name="product-list"),
    path("orders/", order_list, name="order-list"),
]