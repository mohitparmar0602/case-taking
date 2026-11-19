from django.urls import path, re_path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list_view, name='patient_list'),
    path('register/', views.patient_create_view, name='patient_create'),
    path('<int:pk>/', views.patient_detail_view, name='patient_detail'),
    path('<int:pk>/edit/', views.patient_update_view, name='patient_update'),
    path('pid/<slug:pid>/', views.patient_detail_by_pid_view, name='patient_detail_by_pid'),
    path('blood-group/<str:group>/', views.patients_by_blood_group_view, name='patient_by_blood_group'),
    path('api/search/', views.patient_search_api_view, name='patient_search_api'),
    re_path(r'^lookup/(?P<pid>[A-Z]{3}-\d{4}-\d{4,5})/$', views.patient_detail_by_pid_view, name='patient_regex_lookup'),
]
