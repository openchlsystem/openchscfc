# Import all adapter modules to register them
from platform_adapters.webform import *
from platform_adapters.whatsApp import *
# Future platform additions can be added here
from platform_adapters.ceemis.ceemis_adapter import CEEMISAdapter
AdapterFactory.register_adapter("ceemis", CEEMISAdapter)