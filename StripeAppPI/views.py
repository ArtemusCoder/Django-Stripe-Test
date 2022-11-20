from django.shortcuts import render
import stripe
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


def item_detail(request, pk):
    if request.method == 'GET':
        item = Item.objects.filter(pk=pk)
        if item.exists():
            item = item[0]
            intent = stripe.PaymentIntent.create(
                amount=item.price,
                currency=item.currency,
                payment_method_types=["card"],
                statement_descriptor="Custom descriptor",
            )
            content = {
                "title": item.name,
                "item": item,
                "price": "%.2f" % float(item.price / 100),
                "PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                "client_secret": intent.client_secret,
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
            print(items_sum)
            amount = items_sum
            if order.discount is not None:
                if order.discount.amount_of is None:
                    amount = int(amount - (items_sum * (order.discount.percent_of / 100)))
                else:
                    amount = amount - order.discount.amount_of
            print(amount)
            if order.tax.count() != 0:
                for tax in order.tax.all():
                    if not tax.inclusive:
                        amount = amount + (amount * (tax.percentage / 100))
                    else:
                        amount = amount - (amount * (tax.percentage / 100))
            amount = int(amount)
            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency=order.items.all()[0].currency,
                payment_method_types=["card"],
                statement_descriptor="Custom descriptor",
            )
            content = {
                "pk": order.pk,
                "order_name": order.name,
                "items": order.items.all(),
                "discounts": None if order.discount is None else order.discount,
                "taxs": None if order.tax.count() == 0 else order.tax.all(),
                "PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                "amount": "%.2f" % float(amount / 100),
                "client_secret": intent.client_secret,
            }
            return render(request, "StripeAppPI/order.html", content)
        else:
            return HttpResponseNotFound("No such item")
    else:
        return HttpResponseNotFound("There is only GET")
