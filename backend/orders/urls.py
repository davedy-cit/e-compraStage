from django.urls import path

from . import views

urlpatterns = [
    path("transaction-statuses/", views.TransactionStatusList.as_view(), name="transaction-status-list"),
    path("transaction-types/", views.TransactionTypeList.as_view(), name="transaction-type-list"),
    path("payment-statuses/", views.PaymentStatusList.as_view(), name="payment-status-list"),
    path("delivery-statuses/", views.DeliveryStatusList.as_view(), name="delivery-status-list"),
    path("fulfillment-methods/", views.FulfillmentMethodList.as_view(), name="fulfillment-method-list"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path("transactions/<int:pk>/", views.TransactionDetail.as_view(), name="transaction-detail"),
    path("", views.OrderList.as_view(), name="order-list"),
    path("<int:pk>/", views.OrderDetail.as_view(), name="order-detail"),
]
