from .config_flow import WattwalletConfigFlow

PLATFORMS = ["sensor"]

async def async_setup_entry(hass, entry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    )
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)