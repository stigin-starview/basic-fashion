from django.shortcuts import render

from .models import Item


def item_list(request):
    context = {
        'items' : Item.objects.all()
    }
    return render(request, "item_list.html", context)


def home(request):
    return render(request, "home.html")

def checkout(request):
    return render(request, "checkout.html")

def products(request):
    return render(request, "products.html")
