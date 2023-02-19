from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class ContactForm(forms.Form):
	name= forms.CharField(max_length=45)
	email= forms.EmailField()
	country= forms.CharField(max_length=30)
	message= forms.CharField(widget=forms.Textarea)

class RequestForm(forms.Form):
    email = forms.EmailField(required=True)
    amount = forms.FloatField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

class BonusForm(ModelForm):
	class Meta:
		model= Bonus
		fields= '__all__'

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class ClientForm(ModelForm):
	class Meta:
		model= Client
		fields= '__all__'
		exclude= ['user','code', 'recommended_by', 'deposit', 'balance', 'bonus_balance', 'withdrawal', 'profit','roi']



