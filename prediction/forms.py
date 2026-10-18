from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import BUYING_CHOICES, DOOR_CHOICES, LUG_BOOT_CHOICES, MAINT_CHOICES, PERSON_CHOICES, SAFETY_CHOICES


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {"username": forms.TextInput(attrs={"placeholder": "Choose a username", "autocomplete": "username"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"placeholder": "Create a password", "autocomplete": "new-password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm your password", "autocomplete": "new-password"})


class CarEvaluationForm(forms.Form):
    buying = forms.ChoiceField(choices=BUYING_CHOICES, label="Buying Price")
    maint = forms.ChoiceField(choices=MAINT_CHOICES, label="Maintenance Cost")
    doors = forms.ChoiceField(choices=DOOR_CHOICES, label="Number of Doors")
    persons = forms.ChoiceField(choices=PERSON_CHOICES, label="Passenger Capacity")
    lug_boot = forms.ChoiceField(choices=LUG_BOOT_CHOICES, label="Luggage Boot Size")
    safety = forms.ChoiceField(choices=SAFETY_CHOICES, label="Safety Level")
