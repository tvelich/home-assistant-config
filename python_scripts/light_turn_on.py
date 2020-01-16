DEFAULT_KELVIN = 5000
DEFAULT_BRIGHTNESS = 255
DEFAULT_TRANSITION = 3

entity_id = data.get('entity_id')
kelvin = data.get('kelvin')
color_name = data.get('color_name')
effect = data.get('effect')
brightness = data.get('brightness', DEFAULT_BRIGHTNESS)
transition = data.get('transition', DEFAULT_TRANSITION)
preserve_brightness = data.get('preserve_brightness')
replay = data.get('replay', 'true') == 'true'

if entity_id:
    service_data = { 'entity_id': entity_id, 'transition': transition }

    if brightness and not preserve_brightness:
        service_data['brightness'] = brightness

    if color_name:
        service_data['color_name'] = color_name
    elif kelvin:
        service_data['kelvin'] = kelvin
    elif effect:
        service_data['effect'] = effect
    else:
        service_data['kelvin'] = DEFAULT_KELVIN

    hass.services.call('light', 'turn_on', service_data, False)

    # In case something failed to turn on, replay after when the transition should be complete
    if replay:
        time.sleep(transition + 1)
        hass.services.call('light', 'turn_on', service_data, False)
else:
    logger.error('Missing entity id!')
