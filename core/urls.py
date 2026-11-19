from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('clinical-care/', views.clinical_care_view, name='clinical_care'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    path('dashboard/', views.dashboard_router, name='dashboard'),
    path('dashboard/router/', views.dashboard_router, name='dashboard_router'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/receptionist/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('dashboard/nurse/', views.nurse_dashboard, name='nurse_dashboard'),
    path('settings/', views.institution_settings_view, name='settings'),
    path('unauthorized/', views.unauthorized_view, name='unauthorized'),
]
