from rest_framework import serializers
from .models import OVSManager

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OVSManager
        fields = "__all__"
