from platform_adapters.eemis.eemis_adapter import EEMISAdapter
from platform_adapters.adapter_factory import AdapterFactory

# Register the EEMIS adapter with the factory
AdapterFactory.register_adapter('eemis', EEMISAdapter)