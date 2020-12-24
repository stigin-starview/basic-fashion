from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, BillingAddress
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, "checkout.html", context)
    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                state = form.cleaned_data.get('state')
                zip = form.cleaned_data.get('zip')

                # TODO  Add functinoalities to this fields.
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address = street_address,
                    apartment_address= apartment_address,
                    country= country,
                    state=state,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO add redirect to the selected payment options.
                return redirect("core:checkout")
            messages.warning(self.request, "failed to checkout")
            return redirect("core:checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "Your Cart is Empty")
            return redirect("core:order-summary")

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "payment.html")




class HomeView(ListView):
    model = Item
    #paginate is a field where you could show how many items to be shown in a page.??
    paginate_by = 10
    template_name = "home.html"


# mixing is the login recored way with classes
class OrderSummaryView(LoginRequiredMixin, View):  
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Your Cart is Empty")
            return redirect("/")
        

class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

def checkout(request):
    return render(request, "checkout.html")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
            return redirect("core:order-summary")
            
        else:
            order.items.add(order_item)
            messages.info(request, "This item is added to the cart")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item is added to your cart ")
    return redirect("core:order-summary")

@login_required
def remove_from_cart (request,slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from the cart")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:order-summary")

    else:
        messages.info(request, "you didn't place any order.")
        return redirect("core:order-summary")
    

@login_required
def remove_single_item_from_cart (request,slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "Item quantity updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:product", slug=slug)

    else:
        messages.info(request, "you didn't place any order.")
        return redirect("core:product", slug=slug)
    










