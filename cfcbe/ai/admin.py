from django.contrib import admin
from .models import AudioFile, ModelVersion, ModelTranscription

@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'feature_text', 'narrative')
    search_fields = ('file_name', 'feature_text')

@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ('version',)
    search_fields = ('version',)

# @admin.register(ModelTranscription)
# class ModelTranscriptionAdmin(admin.ModelAdmin):
#     list_display = ('model_version', 'predicted_text', 'wer')
#     search_fields = ('model_version')
