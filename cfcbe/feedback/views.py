from rest_framework import generics, permissions
from .models import (
   Category, Complaint, AudioFile, Translation,
    Feedback, Metric, TriageLog, CaseworkerAction, Notification
)
from .serializers import *
# MyUser Views

# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Complaint Views
class ComplaintListCreateView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ComplaintDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    # permission_classes = [permissions.IsAuthenticated]

# Audio File Views
class AudioFileListCreateView(generics.ListCreateAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    # permission_classes = [permissions.IsAuthenticated]


class AudioFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    # permission_classes = [permissions.IsAuthenticated]

# Translation Views
class TranslationListCreateView(generics.ListCreateAPIView):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    # permission_classes = [permissions.IsAuthenticated]


class TranslationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    # permission_classes = [permissions.IsAuthenticated]

# Feedback Views
class FeedbackListCreateView(generics.ListCreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    # permission_classes = [permissions.IsAuthenticated]


class FeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    # permission_classes = [permissions.IsAuthenticated]

# Metric Views
class MetricListCreateView(generics.ListCreateAPIView):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    # permission_classes = [permissions.IsAuthenticated]


class MetricDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    # permission_classes = [permissions.IsAuthenticated]

# Triage Log Views
class TriageLogListCreateView(generics.ListCreateAPIView):
    queryset = TriageLog.objects.all()
    serializer_class = TriageLogSerializer
    # permission_classes = [permissions.IsAuthenticated]


class TriageLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TriageLog.objects.all()
    serializer_class = TriageLogSerializer
    # permission_classes = [permissions.IsAuthenticated]

# Caseworker Action Views
class CaseworkerActionListCreateView(generics.ListCreateAPIView):
    queryset = CaseworkerAction.objects.all()
    serializer_class = CaseworkerActionSerializer
    # permission_classes = [permissions.IsAuthenticated]


class CaseworkerActionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CaseworkerAction.objects.all()
    serializer_class = CaseworkerActionSerializer
    # permission_classes = [permissions.IsAuthenticated]

# Notification Views
class NotificationListCreateView(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes = [permissions.IsAuthenticated]


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes = [permissions.IsAuthenticated]
