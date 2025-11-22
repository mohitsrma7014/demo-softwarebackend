# serializers.py

from rest_framework import serializers
from .models import HeatTreatment

class HeatTreatmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = HeatTreatment
        fields = '__all__'
