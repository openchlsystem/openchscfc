from platform_adapters.ceemis.ceemis_adapter import CEEMISAdapter
from platform_adapters.adapter_factory import AdapterFactory

# Register the EEMIS adapter with the factory
AdapterFactory.register_adapter('ceemis', CEEMISAdapter)