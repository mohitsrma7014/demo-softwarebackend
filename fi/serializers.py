# serializers.py

from rest_framework import serializers
from .models import Fi

class FiSerializer(serializers.ModelSerializer):

    class Meta:
        model = Fi
        fields = '__all__'
