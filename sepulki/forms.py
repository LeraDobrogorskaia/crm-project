from django import forms

from sepulki.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('client', 'color', 'size', 'material')
