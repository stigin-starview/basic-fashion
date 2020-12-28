
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .forms import CheckoutForm, CouponForm

import stripe
stripe.api_key = settings.STRIPE_PRIVATE_KEY





class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Cart is empty")
            return redirect("core:checkout")
    

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
                
                if payment_option == 'S':
                    return redirect('core:payment', payment_option= 'stripe')
                elif payment_option =='P':
                    return redirect('core:payment', payment_option= 'paypal')
                else:
                    messages.warning(self.request, "Invalid payment option")
                    return redirect("core:checkout")

        except ObjectDoesNotExist:
            messages.warning(self.request, "Your Cart is Empty")
            return redirect("core:order-summary")



class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
                
            context = {
                'order': order,
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
                'DISPLAY_COUPON_FORM': False

            }
            return render(self.request, "payment.html", context)

        else:
            messages.warning(self.request, "Enter Shipping Details to continue.")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total()) * 100

        try:
            # find the way to pass in the shipping adress to the cart
            # when using stripe, by indian standards you need to provide a shpping deatail( like below ) and a description about the product. 
            charge = stripe.Charge.create(
                shipping={
                        'name': 'Jenny Rosen',
                        'address': {
                        'line1': '510 Townsend St',
                        'postal_code': '98140',
                        'city': 'San Francisco',
                        'state': 'CA',
                        'country': 'US',
                        },
                    },
                amount=amount,  # cents
                currency="usd",
                description= "this is a test product",
                source=token
            )
                    # Create Payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            
            order_items = order.items.all() 
            order_items.update(ordered=True)
            for item in order_items:
                item.save()


            order.ordered = True
            order.payment = payment
            order.save()   
            messages.success(self.request, " Your order was successful")
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught

            messages.warning(self.request, f" {err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, "Invalid Parameters")
            return redirect("/")
            
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not Authenticated")
            return redirect("/")
            
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")
          
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(self.request, "Something Went Wrong.")
            return redirect("/")
        
        except Exception as e:
            # Something else happened, completely unrelated to Stripe

            #send an email to ourself
            messages.warning(self.request, "A serious error occured")
            return redirect("/")

        

    





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
            messages.warning(self.request, "Your Cart is Empty")
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
    


def get_coupon(request, code):

    try:
        coupon = Coupon.objects.get(code=code)
        return coupon

    except ObjectDoesNotExist:
        messages.info(request, "Invalid Coupon")
        return redirect("core:checkout")




class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Coupon added successfully")
                return redirect("core:checkout")

            except ObjectDoesNotExist:
                messages.info(self.request, "Your Cart is Empty")
                return redirect("core:checkout")







