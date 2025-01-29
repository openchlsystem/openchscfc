import os
from django.core.management.base import BaseCommand
from transcription.models import AudioFile

class Command(BaseCommand):
    help = 'Save audio files as binary data in the AudioFile model'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='The directory containing audio files to save.')

    def handle(self, *args, **kwargs):
        directory = kwargs['directory']

        if not os.path.isdir(directory):
            self.stderr.write(self.style.ERROR(f"Directory not found: {directory}"))
            return

        for filename in os.listdir(directory):
            if filename.endswith('.wav'):
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, 'rb') as audio_file:
                        audio_data = audio_file.read()

                    unique_id = os.path.splitext(filename)[0]  # Use the filename (without extension) as unique_id

                    # Save the audio file to the database
                    audio_file_instance = AudioFile(unique_id=unique_id, audio_file=audio_data)
                    audio_file_instance.save()

                    self.stdout.write(self.style.SUCCESS(f"Saved audio file: {filename}"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error saving file {filename}: {e}"))

        self.stdout.write(self.style.SUCCESS("All audio files have been processed."))
