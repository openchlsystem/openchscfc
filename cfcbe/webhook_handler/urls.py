from django.urls import path

from webhook_handler import auth_views
from webhook_handler.views_eemis import EEMISWebhookView
from .views import HelplineCEEMISUpdateView, HelplineCEEMISView, UnifiedWebhookView 
# from .views import CaseCategoryExportView, HelplineCEEMISView, LocationExportView, TokenGenerationView, UnifiedWebhookView, WebformCategoriesView

urlpatterns = [
    path('webhook/<str:platform>/', UnifiedWebhookView.as_view(), name='unified-webhook'),
    # path('webhook/webform/categories/', WebformCategoriesView.as_view(), name='webform-categories'),
    # path('webhook/webform/locations-export/', LocationExportView.as_view(), name='locations-export'),
    # path('webhook/webform/auth/token/', TokenGenerationView.as_view(), name='token-generation'),
    # path('webhook/webform/case-categories-export/', CaseCategoryExportView.as_view(), name='case-categories-export'),
    path('webhook/webform/auth/request-verification/', auth_views.request_email_verification, name='request_email_verification'),
    path('webhook/webform/auth/verify-otp/', auth_views.verify_otp_and_issue_token, name='verify_otp'),
    path('webhook/eemis', EEMISWebhookView.as_view(), name='eemis_webhook'),
    path('webhook/helpline/case/ceemis/', HelplineCEEMISView.as_view(), name='helpline_ceemis_case'),
    path('webhook/helpline/case/ceemis/update/', HelplineCEEMISUpdateView.as_view(), name='helpline_ceemis_case_update')
]
