from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    path('patient/<int:patient_id>/vitals/add/', views.record_vitals_view, name='record_vitals'),
    path('patient/<int:patient_id>/vitals/trends/', views.vitals_trends_view, name='vitals_trends'),
    path('patient/<int:patient_id>/history/add/', views.record_medical_history_view, name='record_history'),
    path('api/patient/<int:patient_id>/vitals/', views.vitals_json_api_view, name='vitals_api'),
]
