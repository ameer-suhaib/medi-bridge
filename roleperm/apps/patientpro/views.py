# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from .models import Appointment, Patient
from .forms import PatientForm, ProfileForm, UserForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.doctors.models import Doctor, TimeSlot
# from .models import Appointment
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from calendar import day_name

DEFAULT_PASS = 'Patient@123'


@login_required
def patient_dashboard(request):
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_date=timezone.now().date(),
    ).order_by('appointment_date')

    # Get completed appointments count
    completed_appointments_count = Appointment.objects.filter(
        user=request.user,
        status='COMPLETED'
    ).count()

    # Get unique doctors count
    doctors_count = Appointment.objects.filter(
        user=request.user
    ).values('doctor').distinct().count()

    context = {
        'upcoming_appointments': upcoming_appointments,
        'upcoming_appointments_count': upcoming_appointments.count(),
        'completed_appointments_count': completed_appointments_count,
        'doctors_count': doctors_count,
    }

    return render(request, "patient_dashboard.html", context)


def list_patient(request):
    patients = Patient.objects.all()
    return render(request, "patient_list.html", {"patients": patients})

@transaction.atomic
def create_patient(request):
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        user_form = UserForm(request.POST)

        if patient_form.is_valid() and user_form.is_valid():
            try:
                # Get cleaned form data
                user_data = user_form.cleaned_data
                username = user_data['username']
                email = user_data['email']

                # Check if username already exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists. Please choose a different username.')
                    return render(request, "create_patient.html", {
                        "patient": patient_form,
                        "user": user_form
                    })

                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=DEFAULT_PASS
                )

                patient_group, created = Group.objects.get_or_create(name="Patient")
                user.groups.add(patient_group)

                # Create patient profile
                patient = patient_form.save(commit=False)
                patient.user = user
                patient.save()

                messages.success(request, f'Patient {username} created successfully!')
                return redirect("patient_list")

            except Exception as e:
                messages.error(request, f'Error creating patient: {str(e)}')
        else:
            # Form validation errors
            for field, errors in patient_form.errors.items():
                for error in errors:
                    messages.error(request, f'Patient form error - {field}: {error}')
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f'User form error - {field}: {error}')
    else:
        patient_form = PatientForm()
        user_form = UserForm()

    return render(request, "create_patient.html", {
        "patient": patient_form,
        "user": user_form
    })

def view_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    return render(request, 'view_patient.html', {'patient': patient})

def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    user = patient.user

    if request.method == 'POST':
        patient_form = PatientForm(request.POST, instance=patient)
        if patient_form.is_valid():
            try:
                patient_form.save()
                messages.success(request, f'Patient {user.username} updated successfully!')
                return redirect('patient_list')
            except Exception as e:
                messages.error(request, f'Error updating patient: {str(e)}')
    else:
        patient_form = PatientForm(instance=patient)

    return render(request, 'edit_patient.html', {
        'form': patient_form,
        'patient': patient
    })

def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == 'POST':
        try:
            username = patient.user.username
            patient.user.delete()  # This will also delete the patient due to CASCADE
            messages.success(request, f'Patient {username} deleted successfully!')
            return redirect('patient_list')
        except Exception as e:
            messages.error(request, f'Error deleting patient: {str(e)}')
    return render(request, 'delete_patient.html', {'patient': patient})


@login_required
def book_appointment(request):
    if request.method == 'POST':
        try:
            # Log all POST data for debugging
            print("POST Data:", request.POST)

            # Get form data
            doctor_id = request.POST.get('doctor')
            time_slot_id = request.POST.get('time_slot')
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')
            appointment_date = request.POST.get('appointment_date')
            symptoms = request.POST.get('symptoms', '')

            # Detailed input validation
            if not doctor_id:
                messages.error(request, "Doctor selection is required.")
                return redirect('book_appointment')
            
            if not time_slot_id:
                messages.error(request, "Time slot selection is required.")
                return redirect('book_appointment')
            
            if not start_time_str or not end_time_str:
                messages.error(request, "Start and end times are required.")
                return redirect('book_appointment')
            
            if not appointment_date:
                messages.error(request, "Appointment date is required.")
                return redirect('book_appointment')

            # Convert inputs
            try:
                appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
                start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
                end_time = datetime.strptime(end_time_str, '%I:%M %p').time()
                
                print(f"Parsed Data:")
                print(f"Date: {appointment_date}")
                print(f"Start Time: {start_time}")
                print(f"End Time: {end_time}")
            except ValueError as e:
                print(f"Conversion Error: {e}")
                messages.error(request, f"Invalid date or time format: {str(e)}")
                return redirect('book_appointment')

            # Get doctor and time slot with detailed error handling
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                time_slot = TimeSlot.objects.get(id=time_slot_id, doctor=doctor)
                
                print(f"Doctor: {doctor}")
                print(f"Time Slot: {time_slot}")
            except Doctor.DoesNotExist:
                messages.error(request, "Selected doctor does not exist.")
                return redirect('book_appointment')
            except TimeSlot.DoesNotExist:
                messages.error(request, "Selected time slot is not available.")
                return redirect('book_appointment')

            # Check if slot is already booked
            existing_appointment = Appointment.objects.filter(
                doctor=doctor,
                time_slot=time_slot,
                appointment_date=appointment_date,
                start_time=start_time
            )

            if existing_appointment.exists():
                messages.error(request, "This time slot is already booked.")
                return redirect('book_appointment')

            # Create appointment with comprehensive error handling
            try:
                with transaction.atomic():
                    appointment = Appointment.objects.create(
                        user=request.user,
                        doctor=doctor,
                        time_slot=time_slot,
                        appointment_date=appointment_date,
                        start_time=start_time,
                        end_time=end_time,
                        symptoms=symptoms,
                        status='PENDING'
                    )
                    print(f"Appointment Created: {appointment}")
            except Exception as create_error:
                print(f"Appointment Creation Error: {create_error}")
                messages.error(request, f"Error creating appointment: {str(create_error)}")
                return redirect('book_appointment')

            messages.success(request, f"Appointment booked successfully with Dr. {doctor.user.get_full_name()} on {appointment_date} from {start_time} to {end_time}")
            return redirect('my_appointments')

        except Exception as e:
            print(f"Unexpected Error: {e}")
            messages.error(request, f"Unexpected error booking appointment: {str(e)}")
            return redirect('book_appointment')

    # GET request: render booking page
    doctors = Doctor.objects.all()
    return render(request, 'book_appointment.html', {'doctors': doctors})



def my_appointment(request):
    appointment = Appointment.objects.filter(user = request.user).select_related('doctor','time_slot')
    context = {
        'appointments':appointment,
        'today':timezone.now().date()
    }
    print(context.get('appointments'),":::aaaaaaaaaaa")
    return render(request,"my_appointments.html",context)


def cancel_appointment(request,appointment_id):
    appointment = get_object_or_404(Appointment,id=appointment_id,patient = request.user.patient)

    if appointment.status == 'Cancelled':
        messages.error(request,"Appointment alreay cancelled")
    elif appointment.appointment_date < timezone.now().date():
        messages.error(request,"Cannot Cancel ,Date is Passed")
    else:
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request,"Appointment cancelled success!!")

    return redirect('my_appointment')


def get_available_slots(request, doctor_id, date):
    try:
        # Validate inputs
        if not doctor_id or not date:
            return JsonResponse({
                'success': False, 
                'error': 'Doctor ID and Date are required'
            }, status=400)

        # Fetch doctor
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': f'Doctor with ID {doctor_id} not found'
            }, status=404)

        # Parse date
        try:
            appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False, 
                'error': f'Invalid date format: {date}'
            }, status=400)

        # Get day of week
        day_of_week = appointment_date.strftime('%A')

        # Fetch time slots
        time_slots = TimeSlot.objects.filter(
            doctor=doctor,
            day=day_of_week,
            is_available=True
        )

        if not time_slots.exists():
            return JsonResponse({
                'success': True, 
                'slots': [],
                'message': f'No available slots for {day_of_week}'
            })

        # Filter and process available slots
        available_slots = []
        for slot in time_slots:
            try:
                available_appointments = slot.get_available_appointments(date=appointment_date)
                
                if available_appointments > 0:
                    # Get detailed slot times
                    slot_times = slot.get_slot_times()
                    
                    for slot_time in slot_times:
                        available_slots.append({
                            'id': slot.id,
                            'start_time': slot_time['start'],
                            'end_time': slot_time['end'],
                            'available_slots': available_appointments,
                            'time_block': slot.time_block,
                            'slot_duration': slot.slot_duration
                        })

            except Exception as slot_error:
                print(f"Error processing slot {slot.id}: {str(slot_error)}")

        return JsonResponse({
            'success': True, 
            'slots': available_slots
        })

    except Exception as e:
        print(f"Unexpected error in get_available_slots: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': 'An unexpected error occurred'
        }, status=500)
#patient profile

def profile_patients(request,id):
    print(id,"iddddddddd")
    print("enterrrrrrrrrr")
    
    patient = get_object_or_404(Patient,user_id = id)
    user = patient.user
    print(user,"useeeeeeeee")
    if request.method == 'POST':
        print("POST data received:", request.POST)
        print("postt")
        profile_form = ProfileForm(request.POST,instance = patient)
        try:

            if profile_form.is_valid():
                print("validdddddddddd")
                profile_form.save()
                return redirect('patient_dashboard')
            else:
                print(profile_form.errors,"erroorrr")
        except Exception as err:
            messages.error(request, f'Error updating patient: {str(err)}')
    else:
        profile_form =  ProfileForm(instance = patient)
        return render(request,"patient_profile.html",{'form':profile_form,'user':user,'patient':patient})