import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages

from .models import PatientDocument
from .forms import DocumentUploadForm
from patients.models import Patient
from accounts.models import User
from accounts.permissions import clinical_staff_required
from audit.services import log_audit_event
from audit.models import AuditLog


@login_required
@clinical_staff_required
def document_upload_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.patient = patient
            doc.uploaded_by = request.user
            doc.save()

            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.DOCUMENT_UPLOAD,
                record_type="PatientDocument",
                record_id=str(doc.id),
                description=f"Uploaded {doc.get_document_type_display()} '{doc.title}' ({doc.file_size_display}) for patient {patient.patient_id}."
            )
            messages.success(request, f"Document '{doc.title}' uploaded successfully!")
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            messages.error(request, "Failed to upload document. Please ensure valid file type and size under 10 MB.")
    else:
        form = DocumentUploadForm()

    return render(request, 'documents/document_upload.html', {
        'form': form,
        'patient': patient,
    })


@login_required
def document_download_view(request, pk):
    """
    Secure document download endpoint:
    Verifies user permissions, logs access in audit trail, and serves the file securely.
    Receptionists cannot view restricted clinical test documents.
    """
    document = get_object_or_404(PatientDocument, pk=pk)

    # Receptionist restriction
    if request.user.role == User.Role.RECEPTIONIST:
        messages.error(request, "Reception staff are not authorized to download medical test records.")
        return redirect('core:unauthorized')

    file_path = document.file.path
    if not os.path.exists(file_path):
        raise Http404("Document file not found on server storage.")

    log_audit_event(
        request=request,
        user=request.user,
        action=AuditLog.Action.DOCUMENT_DOWNLOAD,
        record_type="PatientDocument",
        record_id=str(document.id),
        description=f"Downloaded document '{document.title}' for patient {document.patient.patient_id}."
    )

    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    return response


@login_required
def document_delete_view(request, pk):
    document = get_object_or_404(PatientDocument, pk=pk)
    patient = document.patient

    # Only Doctors, Admins, or the original uploader can delete
    if not (request.user.is_admin_user or request.user.role == User.Role.DOCTOR or document.uploaded_by == request.user):
        messages.error(request, "You do not have permission to delete this document.")
        return redirect('patients:patient_detail', pk=patient.pk)

    if request.method == 'POST':
        title = document.title
        doc_id = document.id
        # Delete file from storage
        try:
            if document.file and os.path.exists(document.file.path):
                os.remove(document.file.path)
        except Exception:
            pass

        document.delete()
        log_audit_event(
            request=request,
            user=request.user,
            action=AuditLog.Action.STAFF_UPDATE,
            record_type="PatientDocument",
            record_id=str(doc_id),
            description=f"Deleted document '{title}' for patient {patient.patient_id}."
        )
        messages.info(request, f"Document '{title}' deleted.")
        return redirect('patients:patient_detail', pk=patient.pk)

    return render(request, 'documents/document_confirm_delete.html', {
        'document': document,
        'patient': patient,
    })
