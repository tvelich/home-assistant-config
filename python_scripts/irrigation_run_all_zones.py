logger.setLevel('INFO')

def main():
    duration = data.get('duration')

    zones = []
    is_zone_1_enabled = hass.states.is_state('input_boolean.irrigation_zone_1', 'on')
    is_zone_2_enabled = hass.states.is_state('input_boolean.irrigation_zone_2', 'on')
    is_zone_3_enabled = hass.states.is_state('input_boolean.irrigation_zone_3', 'on')
    is_zone_4_enabled = hass.states.is_state('input_boolean.irrigation_zone_4', 'on')
    is_zone_5_enabled = hass.states.is_state('input_boolean.irrigation_zone_5', 'on')
    is_zone_6_enabled = hass.states.is_state('input_boolean.irrigation_zone_6', 'on')

    if is_zone_1_enabled:
        zones.append(1)
    if is_zone_2_enabled:
        zones.append(2)
    if is_zone_3_enabled:
        zones.append(3)
    if is_zone_4_enabled:
        zones.append(4)
    if is_zone_5_enabled:
        zones.append(5)
    if is_zone_6_enabled:
        zones.append(6)

    message = f'Starting watering for {zones} for {int(round(duration / 60))} minutes per zone'
    logger.info(message)
    hass.services.call('script', 'post_slack_message', { 'message':  message }, False)

    for zone in zones:
        service_data = {'entity_id': f'switch.zone_{zone}', 'zone_id': zone, 'zone_run_time': duration}
        hass.services.call('rainmachine', 'start_zone', service_data, True)

main()
