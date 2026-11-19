from django.urls import path, re_path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('', views.consultation_list_view, name='consultation_list'),
    path('start/', views.consultation_create_view, name='consultation_create'),
    path('<int:pk>/', views.consultation_detail_view, name='consultation_detail'),
    path('<int:pk>/edit/', views.consultation_edit_view, name='consultation_edit'),
    path('<int:pk>/finalize/', views.consultation_finalize_view, name='consultation_finalize'),
    path('<int:pk>/amend/', views.consultation_amend_view, name='consultation_amend'),
    path('<int:pk>/pdf/', views.consultation_pdf_view, name='consultation_pdf'),
    path('<int:pk>/print/', views.consultation_print_view, name='consultation_print'),
    re_path(r'^code/(?P<code>CON-\d{4}-\d{4,5})/$', views.consultation_detail_by_code_view, name='consultation_by_code'),
]
