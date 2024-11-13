"""The Plant Manager integration."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import logging
import os
import yaml

_LOGGER = logging.getLogger(__name__)

DOMAIN = "plant_manager"
STORAGE_KEY = f"{DOMAIN}.plants"
STORAGE_VERSION = 1

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional("calendar_entity_id", default="calendar.plants"): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Plant Manager component."""
    store = hass.helpers.storage.Store(STORAGE_VERSION, STORAGE_KEY)
    
    # Load existing plants
    plants = await store.async_load() or {}
    
    # Install generic automations if not already present
    await install_automations(hass)
    
    async def handle_add_plant(call):
        """Handle the add_plant service call."""
        plant_name = call.data["name"]
        watering_frequency = call.data["frequency"]
        
        # Create safe entity_id
        entity_id = f"input_boolean.{plant_name.lower().replace(' ', '_')}_needs_water"
        
        # Add input_boolean for water needs
        await hass.services.async_call(
            "input_boolean",
            "turn_off",
            {"entity_id": entity_id},
            blocking=True,
            context={"source": DOMAIN},
        )
        
        # Create calendar event
        await hass.services.async_call(
            "calendar",
            "create_event",
            {
                "entity_id": config[DOMAIN]["calendar_entity_id"],
                "summary": plant_name,  # Calendar event summary matches plant name exactly
                "description": f"Time to water {plant_name}",
                "start_date_time": (
                    hass.states.get("sensor.date").state + "T09:00:00"
                ),
                "end_date_time": (
                    hass.states.get("sensor.date").state + "T10:00:00"
                ),
                "rrule": f"FREQ=DAILY;INTERVAL={watering_frequency}"
            },
            blocking=True,
            context={"source": DOMAIN},
        )
        
        # Store plant data
        plants[entity_id] = {
            "name": plant_name,
            "frequency": watering_frequency,
            "created_at": hass.states.get("sensor.date").state
        }
        await store.async_save(plants)
        
        _LOGGER.info(f"Added new plant: {plant_name}")

    async def install_automations(hass):
        """Install the generic automations if they don't exist."""
        # Load the generic automations from the YAML file
        component_path = hass.config.path("custom_components", DOMAIN)
        automation_path = os.path.join(component_path, "automations.yaml")
        
        if not os.path.exists(component_path):
            _LOGGER.error(f"Component directory not found: {component_path}")
            return
            
        with open(automation_path, 'r') as file:
            generic_automations = yaml.safe_load(file)
            
        # Check if automations already exist
        existing_automations = await hass.components.automation.async_get_config()
        existing_aliases = [a.get("alias") for a in existing_automations]
        
        # Add only if they don't exist
        automations_added = False
        for automation in generic_automations:
            if automation["alias"] not in existing_aliases:
                existing_automations.append(automation)
                automations_added = True
                _LOGGER.info(f"Added automation: {automation['alias']}")
                
        if automations_added:
            await hass.components.automation.async_save_config(existing_automations)
            await hass.services.async_call(
                "automation",
                "reload",
                {},
                blocking=True,
                context={"source": DOMAIN},
            )

    # Register services
    hass.services.async_register(
        DOMAIN,
        "add_plant",
        handle_add_plant,
        schema=vol.Schema({
            vol.Required("name"): cv.string,
            vol.Required("frequency"): vol.Coerce(int)
        })
    )
    
    return True
