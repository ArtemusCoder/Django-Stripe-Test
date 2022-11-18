from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import stripe
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.http import HttpResponseNotFound

from .models import Item, Order

stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    context = {"title": "Main Page"}
    return render(request, "StripeApp/index.html", context)


class ItemListView(ListView):
    model = Item
    template_name = 'StripeApp/items.html'
    context_object_name = 'items'


class OrderListView(ListView):
    model = Order
    template_name = 'StripeApp/orders.html'
    context_object_name = 'orders'


@csrf_exempt
def buy(request, pk):
    if request.method == 'GET':
        item = Item.objects.filter(pk=pk)
        if item.exists():
            item = item[0]
            session = stripe.checkout.Session.create(
                success_url=settings.URL + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.URL + 'cancel/',
                line_items=[
                    {
                        "price": item.price_id,
                        "quantity": 1,
                    },
                ],
                mode="payment",
            )
            return JsonResponse(session)
        else:
            return HttpResponseNotFound("No such item")
    else:
        return HttpResponseNotFound("There is only GET")


@csrf_exempt
def buy_order(request, pk):
    if request.method == 'GET':
        order = Order.objects.filter(pk=pk)
        if order.exists():
            order = order[0]
            line_items = []
            for item in order.items.all():
                line_items.append({"price": item.price_id, "quantity": 1,
                                   "tax_rates": None if order.tax is None else [order.tax.id_stripe]})

            session = stripe.checkout.Session.create(
                success_url=settings.URL + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.URL + 'cancel/',
                line_items=line_items,
                mode="payment",
                discounts=None if order.discount is None else [{"coupon": order.discount.id_stripe}],
            )
            return JsonResponse(session)
        else:
            return HttpResponseNotFound("No such order")
    else:
        return HttpResponseNotFound("There is only GET")


@csrf_exempt
def item_detail(request, pk):
    if request.method == 'GET':
        item = Item.objects.filter(pk=pk)
        if item.exists():
            item = item[0]
            price = stripe.Price.retrieve(
                item.price_id,
            )
            content = {
                "title": item.name,
                "item": item,
                "price": "%.2f" % (float(price["unit_amount"]) / 100),
                "PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
            }
            return render(request, "StripeApp/item.html", content)
        else:
            return HttpResponseNotFound("No such item")
    else:
        return HttpResponseNotFound("There is only GET")


@csrf_exempt
def order_detail(request, pk):
    if request.method == 'GET':
        order = Order.objects.filter(pk=pk)
        if order.exists():
            order = order[0]
            content = {
                "pk": order.pk,
                "order_name": order.name,
                "items": order.items.all(),
                "discounts": None if order.discount is None else order.discount,
                "tax": None if order.tax is None else order.tax,
                "PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
            }
            return render(request, "StripeApp/order.html", content)
        else:
            return HttpResponseNotFound("No such order")
    else:
        return HttpResponseNotFound("There is only GET")


class SuccessView(TemplateView):
    template_name = "StripeApp/success.html"


class CancelledView(TemplateView):
    template_name = "StripeApp/cancel.html"
