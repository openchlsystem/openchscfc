from django.urls import path
from .views import transcribe_audio
from .views import transcribe_audio, CaseRecordListCreateView, CaseRecordRetrieveUpdateDestroyView

urlpatterns = [
    path("transcribe/", transcribe_audio, name="transcribe_audio"),
    path('caserecords', CaseRecordListCreateView.as_view(), name='caserecords'),
    path('caserecords/<int:pk>', CaseRecordRetrieveUpdateDestroyView.as_view(), name='caserecord'),
]
