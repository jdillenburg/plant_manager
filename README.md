# Home Assistant Plant Manager Integration

This custom integration for Home Assistant helps you manage your plant watering schedule using NFC tags. It creates recurring calendar events for watering reminders and uses input boolean helpers to track which plants need water. When you water a plant, simply scan its NFC tag to mark it as watered.

## Features

- Create recurring calendar events for plant watering schedules
- Automatic input_boolean management for plant watering status
- NFC tag support for marking plants as watered
- Logbook entries for plant watering events
- Dashboard interface for adding new plants

## Installation

1. Create the following directory structure in your Home Assistant config directory:
```
custom_components/
  plant_manager/
    __init__.py
    manifest.json
    automations.yaml
```

2. Copy the integration files into the `plant_manager` directory.

3. Add to your `configuration.yaml`:
```yaml
plant_manager:
  calendar_entity_id: calendar.plants  # Optional, defaults to calendar.plants
```

4. Restart Home Assistant

## Usage

### Adding a New Plant

You can add a new plant either through:

1. Service Call:
```yaml
service: plant_manager.add_plant
data:
  name: "Living Room Snake Plant"
  frequency: 14  # Days between watering
```

2. Dashboard Interface:
```yaml
type: custom:vertical-stack-card
cards:
  - type: entities
    title: Add New Plant
    entities:
      - entity: input_text.new_plant_name
        name: Plant Name
        icon: mdi:flower
        type: custom:text-input-row
        helper_text: "Enter the name of your plant (e.g., Living Room Snake Plant)"
      - entity: input_select.plant_watering_frequency
      - type: button
        name: Add Plant
        tap_action:
          action: call-service
          service: plant_manager.add_plant
          service_data:
            name: "[[[ return states['input_text.new_plant_name'].state ]]]"
            frequency: "[[[ return parseInt(states['input_select.plant_watering_frequency'].state) ]]]"
```

### NFC Tags

1. Create NFC tags with the following naming convention:
   - Tag name: `<plant_name> watered tag`
   - Example: If your plant is named "Living Room Snake Plant", the tag should be named "Living Room Snake Plant watered tag"

2. When you water a plant, scan its NFC tag. This will:
   - Turn off the corresponding input_boolean
   - Create a logbook entry recording the watering

### System Operation

The integration works through two main automations:

1. Calendar Event Trigger:
   - When a plant's calendar event starts, its corresponding input_boolean is turned on
   - Example: `input_boolean.living_room_snake_plant_needs_water`

2. NFC Tag Scanning:
   - When you scan a plant's NFC tag, its corresponding input_boolean is turned off
   - A logbook entry is created recording the watering

### Entity Naming Conventions

- Input Boolean: `input_boolean.<plant_name>_needs_water`
  - Example: `input_boolean.living_room_snake_plant_needs_water`
- Calendar Events: Plant name exactly as entered
  - Example: "Living Room Snake Plant"
- NFC Tags: `<plant_name> watered tag`
  - Example: "Living Room Snake Plant watered tag"

## Dashboard Example

Create a dashboard to display plants that need water:

```yaml
type: entities
title: Plants Needing Water
entities:
  - type: custom:auto-entities
    filter:
      include:
        - entity_id: "input_boolean.*_needs_water"
          state: "on"
    show_empty: false
    card:
      type: entities
      show_header_toggle: false
```

## Development

The integration stores plant data in Home Assistant's storage system. You can find the data in:
`.storage/plant_manager.plants`

## Troubleshooting

1. Check that input_boolean entities are being created:
   ```bash
   ls ~/.homeassistant/config/.storage/core.entity_registry
   ```

2. Verify calendar events are being created:
   - Navigate to Calendar in Home Assistant
   - Look for events matching your plant names

3. Test NFC tag scanning:
   - Scan a tag
   - Check the logbook for the watering entry
   - Verify the input_boolean turns off

## Contributing

Feel free to submit issues and pull requests on GitHub.

## License

This project is licensed under the MIT License - see the LICENSE file for details.