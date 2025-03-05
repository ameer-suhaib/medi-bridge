from django.urls import path
from . import views

urlpatterns = [
    path("doc_listing/",views.listing_doc,name="doc_listing"),
    path("create_doc/",views.create_doc,name="create_doc"),
    path('view/<int:id>/', views.view_doctor, name='view_doctor'),
    path('edit/<int:id>/', views.edit_doctor, name='edit_doctor'),
    path('delete/<int:id>/', views.delete_doctor, name='delete_doctor'),
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('manage_slots/', views.manage_slot, name='manage_slots'),
    path('edit_slot/<int:slot_id>/', views.edit_slot, name='edit_slot'),
    path('delete_slot/<int:slot_id>/', views.delete_slot, name='delete_slot'),
    path('doc_profile/<int:id>/', views.doc_profile, name='doc_profile'),
    path('appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('my-patients/', views.doctor_patients, name='doctor_patients'),
    path('patient-details/<int:patient_id>/', views.view_patient_details, name='doctor_patient_details'),
    path('hospital_docs/', views.hospital_docs, name='hospital_docs'),


]