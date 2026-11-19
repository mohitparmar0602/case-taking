from django.db import models


class InstitutionSettings(models.Model):
    name = models.CharField(max_length=200, default="Apex Institute of Medical Sciences & Research")
    tagline = models.CharField(max_length=255, default="Smart India Hackathon 2026 | PS ID: SIH26047 - Patient Case-Taking Software")
    code = models.CharField(max_length=20, default="AIMS-26")
    patient_id_prefix = models.CharField(max_length=10, default="PAT")
    email = models.EmailField(default="contact@aims-hospital.in")
    phone = models.CharField(max_length=30, default="+91 11 2658 8500")
    emergency_helpline = models.CharField(max_length=30, default="108 / 102")
    address = models.TextField(default="Ansari Nagar, Ring Road")
    city = models.CharField(max_length=100, default="New Delhi")
    state = models.CharField(max_length=100, default="Delhi")
    postal_code = models.CharField(max_length=20, default="110029")
    website = models.URLField(blank=True, default="https://sih.gov.in")
    logo = models.ImageField(upload_to='institution/', blank=True, null=True)
    default_follow_up_days = models.PositiveIntegerField(default=7)
    enable_audit_trail = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Institution Settings"
        verbose_name_plural = "Institution Settings"

    def __str__(self):
        return self.name

    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(id=1)
        return settings
