import boto3
from django.shortcuts import render, redirect

from nestmed import settings
from .models import Transcript
from .forms import TranscriptForm
from rest_framework import generics
from .serializers import TranscriptSerializer

s3 = boto3.client('s3')


def home(request):
    if request.method == "POST":
        form = TranscriptForm(request.POST, request.FILES)
        if form.is_valid():
            transcript = form.save()

            audio_file_path = transcript.audio_file.path
            s3_key = f"audio/{transcript.id}.mp3"
            s3.upload_file(audio_file_path, settings.TRANSCRIPTS_BUCKET, s3_key)

            tags = {
                'TagSet': [
                    {
                        'Key': 'transcript_id',
                        'Value': str(transcript.id)
                    }
                ]
            }

            s3.put_object_tagging(
                Bucket=settings.TRANSCRIPTS_BUCKET,
                Key=s3_key,
                Tagging=tags
            )

            return redirect('home')
    else:
        form = TranscriptForm()

    transcripts = Transcript.objects.all()
    return render(
        request,
        'documentation/home.html',
        {'form': form, 'transcripts': transcripts}
    )


class TranscriptListCreateView(generics.ListCreateAPIView):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
