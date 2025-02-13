from django.shortcuts import render

from apps.accounts.decorator import allowed_users
from apps.doctors.models import Doctor
from apps.patientpro.models import Appointment, Patient

# Create your views here.
@allowed_users(allowed_roles=['Admin'])
def admin_dashboard(request):
    context = {}
    doc_count = Doctor.objects.all().count()
    patient_count = Patient.objects.all().count()
    appo_count = Appointment.objects.all().count()
    context.update({'doc_count':doc_count})
    context.update({'patient_count':patient_count})
    context.update({'appointment':appo_count})
    return render(request,"admin_dashboard.html",context)