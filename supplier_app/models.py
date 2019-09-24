from django.db import models
from django.core.validators import FileExtensionValidator


class PDFFile(models.Model):
    pdf_file = models.FileField(
        upload_to='cuil',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
