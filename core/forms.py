from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

# impliment paypal method
PAYMENT_METHODS = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    # try to understand this !! 
    # widget and class is there to pass the styling of the pulldown selector. 
    shipping_country = CountryField(blank_label='select country').formfield(
        required=False,
        widget= CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
    }))
    # install dajngo state and deal with the attrs     
    # shipping_state = forms.CharField(required=False) 

    shipping_zip = forms.CharField(required=False)


    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='select country').formfield(
        required=False,
        widget= CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
    }))
    billing_zip = forms.CharField(required=False)


    same_billing_address = forms.BooleanField(required= False)
    set_default_shipping = forms.BooleanField(required= False)
    use_default_shipping = forms.BooleanField(required= False)
    set_default_billing = forms.BooleanField(required= False)
    use_default_billing = forms.BooleanField(required= False)

    payment_option = forms.ChoiceField(
                    widget=forms.RadioSelect, choices=PAYMENT_METHODS)



class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2',
    }))



class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()



class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
