from django.db import models
from bridge.models import OVSBridge
from port.models import OVSPort

# Create your models here.
class OVSMirror(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    src_ports = models.ManyToManyField(OVSPort, related_name='src_ports_mirror')
    dst_ports = models.ManyToManyField(OVSPort, related_name='dst_ports_mirror')
    out_port = models.ForeignKey(OVSPort, on_delete=models.SET_NULL, null=True)
    health = models.BooleanField(default=None, null=True)
    description = models.TextField()

    def __str__(self):
        return self.name