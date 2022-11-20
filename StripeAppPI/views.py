from django.shortcuts import render
import stripe
from django.http.response import JsonResponse
from django.conf import settings
from StripeApp.models import Item, Order
from django.http import HttpResponseNotFound
from django.views.generic import ListView

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderListView(ListView):
    model = Order
    template_name = 'StripeAppPI/orders.html'
    context_object_name = 'orders'


class ItemListView(ListView):
    model = Item
    template_name = 'StripeAppPI/items.html'
    context_object_name = 'items'


def item_buy(request, pk):
    if request.method == 'GET':
        item = Item.objects.filter(pk=pk)
        if item.exists():
            item = item[0]
            try:
                intent = stripe.PaymentIntent.create(
                    amount=item.price,
                    currency=item.currency,
                    payment_method_types=["card"],
                    statement_descriptor="Custom descriptor",
                )
            except Exception as e:
                print(e)
                return HttpResponseNotFound("Something wrong with Payment")
            return JsonResponse({'clientSecret': intent['client_secret']})


def order_buy(request, pk):
    if request.method == 'GET':
        order = Order.objects.filter(pk=pk)
        if order.exists():
            order = order[0]
            amount = 0.0
            items_sum = sum([int(item.price) for item in order.items.all()])
            amount = items_sum
            if order.discount is not None:
                if order.discount.amount_of is None:
                    amount = int(amount - (items_sum * (order.discount.percent_of / 100)))
                else:
                    amount = amount - order.discount.amount_of
            if order.tax.count() != 0:
                for tax in order.tax.all():
                    if not tax.inclusive:
                        amount = amount + (amount * (tax.percentage / 100))
                    else:
                        amount = amount - (amount * (tax.percentage / 100))
            amount = round(amount)
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(amount),
                    currency=order.items.all()[0].currency,
                    payment_method_types=["card"],
                    statement_descriptor="Custom descriptor",
                )
            except Exception as e:
                print(e)
                return HttpResponseNotFound("Something wrong with Payment")
            return JsonResponse({'clientSecret': intent['client_secret']})


def item_detail(request, pk):
    if request.method == 'GET':
        item = Item.objects.filter(pk=pk)
        if item.exists():
            item = item[0]
            content = {
                "title": item.name,
                "item": item,
                "price": "%.2f" % float(item.price / 100),
                "PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                "URL": settings.URL,
            }
            return render(request, "StripeAppPI/item.html", content)
        else:
            return HttpResponseNotFound("No such item")
    else:
        return HttpResponseNotFound("There is only GET")


def order_detail(request, pk):
    if request.method == 'GET':
        order = Order.objects.filter(pk=pk)
        if order.exists():
            order = order[0]
            amount = 0.0
            items_sum = sum([int(item.price) for item in order.items.all()])
            amount = items_sum
            if order.discount is not None:
                if order.discount.amount_of is None:
                    amount = float(amount - (items_sum * (order.discount.percent_of / 100)))
                else:
                    amount = amount - order.discount.amount_of
            if order.tax.count() != 0:
                for tax in order.tax.all():
                    if not tax.inclusive:
                        amount = amount + (amount * (tax.percentage / 100))
                    else:
                        amount = amount - (amount * (tax.percentage / 100))
            amount = round(amount)
            content = {
                "pk": order.pk,
                "order_name": order.name,
                "items": order.items.all(),
                "discounts": None if order.discount is None else order.discount,
                "taxs": None if order.tax.count() == 0 else order.tax.all(),
                "PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                "amount": "%.2f" % float(amount / 100)
            }
            return render(request, "StripeAppPI/order.html", content)
        else:
            return HttpResponseNotFound("No such item")
    else:
        return HttpResponseNotFound("There is only GET")
