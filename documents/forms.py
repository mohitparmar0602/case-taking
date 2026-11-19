from django import forms
from .models import PatientDocument


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = PatientDocument
        fields = ['title', 'document_type', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CBC Lab Report / Chest X-Ray'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes regarding this clinical document...'}),
        }
