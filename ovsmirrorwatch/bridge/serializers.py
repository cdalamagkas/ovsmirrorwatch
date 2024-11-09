from rest_framework import serializers
from .models import OVSBridge

class BridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OVSBridge
        fields = "__all__"
