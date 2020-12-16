from django.urls import path, reverse

from .views import (
    home,
    checkout,
    products,
)

# app_name ='core'

urlpatterns = [
    path('', home, name= 'home-page'),
    path('checkout/',checkout,name= 'checkout-page'),
    path('products/',products,name= 'products-page'),

]