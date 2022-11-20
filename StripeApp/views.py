from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import stripe
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.http import HttpResponseNotFound
from .forms import ProductCreateForm, DiscountCreateForm, TaxCreateForm, OrderCreateForm

from .models import Item, Order

stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    context = {"title": "Main Page"}
    return render(request, "StripeApp/index.html", context)


def create(request):
    context = {"title": "Create Page"}
    return render(request, "StripeApp/create.html", context)


class ItemListView(ListView):
    model = Item
    template_name = 'StripeApp/item/items.html'
    context_object_name = 'items'


def createProduct(request):
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            currency = form.cleaned_data.get('currency')
            price = form.cleaned_data.get('price')
            try:
                product = stripe.Product.create(name=name, description=description)
                price_stripe = stripe.Price.create(unit_amount=price, currency=currency, product=product['id'])
            except Exception as e:
                print(e)
                return HttpResponseNotFound("Something wrong with Payment")
            item.price_id = price_stripe['id']
            item.save()
            return redirect('items')
    else:
        form = ProductCreateForm()
    return render(request, 'StripeApp/create/create-product.html', {'form': form})


def createDiscount(request):
    if request.method == 'POST':
        form = DiscountCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            percent_of = form.cleaned_data.get('percent_of')
            amount_of = form.cleaned_data.get('amount_of')
            print(percent_of, amount_of)
            if percent_of is not None and amount_of is not None:
                return redirect('create-discount')
            try:
                stripe_discount = stripe.Coupon.create(percent_off=percent_of, name=name)
            except Exception as e:
                return HttpResponseNotFound(e)
            discount = form.save(commit=False)
            discount.id_stripe = stripe_discount['id']
            discount.save()
            return redirect('items')
    else:
        form = DiscountCreateForm()
    return render(request, 'StripeApp/create/create-discount.html', {'form': form})


def createTax(request):
    if request.method == 'POST':
        form = TaxCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            inclusive = form.cleaned_data.get('inclusive')
            percentage = form.cleaned_data.get('percentage')
            try:
                stripe_tax = stripe.TaxRate.create(display_name=name, description=description, inclusive=inclusive,
                                                percentage=percentage)
            except Exception as e:
                print(e)
                return HttpResponseNotFound("Something wrong with Payment")
            tax = form.save(commit=False)
            tax.id_stripe = stripe_tax['id']
            tax.save()
            return redirect('items')
    else:
        form = TaxCreateForm()
    return render(request, 'StripeApp/create/create-tax.html', {'form': form})


def createOrder(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('orders')
    else:
        form = OrderCreateForm()
    return render(request, 'StripeApp/create/create-order.html', {'form': form})


class OrderListView(ListView):
    model = Order
    template_name = 'StripeApp/order/orders.html'
    context_object_name = 'orders'


@csrf_exempt
def buy(request, pk):
    if request.method == 'GET':
        item = Item.objects.filter(pk=pk)
        if item.exists():
            item = item[0]
            try:
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
            except Exception as e:
                print(e)
                return HttpResponseNotFound("Problems with Stripe")
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
                                   "tax_rates": None if order.tax.count() == 0 else [str(id.id_stripe) for id in
                                                                                     order.tax.all()]})
            try:
                session = stripe.checkout.Session.create(
                    success_url=settings.URL + 'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=settings.URL + 'cancel/',
                    line_items=line_items,
                    mode="payment",
                    discounts=None if order.discount is None else [{"coupon": order.discount.id_stripe}],
                )
                return JsonResponse(session)
            except Exception as e:
                print(e)
                return HttpResponseNotFound("Problems with Stripe")
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
            content = {
                "title": item.name,
                "item": item,
                "price": "%.2f" % float(item.price / 100),
                "PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
            }
            return render(request, "StripeApp/item/item.html", content)
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
                "taxs": None if order.tax.count() == 0 else order.tax.all(),
                "PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
            }
            return render(request, "StripeApp/order/order.html", content)
        else:
            return HttpResponseNotFound("No such order")
    else:
        return HttpResponseNotFound("There is only GET")


class SuccessView(TemplateView):
    template_name = "StripeApp/success.html"


class CancelledView(TemplateView):
    template_name = "StripeApp/cancel.html"
