from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard_view, name='dashboard'),
    path('export/patients/csv/', views.export_patients_csv, name='export_patients_csv'),
    path('export/consultations/csv/', views.export_consultations_csv, name='export_consultations_csv'),
    path('export/summary/pdf/', views.export_executive_summary_pdf, name='export_summary_pdf'),
]
