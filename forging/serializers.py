from rest_framework import serializers
from .models import Forging

class ForgingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forging
        fields = '__all__'

