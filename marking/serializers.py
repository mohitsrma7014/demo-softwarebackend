# serializers.py

from rest_framework import serializers
from .models import marking

class MarkingSerializer(serializers.ModelSerializer):

    class Meta:
        model = marking
        fields = '__all__'
