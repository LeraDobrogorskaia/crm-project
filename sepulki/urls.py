from django.urls import path

from sepulki.views import OrderListView, OrderDetailView, create_order_view


urlpatterns = [
    path('', OrderListView.as_view(), name='sepulki-list'),
    path('create/', create_order_view, name='sepulki-create'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='sepulki-detail'),
]
