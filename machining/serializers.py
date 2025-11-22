from rest_framework import serializers
from .models import machining

class MachiningSerializer(serializers.ModelSerializer):

    class Meta:
        model = machining
        fields = '__all__'