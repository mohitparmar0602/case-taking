from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list_view, name='appointment_list'),
    path('book/', views.appointment_book_view, name='appointment_book'),
    path('schedule/', views.appointment_schedule_view, name='appointment_schedule'),
    path('status/<str:status>/', views.appointment_by_status_view, name='appointment_by_status'),
    path('<int:pk>/edit/', views.appointment_edit_view, name='appointment_edit'),
    path('<int:pk>/cancel/', views.appointment_cancel_view, name='appointment_cancel'),
]
