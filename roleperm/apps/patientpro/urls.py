# urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient-list/', views.list_patient, name='patient_list'),
    path("create_patient/", views.create_patient, name="create_patient"),
    path('view/<int:id>/', views.view_patient, name='view_patient'),
    path('edit/<int:id>/', views.edit_patient, name='edit_patient'),
    path('delete/<int:id>/', views.delete_patient, name='delete_patient'),
    path('patient_profile/<int:id>/',views.profile_patients,name = 'profile_patients'),
    
    # Appointment URLs
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointment, name='my_appointments'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('get-available-slots/<int:doctor_id>/<str:date>/', views.get_available_slots, name='get_available_slots'),
]
