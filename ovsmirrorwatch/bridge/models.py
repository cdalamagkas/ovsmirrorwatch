from django.db import models
from manager.models import OVSManager

# Create your models here.
class OVSBridge(models.Model):
    ovs_name = models.CharField(max_length=20)
    friendly_name = models.CharField(max_length=20)
    ovsdb_manager = models.ForeignKey(OVSManager, on_delete=models.SET_NULL, null=True)
    description = models.TextField(default=None, null=True)

    def __str__(self):
        return self.ovs_name + " (" + self.friendly_name + ")"
