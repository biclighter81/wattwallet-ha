import logging
import requests
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
from functools import partial

_LOGGER = logging.getLogger(__name__)

class HttpStatusSensor(Entity):
    
    def __init__(self, name="Wattwallet HTTP Status"):
        self._attr_name = name
        self._attr_icon = "mdi:http"
        self._state = None
        self._message = ""

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {"message": self._message}

    async def async_update(self):
        pass

async def async_setup_entry(hass, entry, async_add_entities):
    config = entry.data

    status_sensor = HttpStatusSensor()

    async def send_energy_data(now):
        data = []
        for entity_id in config.get("stromzaehler", []):
            state = hass.states.get(entity_id)
            if state:
                data.append({
                    "entity_id": entity_id,
                    "state": state.state,
                    "attributes": dict(state.attributes)
                })

        headers = {
            "Authorization": f"Bearer {config['api_token']}",
            "Content-Type": "application/json"
        }

        try:
            post_fn = partial(
                requests.post,
                config["target_url"],
                json={"data": data},
                headers=headers
            )
            response = await hass.async_add_executor_job(post_fn)
            response.raise_for_status()
            status_sensor._state = response.status_code
            status_sensor._message = "Erfolgreich gesendet"
            _LOGGER.debug("Successfully sent data to %s", config["target_url"])
        except Exception as e:
            status_sensor._state = None
            status_sensor._message = f"Fehler: {e}"
            _LOGGER.error("Failed to send data: %s", str(e))

        status_sensor.async_write_ha_state()

    interval = timedelta(seconds=config.get("interval", 300))
    async_track_time_interval(hass, send_energy_data, interval)

    async_add_entities([status_sensor])

    return True
