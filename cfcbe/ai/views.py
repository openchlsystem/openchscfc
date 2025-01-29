import os
from django.http import HttpResponseBadRequest, JsonResponse
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import IntegrityError, transaction
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
        # Sanitize and validate file name
        file_name = os.path.basename(audio_file.name).strip()
        if not file_name:
            return HttpResponseBadRequest("Invalid file name")
        
        # Check for existing file with the same name
        if AudioFile.objects.filter(file_name=file_name).exists():
            return HttpResponseBadRequest("File with this name already exists")
        
        try:
            # Read file content as binary
            audio_data = audio_file.read()
            
            # Create and save new audio file record
            new_audio = AudioFile(
                file_name=file_name,
                audio_file=audio_data
            )
            new_audio.save()
            
            return JsonResponse({
                'status': 'success',
                'id': new_audio.id,
                'file_name': new_audio.file_name
            }, status=201)
            
        except IntegrityError:
            # Handle race condition for duplicate file names
            return HttpResponseBadRequest("File with this name already exists")
        except Exception as e:
            return HttpResponseBadRequest(f"Error processing file: {str(e)}")


    
class ModelTranscriptionViewSet(viewsets.ModelViewSet):
    queryset = ModelTranscription.objects.all()
    serializer_class = ModelTranscriptionSerializer

class ModelVersionViewSet(viewsets.ModelViewSet):
    queryset = ModelVersion.objects.all()
    serializer_class = ModelVersionSerializer
