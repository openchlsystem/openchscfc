import os
import re
from django.core.files import File
from django.core.management.base import BaseCommand
from transcription.models import AudioFile, AudioFileChunk

class Command(BaseCommand):
    help = "Save audio file chunks to the FileField"

    def add_arguments(self, parser):
        parser.add_argument("directory", type=str, help="The directory containing chunked audio files.")

    def handle(self, *args, **kwargs):
        directory = kwargs["directory"]

        if not os.path.isdir(directory):
            self.stderr.write(self.style.ERROR(f"Directory not found: {directory}"))
            return

        for filename in sorted(os.listdir(directory)):  # Sort to maintain order
            if filename.endswith(".wav"):
                file_path = os.path.join(directory, filename)

                # ✅ Debug: Print filename before matching
                print(f"🔍 Checking filename: {filename}")

                # ✅ Try multiple regex formats
                match = re.match(r"^(?P<unique_id>[\d.]+)_chunk_(?P<order>\d+)\.wav$", filename)
                
                if match:
                    unique_id = match.group("unique_id")
                    chunk_order = int(match.group("order"))  # Convert chunk number to integer
                    print(f"✅ Matched! Unique ID: {unique_id}, Chunk Order: {chunk_order}")
                else:
                    print(f"❌ No match for filename: {filename}")
                    continue  # Skip this file

            try:
                # ✅ Find the parent `AudioFile`
                parent_audio = AudioFile.objects.filter(unique_id=unique_id).first()
                if not parent_audio:
                    self.stderr.write(self.style.ERROR(f"No matching AudioFile for {unique_id}, skipping {filename}"))
                    continue

                # ✅ Check if chunk already exists
                chunk_instance, created = AudioFileChunk.objects.get_or_create(
                    parent_audio=parent_audio,
                    order=chunk_order,
                    defaults={"chunk_file": file_path}  # ✅ Ensure chunk_file is set
                )

                # ✅ Open the file properly before saving
                with open(file_path, "rb") as f:
                    django_file = File(f)
                    
                    # ✅ Assign chunk_file correctly
                    chunk_instance.chunk_file.save(filename, django_file, save=True)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"🔹 New chunk saved: {filename}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Using existing chunk: {filename}"))

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.stderr.write(self.style.ERROR(f"❌ Error saving file {filename}: {e}\n{error_details}"))



        self.stdout.write(self.style.SUCCESS("✅ All audio chunks processed successfully."))
