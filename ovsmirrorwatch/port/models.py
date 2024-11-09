from django.db import models
from bridge.models import OVSBridge

# Create your models here.
class OVSPort(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    bridge = models.ForeignKey(OVSBridge, on_delete=models.CASCADE)
    description = models.TextField()