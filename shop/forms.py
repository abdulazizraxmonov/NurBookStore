from django import forms
from .models import Review, Order
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# forms.py
from django import forms
from .models import Review, UserProfile

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'stars']
        widgets = {
            'stars': forms.HiddenInput()
        }
        labels = {
            'comment': 'Your Review',
            'stars': 'Rating'
        }


class OrderForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1)  # Добавляем поле для указания количества книг

    class Meta:
        model = Order
        fields = ['quantity', 'address', 'phone_number'] 

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'photo']

from django import forms

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()
