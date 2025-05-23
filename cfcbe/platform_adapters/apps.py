from django.apps import AppConfig

class PlatformAdaptersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'platform_adapters'
    
    def ready(self):
        # Import and register adapters here
        from platform_adapters.adapter_factory import AdapterFactory
        from platform_adapters.webform.webform_adapter import WebformAdapter
        
        # Only attempt to import WhatsApp adapter if directory exists
        try:
            from platform_adapters.whatsApp.whatsapp_adapter import WhatsAppAdapter
            AdapterFactory.register_adapter('whatsapp', WhatsAppAdapter)
        except ImportError:
            pass
            
        # Register webform adapter
        AdapterFactory.register_adapter('webform', WebformAdapter)
        
        # Register EEMIS adapter
        try:
            from platform_adapters.eemis.eemis_adapter import EEMISAdapter
            AdapterFactory.register_adapter('eemis', EEMISAdapter)
            print("EEMIS adapter registered successfully")
        except ImportError as e:
            print(f"Could not import EEMIS adapter: {str(e)}")