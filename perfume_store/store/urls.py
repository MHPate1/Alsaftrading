from django.urls import path
from . import views


app_name = 'store'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('product/<str:category>/<int:product_id>/', views.SingleProductView.as_view(), name='single_product'),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('create-checkout-session/', views.CheckoutView.as_view(), name='create-checkout-session'),
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
]