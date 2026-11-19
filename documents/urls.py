from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('patient/<int:patient_id>/upload/', views.document_upload_view, name='document_upload'),
    path('<int:pk>/download/', views.document_download_view, name='document_download'),
    path('<int:pk>/delete/', views.document_delete_view, name='document_delete'),
]
