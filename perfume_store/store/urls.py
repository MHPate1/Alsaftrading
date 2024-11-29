from django.urls import path
from . import views


app_name = 'store'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('liked/', views.LikedView.as_view(), name='liked'),
    path('cart/', views.CartView.as_view(), name='cart'),
]