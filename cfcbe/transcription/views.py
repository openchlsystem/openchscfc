from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Transcription
from .serializers import TranscriptionSerializer
import whisper
import os
import torch

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


# # Load Whisper model without downloading
# MODEL_PATH = os.path.expanduser("~/.cache/whisper/whisper-small.pt")
# model = whisper.load_model("small", download_root=os.path.dirname(MODEL_PATH), in_memory=False)

# Manually specify the model path
# MODEL_PATH = os.path.expanduser("~/.cache/whisper/whisper-small.pt")

# Load the model from the local file
model = whisper.load_model("turbo", device="cuda" if torch.cuda.is_available() else "cpu")


@api_view(["POST"])
def transcribe_audio(request):
    if "audio_file" not in request.FILES:
        return Response({"error": "No audio file provided"}, status=400)

    # Save the uploaded file
    audio_instance = Transcription(audio_file=request.FILES["audio_file"])
    audio_instance.save()

    # Get the full file path
    file_path = audio_instance.audio_file.path

    # Transcribe the audio
    result = model.transcribe(file_path)
    transcript_text = result["text"]

    # Save the transcript
    audio_instance.transcript = transcript_text
    audio_instance.save()

    return Response({"transcript": transcript_text})
