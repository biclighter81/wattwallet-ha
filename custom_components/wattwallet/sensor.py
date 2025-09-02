"""Support for Wattwallet energy monitoring."""

from datetime import timedelta
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)


class HttpStatusSensor(Entity):
    """Entity to track HTTP request status."""

    def __init__(self, hass: HomeAssistant, name="wattwallet HTTP Status"):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._attr_name = name
        self._attr_icon = "mdi:http"
        self._attr_unique_id = "wattwallet_http_status"
        self._attr_state = None
        self._attr_extra_state_attributes = {"message": ""}

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._attr_state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attr_extra_state_attributes

    def set_state(self, state, message):
        """Update the sensor state safely."""
        self._attr_state = state
        self._attr_extra_state_attributes["message"] = message
        if self.hass:
            self.async_write_ha_state()

    async def async_update(self):
        """Update method is not used."""
        return


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the wattwallet sensor."""
    session = async_get_clientsession(hass)
    status_sensor = HttpStatusSensor(hass=hass)

    # Add entities first
    async_add_entities([status_sensor])
    timer_data = {}

    async def send_energy_data(now=None):
        """Send energy data to the configured endpoint."""
        if not entry.data:
            _LOGGER.error("No configuration data available")
            return

        api_token = entry.options.get("api_token", entry.data.get("api_token"))
        target_url = entry.options.get("target_url", entry.data.get("target_url"))
        meters = entry.options.get("stromzaehler", entry.data.get("stromzaehler", []))

        if not all([api_token, target_url, meters]):
            _LOGGER.error("Missing required configuration values")
            return

        data = []
        for entity_id in meters:
            state = hass.states.get(entity_id)
            if state:
                data.append(
                    {
                        "entity_id": entity_id,
                        "state": state.state,
                        "attributes": dict(state.attributes),
                    }
                )

        if not data:
            _LOGGER.warning("No energy data available to send")
            return

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        try:
            _LOGGER.debug("Sending data to URL: %s", target_url)
            async with session.post(
                target_url,
                json={"data": data},
                headers=headers,
                timeout=30,
            ) as response:
                await response.text()  
                response.raise_for_status()
                status_sensor.set_state(
                    state=response.status, message="Erfolgreich gesendet"
                )
                _LOGGER.debug("Successfully sent data to %s", target_url)
        except (aiohttp.ClientError, aiohttp.ServerTimeoutError) as err:
            status_sensor.set_state(state=None, message=f"Fehler: {err}")
            _LOGGER.error("Failed to send data: %s", str(err))

    def setup_timer():
        """Set up the update timer with current config."""

        if "cancel" in timer_data:
            timer_data["cancel"]()

        interval = timedelta(
            seconds=entry.options.get(
                "interval",
                entry.data.get("interval", 300),  # Default 5 minutes
            )
        )

        # Set up new timer
        timer_data["cancel"] = async_track_time_interval(
            hass, send_energy_data, interval
        )

    # Initial timer setup
    setup_timer()

    # Store the cancel function for cleanup
    entry.async_on_unload(timer_data["cancel"])

    async def handle_options_update(
        hass: HomeAssistant, updated_entry: ConfigEntry
    ) -> None:
        """Handle options update."""
        _LOGGER.debug("Options update received: %s", updated_entry.options)
        # Update timer with new interval
        setup_timer()
        # Trigger immediate send after config change
        await send_energy_data()

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(handle_options_update))

    # Schedule initial data send after Home Assistant is fully started
    async def async_init_send(_):
        """Handle initial data send after HA is started."""
        await send_energy_data()

    if hass.is_running:
        await async_init_send(None)
    else:
        hass.bus.async_listen_once("homeassistant_started", async_init_send)

    return True
