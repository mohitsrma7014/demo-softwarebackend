from rest_framework import serializers
from .models import dispatch

class DispatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = dispatch
        fields = '__all__'  # Include all fields from the model