# serializers.py

from rest_framework import serializers
from .models import pre_mc

class pre_mcSerializer(serializers.ModelSerializer):
    class Meta:
        model = pre_mc
        fields = '__all__'
