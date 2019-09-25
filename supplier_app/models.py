from django.db import models
from django.core.validators import FileExtensionValidator


class PDFFile(models.Model):
    pdf_file_received = models.DateTimeField(auto_now=True)
    pdf_file = models.FileField(
        upload_to='file',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
