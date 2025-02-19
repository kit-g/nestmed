from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Transcript
from .serializers import TranscriptSerializer


@api_view(['POST'])
def process_transcript(request):
    serializer = TranscriptSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
