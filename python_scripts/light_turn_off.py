DEFAULT_TRANSITION = 3

entity_id = data.get('entity_id')
transition = data.get('transition', DEFAULT_TRANSITION)
replay = data.get('replay', 'true') == 'false'

if entity_id:
    service_data = { 'entity_id': entity_id, 'transition': transition }
    hass.services.call('light', 'turn_off', service_data, False)

    # In case something failed to turn off, replay call after when the transition should be complete
    if not replay:
        time.sleep(transition + 1)
        hass.services.call('light', 'turn_off', service_data, False)
else:
    logger.error('Missing entity id!')
