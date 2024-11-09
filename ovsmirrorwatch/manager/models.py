from django.db import models

# Create your models here.
class OVSManager(models.Model):
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(default=6640)
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(default='')
    monitor = models.BooleanField(default=False)