from rest_framework import serializers
from .models import OVSMirror

class MirrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = OVSMirror
        fields = "__all__"
