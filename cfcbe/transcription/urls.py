from django.urls import path
from .views import transcribe_audio
from .views import transcribe_audio, AudioFileListCreateView, TranscriptionListCreateView, TranscriptionRetrieveUpdateDestroyView, CaseRecordListCreateView, CaseRecordRetrieveUpdateDestroyView

urlpatterns = [
    path("transcribe/", transcribe_audio, name="transcribe_audio"),
    
    
    # AudioFile API
    path('audio-files/', AudioFileListCreateView.as_view(), name='audio-file-list-create'),

    # Transcription API
    path('transcriptions/', TranscriptionListCreateView.as_view(), name='transcription-list-create'),
    path('transcriptions/<int:pk>/', TranscriptionRetrieveUpdateDestroyView.as_view(), name='transcription-detail'),

    # CaseRecord API
    path('case-records/', CaseRecordListCreateView.as_view(), name='case-record-list-create'),
    path('case-records/<int:pk>/', CaseRecordRetrieveUpdateDestroyView.as_view(), name='case-record-detail'),
    

]
