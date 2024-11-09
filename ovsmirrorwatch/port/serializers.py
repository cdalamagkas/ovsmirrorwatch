from rest_framework import serializers
from .models import OVSPort

class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = OVSPort
        fields = "__all__"
