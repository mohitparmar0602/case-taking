from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('staff/', views.staff_list_view, name='staff_list'),
    path('staff/create/', views.staff_create_view, name='staff_create'),
    path('staff/<int:pk>/edit/', views.staff_edit_view, name='staff_edit'),
    path('staff/<int:pk>/toggle/', views.staff_toggle_status_view, name='staff_toggle'),
]
