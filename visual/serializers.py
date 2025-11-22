# serializers.py

from rest_framework import serializers
from .models import Visual

class VisualSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visual
        fields = '__all__'
