from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ModelTranscription, CaseRecord
import whisper
import os
from jiwer import wer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Transcription, CaseRecord, AudioFile
from .serializers import TranscriptionSerializer, CaseRecordSerializer, AudioFileSerializer

import ssl
from rest_framework import generics
from .serializers import CaseRecordSerializer
ssl._create_default_https_context = ssl._create_unverified_context

# Change this to "tiny", "small", "medium", or "large" as needed
MODEL_SIZE = "tiny"

# Manually specify the model path
CACHE_DIR = os.path.expanduser("~/.cache/whisper/")
MODEL_PATH = os.path.join(CACHE_DIR, f"whisper-{MODEL_SIZE}.pt")

# ✅ Check if model exists in cache before downloading
if not os.path.exists(MODEL_PATH):
    print(f"🔍 Model not found in cache: {MODEL_PATH}. Downloading...")
model = whisper.load_model(MODEL_SIZE, download_root=CACHE_DIR)


@api_view(["POST"])
def transcribe_audio(request):
    """
    API to transcribe audio, calculate WER, and save the result.
    """
    # Validate audio file
    if "audio_file" not in request.FILES:
        return Response({"error": "No audio file provided"}, status=400)

    # Make true_transcription optional
    true_transcription = request.data.get("true_transcription", None)

    # Save the uploaded audio file
    audio_instance = ModelTranscription(
        audio_file=request.FILES["audio_file"],
    )
    audio_instance.save()

    # Get the full file path of the uploaded file
    file_path = audio_instance.audio_file.path

    # ✅ Transcribe the audio using Whisper
    try:
        result = model.transcribe(file_path)  # Use `model`, not `MODEL_PATH`
        model_transcription = result["text"]

        # ✅ Calculate Word Error Rate (WER) only if true transcription is provided
        error_rate = wer(true_transcription, model_transcription) if true_transcription else None

        # Save the model transcription and WER to the database
        audio_instance.model_transcription = model_transcription
        audio_instance.wer = error_rate
        audio_instance.save()

        # ✅ Return the transcription and WER (if available)
        response_data = {
            "model_transcription": model_transcription
        }
        if error_rate is not None:
            response_data["wer"] = error_rate

        return Response(response_data)

    except Exception as e:
        # Handle transcription errors
        return Response({"error": str(e)}, status=500)



# Generic view for AudioFile Model (List and Create)
class AudioFileListCreateView(generics.ListCreateAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    #permission_classes = [IsAuthenticated]  # Adjust permissions as needed

# Generic view for Transcription Model (List, Create, Retrieve, Update, Destroy)
class TranscriptionListCreateView(generics.ListCreateAPIView):
    queryset = Transcription.objects.all()
    serializer_class = TranscriptionSerializer
    #permission_classes = [IsAuthenticated]  # Adjust permissions as needed

class TranscriptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transcription.objects.all()
    serializer_class = TranscriptionSerializer
    #permission_classes = [IsAuthenticated]  # Adjust permissions as needed

# Generic view for CaseRecord Model (List, Create, Retrieve, Update, Destroy)
class CaseRecordListCreateView(generics.ListCreateAPIView):
    queryset = CaseRecord.objects.all()
    serializer_class = CaseRecordSerializer
    #permission_classes = [IsAuthenticated]  # Adjust permissions as needed

class CaseRecordRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CaseRecord.objects.all()
    serializer_class = CaseRecordSerializer
    #permission_classes = [IsAuthenticated]  # Adjust permissions as needed


