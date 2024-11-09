from django.db import models

# Create your models here.
class OVSBridge(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    description = models.TextField()

