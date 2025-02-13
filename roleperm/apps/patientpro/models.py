from django.db import models
from django.contrib.auth.models import User
from apps.doctors.models import Doctor, TimeSlot


class Patient(models.Model):
    BLD_GRP_CHOICES = (
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        )
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(null=True)
    street = models.CharField(null=True,max_length=150)
    city = models.CharField(null=True,max_length=150)
    state = models.CharField(null=True,max_length=150)
    zipcode = models.CharField(null=True,max_length=6)
    blood_group = models.CharField(choices=BLD_GRP_CHOICES,max_length=6,null=True)
    medical_history = models.TextField(default='')

    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="doctor_appointments")
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    start_time = models.TimeField()  # New field for precise start time
    end_time = models.TimeField()    # New field for precise end time
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='PENDING')
    symptoms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['doctor', 'time_slot', 'appointment_date', 'start_time']
        ordering = ['-appointment_date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.doctor.user.username} - {self.appointment_date} {self.start_time}"
     

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE,related_name="reviews")
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name="reviews")
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.user.username} has rated {self.rating} to {self.doctor.user.username}"