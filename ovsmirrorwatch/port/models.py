from django.db import models
from bridge.models import OVSBridge

# Create your models here.
class OVSPort(models.Model):
    ovs_name = models.CharField(max_length=30, primary_key=True)
    friendly_name = models.CharField(max_length=30)
    bridge = models.ForeignKey(OVSBridge, on_delete=models.CASCADE)
    description = models.TextField(default=None, null=True)