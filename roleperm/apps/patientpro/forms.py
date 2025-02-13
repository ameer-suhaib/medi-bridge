# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Appointment, Patient

class UserForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']


class PatientForm(forms.ModelForm):
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number',
            'pattern': '[0-9]{10}'
        }),
        help_text='Enter 10 digit phone number'
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter address',
            'rows': 3
        })
    )
    medical_history = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter medical history',
            'rows': 4
        })
    )

    class Meta:
        model = Patient
        fields = ['phone_number', 'address', 'medical_history']



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['phone_number','address','street','city','state','zipcode','blood_group']   