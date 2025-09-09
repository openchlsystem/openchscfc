from django.apps import AppConfig

class PlatformAdaptersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'platform_adapters'
    
    def ready(self):
        # Import and register adapters here
        from platform_adapters.adapter_factory import AdapterFactory
        from platform_adapters.webform.webform_adapter import WebformAdapter
        from platform_adapters.whatsApp.whatsapp_adapter import WhatsAppAdapter
        from platform_adapters.ceemis.ceemis_adapter import CEEMISAdapter
        from platform_adapters.eemis.eemis_adapter import EEMISAdapter
        from platform_adapters.mamacare_chatbot.mamacare_adapter import MamaCareAdapter

        AdapterFactory.register_adapter('whatsapp', WhatsAppAdapter)
        AdapterFactory.register_adapter('webform', WebformAdapter)
        AdapterFactory.register_adapter('ceemis', CEEMISAdapter)
        AdapterFactory.register_adapter('eemis', EEMISAdapter)
        AdapterFactory.register_adapter('mamacare', MamaCareAdapter)
