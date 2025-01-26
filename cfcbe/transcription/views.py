from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Transcription
from .serializers import TranscriptionSerializer
import whisper
import os
import torch
from jiwer import wer

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
    """
    API to transcribe audio, calculate WER, and save the result.
    """
    # Validate audio file
    if "audio_file" not in request.FILES:
        return Response({"error": "No audio file provided"}, status=400)

    # Validate true transcription
    true_transcription = request.data.get("true_transcription", "")
    if not true_transcription:
        return Response({"error": "No true transcription provided"}, status=400)

    # Save the uploaded audio file
    audio_instance = Transcription(
        audio_file=request.FILES["audio_file"],
        true_transcription=true_transcription
    )
    audio_instance.save()

    # Get the full file path of the uploaded file
    file_path = audio_instance.audio_file.path

    # Transcribe the audio using Whisper
    try:
        result = model.transcribe(file_path)
        model_transcription = result["text"]

        # Calculate Word Error Rate (WER)
        error_rate = wer(true_transcription, model_transcription)

        # Save the model transcription and WER to the database
        audio_instance.model_transcription = model_transcription
        audio_instance.wer = error_rate
        audio_instance.save()

        # Return the transcription and WER
        return Response({
            "model_transcription": model_transcription,
            "wer": error_rate
        })

    except Exception as e:
        # Handle transcription errors
        return Response({"error": str(e)}, status=500)