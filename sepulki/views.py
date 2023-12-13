from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView

from sepulki.models import Order, Color, Material, Size, OrderReturn
from sepulki.forms import OrderForm


class OrderListView(ListView):
    model = Order
    queryset = Order.objects.all().order_by('-modified')
    template_name = 'sepulki/home.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(client=self.request.user)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(
                '%s?next=%s' % (
                    reverse_lazy('account-login'),
                    request.get_full_path(),
                ),
            )

        return super().get(request, *args, **kwargs)


class OrderDetailView(DetailView):
    model = Order
    queryset = Order.objects.all().order_by('-modified')
    template_name = 'sepulki/retrieve.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()

        context = {}

        if not self.object.can_be_returned:
            context["errors"] = "The order can not be returned."

        if self.object.is_returned:
            context["errors"] = "The order already returned."

        if not hasattr(context, "errors"):
            OrderReturn.objects.create(order=self.object)
            context['success'] = (
                "Order has been returned, pending manager decision."
            )

        return self.render_to_response(
            context | self.get_context_data(object=self.object),
        )


def create_order_view(request: HttpRequest):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(
            reverse_lazy('account-login'),
            next=request.get_full_path(),
        )

    context={}

    context['colors'] = Color.objects.all().filter(is_active=True)
    context['sizes'] = Size.objects.all().filter(is_active=True)
    context['materials'] = Material.objects.all().filter(is_active=True)

    if request.method == "POST":
        form = OrderForm(request.POST)
        is_confirmed = request.POST.get('is_confirmed', False)

        if form.is_valid():
            order = form.save(commit=False)

            if is_confirmed:
                order.save()
                return HttpResponseRedirect(reverse_lazy('sepulki-list'))

            context["confirm"] = {
                "weight": order.weight,
                "cost": order.total_cost,
            }

        context["form"] = form
        context["errors"] = form.errors

    if request.method == "GET":
        context["form"] = OrderForm()

    return render(request, 'sepulki/create.html', context=context)

