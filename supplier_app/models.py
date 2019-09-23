from django.db import models

class File(models.Model):
    file_date_received = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='cuil', blank=True)
