from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("buy/<int:pk>/", views.buy, name='buy'),
    path("buy-order/<int:pk>/", views.buy_order, name="buy-order"),
    path("item/<int:pk>/", views.item_detail, name="item"),
    path("item", views.ItemListView.as_view(), name="items"),
    path("order/<int:pk>/", views.order_detail, name="order"),
    path("order/", views.OrderListView.as_view(), name="orders"),
    path('success/', views.SuccessView.as_view(), name="success"),
    path('cancel/', views.CancelledView.as_view(), name="cancel"),
]