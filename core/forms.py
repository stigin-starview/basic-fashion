from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_METHODS = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main Street'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite'
    }))
    # try to understand this !! 
    # widget and class is there to pass the styling of the pulldown selector. 
    country = CountryField(blank_label='select country').formfield(
        widget= CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
    }))
    # install dajngo state and deal with the attrs     
    state = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    })) 

    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(required= False)
    save_info = forms.BooleanField(required= False)
    payment_option = forms.ChoiceField(
                    widget=forms.RadioSelect, choices=PAYMENT_METHODS)



class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2',
    }))
