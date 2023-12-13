from typing import Any
from django import forms

from sepulki.models import Order, PreparedPropertiesSet


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('client', 'color', 'size', 'material')

    def save(self, commit: bool = ...) -> Any:
        if self.instance:
            order = self.instance

            prepared_props = PreparedPropertiesSet.objects.filter(
                color=order.color,
                size=order.size,
                material=order.material
            ).first()

            # Set order status `in_process` if the properties set is
            # standard
            if prepared_props is not None:
                self.instance.status = Order.StatusChoice.IN_PROCESS

        return super().save(commit)
