from django import forms
from .models import Item, Discount, Tax, Order


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'currency']


class DiscountCreateForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['name', 'amount_of', 'percent_of']


class TaxCreateForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['name', 'description', 'inclusive', 'percentage']


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'items', 'discount', 'tax']
