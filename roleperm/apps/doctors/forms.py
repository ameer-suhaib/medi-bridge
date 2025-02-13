from django import forms
from .models import Doctor,TimeSlot
from django.contrib.auth.models import User

class DoctorForm(forms.ModelForm):
    specialization = forms.ChoiceField(
        choices=Doctor.SPECIALIZATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    qualification = forms.ChoiceField(
        choices=Doctor.QUALIFICATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    experience = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    hospital_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Doctor
        fields = ['specialization', 'qualification', 'experience', 'hospital_name']

class DoctorUser(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']



# from django import forms

# forms.py

# forms.py

from django import forms

class TimeSlotManagementForm(forms.Form):
    DAYS_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    # Let the doctor select multiple days
    day = forms.ChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.Select,
        label="Select Day"
    )

    # Let the doctor select multiple time blocks (intervals)
    time_block = forms.MultipleChoiceField(
        choices=TimeSlot.TIME_BLOCK_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Select Time Blocks"
    )
    
    max_appointments = forms.IntegerField(
        initial=4,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        label="Max Appointments per Slot"
    )


class DocProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["specialization","qualification","experience","consultation_fee","department","hospital_name"]

