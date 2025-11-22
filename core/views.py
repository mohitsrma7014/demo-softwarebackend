from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserSerializer(request.user)
    data= serializer.data
    print(data)
    return Response(serializer.data)
