import os
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import AudioFile, ModelTranscription, ModelVersion, TriageRule, TriageAnalysis, Department, CaseHistory, ComplaintRouting, Complaint
from .serializers import (
    AudioFileSerializer,
    ModelTranscriptionSerializer,
    ModelVersionSerializer,
    TriageRuleSerializer,
    TriageAnalysisSerializer,
    DepartmentSerializer,
    CaseHistorySerializer,
    ComplaintRoutingSerializer,
    ComplaintSerializer
)

# TriageRule Views
class TriageRuleListCreateView(generics.ListCreateAPIView):
    queryset = TriageRule.objects.all()
    serializer_class = TriageRuleSerializer


class TriageRuleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TriageRule.objects.all()
    serializer_class = TriageRuleSerializer


# TriageAnalysis Views
class TriageAnalysisListCreateView(generics.ListCreateAPIView):
    queryset = TriageAnalysis.objects.all()
    serializer_class = TriageAnalysisSerializer


class TriageAnalysisRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TriageAnalysis.objects.all()
    serializer_class = TriageAnalysisSerializer


# Department Views
class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


# CaseHistory Views
class CaseHistoryListCreateView(generics.ListCreateAPIView):
    queryset = CaseHistory.objects.all()
    serializer_class = CaseHistorySerializer


class CaseHistoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CaseHistory.objects.all()
    serializer_class = CaseHistorySerializer


# ComplaintRouting Views
class ComplaintRoutingListCreateView(generics.ListCreateAPIView):
    queryset = ComplaintRouting.objects.all()
    serializer_class = ComplaintRoutingSerializer


class ComplaintRoutingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ComplaintRouting.objects.all()
    serializer_class = ComplaintRoutingSerializer


# Complaint Views
class ComplaintListCreateView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer


class ComplaintRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

class AudioFileViewSet(viewsets.ModelViewSet):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer

    @action(detail=False, methods=['post'])
    def upload_audio(self, request):
        """
        Endpoint for uploading an audio file. The file_name is extracted from the filename.
        If a file with the same file_name exists, it will be updated.
        """
        if 'audio_file' not in request.FILES:
            return Response({"error": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)

        audio_file = request.FILES['audio_file']
        file_name = os.path.splitext(audio_file.name)[0]  # Extract filename without extension

        # Ensure the audio file is read correctly
        audio_binary = audio_file.read()
        if not audio_binary:
            return Response({"error": "Uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to fetch an existing record
            audio_instance, created = AudioFile.objects.get_or_create(file_name=file_name)
            audio_instance.audio_file = audio_binary
            audio_instance.save()
        except Exception as e:
            return Response({"error": f"Database error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(AudioFileSerializer(audio_instance).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    
class ModelTranscriptionViewSet(viewsets.ModelViewSet):
    queryset = ModelTranscription.objects.all()
    serializer_class = ModelTranscriptionSerializer

class ModelVersionViewSet(viewsets.ModelViewSet):
    queryset = ModelVersion.objects.all()
    serializer_class = ModelVersionSerializer