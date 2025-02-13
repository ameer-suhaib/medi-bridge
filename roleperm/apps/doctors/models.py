from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Doctor(models.Model):

    QUALIFICATION_CHOICES = [
        ('MBBS', 'MBBS'),
        ('MD', 'MD'),
        ('MS', 'MS'),
        ('MCh', 'MCh'),
        ('DNB', 'DNB'),
        ('DGO', 'DGO'),
        ('MDS', 'MDS'),
        ('DPM', 'DPM'),
        ('FRCS', 'FRCS'),
        ('DM', 'DM'),
    ]

    SPECIALIZATION_CHOICES = [
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Orthopedics', 'Orthopedics'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Gastroenterology', 'Gastroenterology'),
        ('Obstetrics and Gynecology', 'Obstetrics and Gynecology'),
        ('Endocrinology', 'Endocrinology'),
        ('Ophthalmology', 'Ophthalmology'),
        ('Psychiatry', 'Psychiatry'),
        ('Urology', 'Urology'),
        ('Rheumatology', 'Rheumatology'),
        ('Pulmonology', 'Pulmonology'),
        ('Hematology', 'Hematology'),
        ('Nephrology', 'Nephrology'),
        ('Radiology', 'Radiology'),
        ('Oncology', 'Oncology'),
        ('Plastic Surgery', 'Plastic Surgery'),
        ('Anesthesiology', 'Anesthesiology'),
        ('Emergency Medicine', 'Emergency Medicine'),
        ('Pathology', 'Pathology'),
        ('Family Medicine', 'Family Medicine'),
        ('Geriatrics', 'Geriatrics'),
        ('Infectious Disease', 'Infectious Disease'),
        ('Sports Medicine', 'Sports Medicine'),
        ('Allergy and Immunology', 'Allergy and Immunology'),
        ('Vascular Surgery', 'Vascular Surgery'),
        ('Clinical Genetics', 'Clinical Genetics'),
        ('Occupational Medicine', 'Occupational Medicine'),
        ('Pain Medicine', 'Pain Medicine'),
    ]
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    specialization = models.CharField(max_length=250,choices=SPECIALIZATION_CHOICES,default='Cardiology')
    qualification = models.CharField(max_length=250,choices=QUALIFICATION_CHOICES,default='MBBS')
    experience = models.PositiveIntegerField()
    consultation_fee = models.DecimalField(max_digits=10,decimal_places=2,default=0,null=True)
    department = models.CharField(max_length=300,null=False,default='')
    hospital_name = models.CharField(max_length=250)

    def __str__(self):
        return self.user.username   
    

class TimeSlot(models.Model):
    DAY_CHOICES = (
        ('Monday', 'monday'),
        ('Tuesday', 'tuesday'),
        ('Wednesday', 'wednesday'),
        ('Thursday', 'thursday'),
        ('Friday', 'friday'),
        ('Saturday', 'saturday'),
        ('Sunday', 'sunday')
    )
    TIME_BLOCK_CHOICES = [
        ('08:00-10:00', '8:00 AM - 10:00 AM'),
        ('10:00-12:00', '10:00 AM - 12:00 PM'),
        ('12:00-14:00', '12:00 PM - 2:00 PM'),
        ('14:00-16:00', '2:00 PM - 4:00 PM'),
        ('16:00-18:00', '4:00 PM - 6:00 PM'),
        ('18:00-20:00', '6:00 PM - 8:00 PM'),
    ]
    
    SLOT_DURATION_CHOICES = [
        ('30', '30 Minutes'),
        ('60', '1 Hour'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="time_slots")
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    time_block = models.CharField(max_length=20, choices=TIME_BLOCK_CHOICES)
    slot_duration = models.CharField(max_length=10, choices=SLOT_DURATION_CHOICES, default='30')
    
    max_appointments = models.PositiveIntegerField(
        default=4, 
        help_text="Maximum number of appointments per two-hour block",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)  # Updated to support 8 slots of 30 minutes
        ]
    )
    
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['doctor', 'day', 'time_block']
        verbose_name_plural = "Time Slots"
    
    def __str__(self):
        return f"{self.doctor.user.username} - {self.get_day_display()} - {self.get_time_block_display()} ({self.slot_duration} min slots)"
    
    @property
    def start_time(self):
        return self.get_time_block_display().split(' - ')[0]
    
    @property
    def end_time(self):
        return self.get_time_block_display().split(' - ')[1]
    
    def get_slot_times(self):
        """
        Generate 30-minute slot times within the 2-hour block
        """
        from datetime import datetime, timedelta
        
        start = datetime.strptime(self.start_time, '%I:%M %p')
        end = datetime.strptime(self.end_time, '%I:%M %p')
        
        slots = []
        current = start
        while current < end:
            slot_end = current + timedelta(minutes=int(self.slot_duration))
            slots.append({
                'start': current.strftime('%I:%M %p'),
                'end': slot_end.strftime('%I:%M %p')
            })
            current = slot_end
        
        return slots
    
    def get_available_appointments(self, date=None):
        from django.apps import apps
        
        try:
            # Dynamically import Appointment model to avoid circular imports
            Appointment = apps.get_model('patientpro', 'Appointment')
            
            # Validate inputs
            if not self.is_available:
                return 0
            
            # If no date is provided, return max appointments
            if date is None:
                return self.max_appointments
            
            # Count booked appointments for this specific slot and date
            booked_appointments = Appointment.objects.filter(
                doctor=self.doctor,
                time_slot=self,
                appointment_date=date,
                status__in=['PENDING', 'CONFIRMED']
            )
            
            booked_count = booked_appointments.count()
            
            # Calculate available appointments
            available = max(0, self.max_appointments - booked_count)
            
            return available
        
        except Exception as e:
            print(f"Error in get_available_appointments: {str(e)}")
            return 0