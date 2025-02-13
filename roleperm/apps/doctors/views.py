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
    # Debug: Print user information
    print(f"Current User: {request.user}")
    print(f"User ID: {request.user.id}")
    print(f"Username: {request.user.username}")

    try:
        # Debug: Verify doctor profile exists
        doctor = request.user.doctor
        print(f"Doctor Object: {doctor}")
        print(f"Doctor ID: {doctor.id}")
    except Exception as e:
        # Critical error if doctor profile doesn't exist
        print(f"ERROR: No doctor profile found for user {request.user.username}")
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

    # Get appointments for the current doctor with extensive logging
    try:
        appointments = Appointment.objects.filter(
            doctor=doctor
        ).select_related(
            'user', 'time_slot'
        ).order_by('-appointment_date', '-created_at')

        # Debug: Print appointment details
        print(f"Total Appointments: {appointments.count()}")
        for appt in appointments:
            print(f"Appointment Details:")
            print(f"  ID: {appt.id}")
            print(f"  Patient: {appt.user.username}")
            print(f"  Date: {appt.appointment_date}")
            print(f"  Status: {appt.status}")
        
        # Group appointments by status
        pending_appointments = appointments.filter(status='PENDING')
        confirmed_appointments = appointments.filter(status='CONFIRMED')
        cancelled_appointments = appointments.filter(status='CANCELLED')
        completed_appointments = appointments.filter(status='COMPLETED')

        # Debug: Print count of appointments in each status
        print(f"Pending Appointments: {pending_appointments.count()}")
        print(f"Confirmed Appointments: {confirmed_appointments.count()}")
        print(f"Cancelled Appointments: {cancelled_appointments.count()}")
        print(f"Completed Appointments: {completed_appointments.count()}")
        
        context = {
            'pending_appointments': pending_appointments,
            'confirmed_appointments': confirmed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'completed_appointments': completed_appointments,
        }
        
        return render(request, 'doctor_appointments.html', context)

    except Exception as e:
        # Catch and log any unexpected errors
        print(f"UNEXPECTED ERROR: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, 'doctor_appointments.html', {'error': str(e)})