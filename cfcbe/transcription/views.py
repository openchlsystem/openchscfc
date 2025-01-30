import io
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ModelTranscription, CaseRecord, AudioFile, ModelVersion
import whisper
import os
from jiwer import wer
from rest_framework import generics
from .models import ModelTranscription, CaseRecord, AudioFile
from .serializers import (
    ModelTranscriptionSerializer,
    CaseRecordSerializer,
    AudioFileSerializer,
)

import ssl
from rest_framework import generics
from .serializers import CaseRecordSerializer

ssl._create_default_https_context = ssl._create_unverified_context

# Change this to "tiny", "small", "medium", or "large" as needed
MODEL_SIZE = "tiny"

# Manually specify the model path
CACHE_DIR = os.path.expanduser("~/.cache/whisper/")
MODEL_PATH = os.path.join(CACHE_DIR, f"{MODEL_SIZE}.pt")

if os.path.exists(os.path.expanduser("~/.cache/whisper/large-v3-turbo.pt")):
    print("turbo model found 🔍")
    MODEL_SIZE = "large-v3-turbo"

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
    # Process audio file
    audio_file_obj = process_audio_file(request.FILES["audio_file"])

    # Extract unique_id from the filename
    unique_id = os.path.splitext(request.FILES["audio_file"].name)[0]

    # Check if an AudioFile with the same unique_id already exists
    audio_instance, created = AudioFile.objects.get_or_create(
        unique_id=unique_id,
        defaults={"audio_file": request.FILES["audio_file"]},  # Saves only if new
    )

    # If the file already exists, use the existing record
    if not created:
        print(f"✅ Using existing AudioFile: {audio_instance.unique_id}")
    else:
        print(f"🎵 New AudioFile saved: {audio_instance.unique_id}")

    # Get or create the latest model version
    latest_model, _ = ModelVersion.objects.get_or_create(version="version_1")

    # Get the full file path
    file_path = audio_instance.audio_file.path
    try:
        # Transcribe audio using Whisper
        model_transcription = transcribe_audio_file(file_path)

        error_rate = (
            wer(true_transcription, model_transcription) if true_transcription else None
        )

        # Save the transcription result
        ModelTranscription.objects.create(
            audio_id=audio_instance,
            model_version_id=latest_model,
            predicted_text=model_transcription,
            wer=error_rate if error_rate is not None else 0.0,
        )

        # ✅ Return the transcription and WER (if available)
        response_data = {"model_transcription": model_transcription}
        if error_rate is not None:
            response_data["wer"] = error_rate

        return Response(response_data)

    except Exception as e:
        # Handle transcription errors
        return Response({"error": str(e)}, status=500)


# Function to handle different audio formats and convert to required format
def process_audio_file(audio_file):
    """
    Converts the uploaded audio file to a format required by the model.
    """
    if not audio_file:
        raise ValueError("No audio file provided")

    # Read file content into bytes
    audio_binary = audio_file.read()
    if not audio_binary:
        raise ValueError("Uploaded file is empty")

    # Convert bytes to a file-like object
    return io.BytesIO(audio_binary)


# Function to transcribe audio using Whisper
def transcribe_audio_file(audio_file_obj):
    """
    Transcribes an audio file using the Whisper model.
    """
    try:
        result = model.transcribe(audio_file_obj, language="swahili")
        predicted_text = result["text"]
    except Exception as e:
        raise Exception(f"Whisper transcription error: {str(e)}")

    return predicted_text


# Generic view for AudioFile Model (List and Create)
class AudioFileListCreateView(generics.ListCreateAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    # permission_classes = [IsAuthenticated]  # Adjust permissions as needed


# Generic view for Transcription Model (List, Create, Retrieve, Update, Destroy)
class TranscriptionListCreateView(generics.ListCreateAPIView):
    queryset = ModelTranscription.objects.all()
    serializer_class = ModelTranscriptionSerializer
    # permission_classes = [IsAuthenticated]  # Adjust permissions as needed


class TranscriptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ModelTranscription.objects.all()
    serializer_class = ModelTranscriptionSerializer
    # permission_classes = [IsAuthenticated]  # Adjust permissions as needed


# Generic view for CaseRecord Model (List, Create, Retrieve, Update, Destroy)
class CaseRecordListCreateView(generics.ListCreateAPIView):
    queryset = CaseRecord.objects.all()
    serializer_class = CaseRecordSerializer
    # permission_classes = [IsAuthenticated]  # Adjust permissions as needed


class CaseRecordRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CaseRecord.objects.all()
    serializer_class = CaseRecordSerializer
    # permission_classes = [IsAuthenticated]  # Adjust permissions as needed
