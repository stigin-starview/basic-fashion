from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Item


# def item_list(request):
#     context = {
#         'items' : Item.objects.all()
#     }
#     return render(request, "item_list.html", context)


# def home(request):
#     context = {
#         'items' : Item.objects.all()
#     }
#     return render(request, "home.html", context)

class HomeView(ListView):
    model = Item
    template_name = "home.html"

class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

def checkout(request):
    return render(request, "checkout.html")

# def products(request):
#     return render(request, "product.html")
