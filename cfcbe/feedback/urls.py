from django.urls import path
from . import views

urlpatterns = [
  

    # Category URLs
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Complaint URLs
    path('complaints/', views.ComplaintListCreateView.as_view(), name='complaint-list-create'),
    path('complaints/<int:pk>/', views.ComplaintDetailView.as_view(), name='complaint-detail'),

    # Audio File URLs
    path('audio-files/', views.AudioFileListCreateView.as_view(), name='audiofile-list-create'),
    path('audio-files/<int:pk>/', views.AudioFileDetailView.as_view(), name='audiofile-detail'),

    # Translation URLs
    path('translations/', views.TranslationListCreateView.as_view(), name='translation-list-create'),
    path('translations/<int:pk>/', views.TranslationDetailView.as_view(), name='translation-detail'),

    # Feedback URLs
    path('feedback/', views.FeedbackListCreateView.as_view(), name='feedback-list-create'),
    path('feedback/<int:pk>/', views.FeedbackDetailView.as_view(), name='feedback-detail'),

    # Metric URLs
    path('metrics/', views.MetricListCreateView.as_view(), name='metric-list-create'),
    path('metrics/<int:pk>/', views.MetricDetailView.as_view(), name='metric-detail'),

    # Triage Log URLs
    path('triage-logs/', views.TriageLogListCreateView.as_view(), name='triage-log-list-create'),
    path('triage-logs/<int:pk>/', views.TriageLogDetailView.as_view(), name='triage-log-detail'),

    # Caseworker Action URLs
    path('caseworker-actions/', views.CaseworkerActionListCreateView.as_view(), name='caseworker-action-list-create'),
    path('caseworker-actions/<int:pk>/', views.CaseworkerActionDetailView.as_view(), name='caseworker-action-detail'),

    # Notification URLs
    path('notifications/', views.NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
]
