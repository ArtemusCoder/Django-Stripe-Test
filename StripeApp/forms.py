from django import forms
from .models import Item, Discount, Tax


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price']


class DiscountCreateForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['name', 'amount_of', 'percent_of']


class TaxCreateForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['name', 'description', 'inclusive', 'percentage']
