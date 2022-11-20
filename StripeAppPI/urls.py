from django.urls import path
from . import views

urlpatterns = [
    path("payment/item/<int:pk>/", views.item_detail, name='item-paymentintent'),
    path("payment/buy/<int:pk>/", views.item_buy, name='buy-item-paymentintent'),
    path("payment/item", views.ItemListView.as_view(), name="items-paymentintent"),
    path("payment/order/<int:pk>/", views.order_detail, name="order-paymentintent"),
    path("payment/buy-order/<int:pk>/", views.order_buy, name="buy-order-paymentintent"),
    path("payment/order/", views.OrderListView.as_view(), name="orders-paymentintent"),
]