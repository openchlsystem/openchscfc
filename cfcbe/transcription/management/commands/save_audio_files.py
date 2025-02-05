import os
from django.core.files import File
from django.core.management.base import BaseCommand
from transcription.models import AudioFile

class Command(BaseCommand):
    help = "Save audio files to the FileField"

    def add_arguments(self, parser):
        parser.add_argument("directory", type=str, help="The directory containing audio files to save.")

    def handle(self, *args, **kwargs):
        directory = kwargs["directory"]

        if not os.path.isdir(directory):
            self.stderr.write(self.style.ERROR(f"Directory not found: {directory}"))
            return

        for filename in os.listdir(directory):
            if filename.endswith(".wav"):
                file_path = os.path.join(directory, filename)
                unique_id = os.path.splitext(filename)[0]  # Extract filename without extension

                try:
                    # ✅ Check if the file already exists
                    audio_file_instance, created = AudioFile.objects.get_or_create(unique_id=unique_id)

                    # ✅ Save the file to the FileField (filesystem)
                    with open(file_path, "rb") as f:
                        django_file = File(f)
                        audio_file_instance.audio_file.save(filename, django_file, save=True)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"🎵 New audio file saved: {filename}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"✅ Using existing audio file: {filename}"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ Error saving file {filename}: {e}"))

        self.stdout.write(self.style.SUCCESS("✅ All audio files processed successfully."))
