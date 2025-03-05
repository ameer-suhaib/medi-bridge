# # Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone

from apps.patientpro.models import Appointment

from .models import Doctor, TimeSlot
from .forms import DocProfileForm, DoctorForm, TimeSlotManagementForm, DoctorUser

DEFAULT_PASS = 'Doctor@123'

def listing_doc(request):
    doctors = Doctor.objects.all()
    return render(request, "doc_listing.html", {"doctors": doctors})

def create_doc(request):
    if request.method == 'POST':
        doctor_form = DoctorForm(request.POST)
        user_form = DoctorUser(request.POST)
        if doctor_form.is_valid() and user_form.is_valid():
            user_data = user_form.cleaned_data
            user_name = user_data['username']
            user_email = user_data['email']
            user = User.objects.create_user(
                username=user_name,
                email=user_email,
                password=DEFAULT_PASS
            )
            doctor_group, created = Group.objects.get_or_create(name="Doctor")
            user.groups.add(doctor_group)

            doctor_data = doctor_form.save(commit=False)
            doctor_data.user = user

            doctor_data.save()

            return redirect("doc_listing")
    else:
        doctor_form = DoctorForm()
        user_form = DoctorUser()

    return render(request, "create_doc.html", {"doctors": doctor_form, "user": user_form})

def view_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    return render(request, 'view_doctor.html', {'doctor': doctor})

def edit_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)

    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('doc_listing')  
    else:
        form = DoctorForm(instance=doctor)

    return render(request, 'edit_doctor.html', {'forms': form, 'doctor': doctor})

def delete_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == 'POST':
        doctor.delete()
        return redirect('doc_listing') 
    return render(request, 'delete_doctor.html', {'doctor': doctor})

def is_doctor(user):
    return user.groups.filter(name='Doctor').exists()

@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    today = timezone.now().date()
    doctor = request.user.doctor  # Assuming there's a one-to-one relationship between User and Doctor

    context = {
        # 'today_appointments_count': Appointment.objects.filter(
        #     doctor=doctor,
        #     date=today
        # ).count(),
        # 'total_patients': Patient.objects.filter(doctor=doctor).count(),
        # 'upcoming_appointments': Appointment.objects.filter(
        #     doctor=doctor,
        #     date__gte=today
        # ).order_by('date', 'time')[:5],
        # 'recent_patients': Patient.objects.filter(
        #     doctor=doctor
        # ).order_by('-last_visit')[:5],
        'total_appointment':Appointment.objects.filter(doctor=doctor).count(),
        'today_appointments':Appointment.objects.filter(doctor=doctor,created_at = today)
    }
    
    return render(request, 'doctor_dashboard.html', context)

@login_required
def manage_slot(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == 'POST':
        form = TimeSlotManagementForm(request.POST, initial={'doctor': doctor})
        if form.is_valid():
            day = form.cleaned_data['day']
            time_blocks = form.cleaned_data['time_block']
            max_appointments = form.cleaned_data['max_appointments']

            for timeblock in time_blocks:
                TimeSlot.objects.create(
                    doctor = doctor,
                    day = day,
                    time_block = timeblock,
                    max_appointments = max_appointments
                )
            messages.success(request, f"Time slots for {day} added successfully.")
            return redirect('manage_slots')
            
    else:
        form = TimeSlotManagementForm()
    
    # Get existing slots for the doctor
    existing_slots = TimeSlot.objects.filter(doctor=doctor).order_by('day', 'time_block')
    
    context = {
        'form': form,
        'existing_slots': existing_slots,
    }
    
    return render(request, 'manage_slote.html', context)

@login_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id, doctor__user=request.user)
    
    if request.method == 'POST':
        slot_info = f"{slot.get_time_block_display()} on {slot.get_day_display()}"
        slot.delete()
        messages.success(request, f"Time slot {slot_info} deleted successfully.")
        return redirect('manage_slots')
    
    return render(request, 'confirm_delete_slot.html', {'slot': slot})

@login_required
@user_passes_test(is_doctor)
def edit_slot(request, slot_id):
    doctor = request.user.doctor
    slot = get_object_or_404(TimeSlot, id=slot_id, doctor=doctor)
    
    if request.method == 'POST':
        form = TimeSlotManagementForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Time slot updated successfully!')
            return redirect('manage_slots')
    else:
        form = TimeSlotManagementForm(instance=slot)
    
    return render(request, 'edit_slot.html', {'form': form, 'slot': slot})


def doc_profile(request,id):
    doctor = get_object_or_404(Doctor,user_id = id)
    print(doctor,"doccc")
    if request.method == 'POST':
        doc_profile_form=DocProfileForm(request.POST, instance=doctor)
        try:
            if doc_profile_form.is_valid():
                print("enterrrrrrrr")
                doc_profile_form.save()
                return redirect("doctor_dashboard")
            
        except Exception as err:
            messages.error(request,f"Something went wrong {err}")

    doc_profile_form = DocProfileForm(instance = doctor)
    return render(request,"doc_profile.html",{"forms":doc_profile_form,'doctor':doctor})


@login_required
def doctor_appointments(request):
    try:
        doctor = request.user.doctor
    except Exception as e:
        messages.error(request, "No doctor profile associated with this account.")
        return render(request, 'doctor_appointments.html', {'error': 'No doctor profile found'})

    # Handle appointment status update
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')	
        action = request.POST.get('action')
        
        try:
            appointment = Appointment.objects.get(
                id=appointment_id, 
                doctor=doctor
            )
            
            if action == 'confirm':
                appointment.status = 'CONFIRMED'
            elif action == 'cancel':
                appointment.status = 'CANCELLED'
            
            appointment.save()
            messages.success(request, f'Appointment {action}ed successfully.')
            return redirect('doctor_appointments')
        
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found.')

    # Get filter parameters from request
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Base queryset for appointments
    appointments = Appointment.objects.filter(doctor=doctor)

    # Apply status filter if provided
    if status_filter:
        appointments = appointments.filter(status=status_filter.upper())

    # Apply date range filter if dates are provided
    if date_from:
        appointments = appointments.filter(appointment_date__gte=date_from)
    if date_to:
        appointments = appointments.filter(appointment_date__lte=date_to)

    # Order appointments
    appointments = appointments.order_by('-appointment_date', '-created_at')

    # Prepare context with all possible statuses for filter dropdown
    context = {
        'appointments': appointments,
        'statuses': ['PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED'],
        'selected_status': status_filter,
        'date_from': date_from,
        'date_to': date_to
    }
    
    return render(request, 'doctor_appointments.html', context)


@login_required
@user_passes_test(is_doctor)
def doctor_patients(request):
    try:
        doctor = request.user.doctor
    except Exception as e:
        messages.error(request, "No doctor profile associated with this account.")
        return render(request, 'doctor_patients.html', {'error': 'No doctor profile found'})

    # Get patients who have appointments with this doctor
    from apps.patientpro.models import Patient, Appointment
    patient_ids = Appointment.objects.filter(doctor=doctor).values_list('user_id', flat=True).distinct()
    
    # Fetch patient details
    patient_details = Patient.objects.filter(user_id__in=patient_ids)

    context = {
        'patients': patient_details
    }
    
    return render(request, 'doctor_patients.html', context)

@login_required
@user_passes_test(is_doctor)
def view_patient_details(request, patient_id):
    from apps.patientpro.models import Patient, Appointment
    
    try:
        doctor = request.user.doctor
        patient = Patient.objects.get(id=patient_id)
        
        # Get patient's appointments with this doctor
        patient_appointments = Appointment.objects.filter(
            user=patient.user, 
            doctor=doctor
        ).order_by('-appointment_date')
        
        context = {
            'patient': patient,
            'appointments': patient_appointments
        }
        
        return render(request, 'doctor_patient_details.html', context)
    
    except Patient.DoesNotExist:
        messages.error(request, "Patient not found.")
        return redirect('doctor_patients')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('doctor_patients')
    


def hospital_docs(request):
    # Get all doctors
    doctors = Doctor.objects.all()
    
    # Filter by specialization if provided
    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    # Prepare context with specialization choices
    context = {
        'doctors': doctors,
        'specialization_choices': Doctor.SPECIALIZATION_CHOICES,
        'selected_specialization': specialization
    }
    
    return render(request, 'hospital_docs.html', context)