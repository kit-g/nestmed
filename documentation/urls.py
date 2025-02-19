from django.urls import path
from .views import home, TranscriptListCreateView
from .api_views import process_transcript

urlpatterns = [
    path('', home, name='home'),
    path('api/transcripts/', process_transcript, name='api-transcripts'),
    path('api/transcripts/', TranscriptListCreateView.as_view(), name='transcripts-list-create'),
]
