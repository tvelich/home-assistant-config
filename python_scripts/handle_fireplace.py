REPEAT_TIMES = 5
TEMP_UPPER_THRESHOLD = 3
TEMP_LOWER_THRESHOLD = 0.3

logger.setLevel('INFO')

def call_service_repeat(action):
    for cycle in range(REPEAT_TIMES):
        hass.services.call('light', action, { 'entity_id': 'light.fireplace' }, True)

def main():
    is_cool_mode = hass.states.is_state('sensor.hallway_thermostat_operation_mode', 'cool')
    is_heat_mode = hass.states.is_state('sensor.hallway_thermostat_operation_mode', 'heat')
    is_fireplace_probably_on = hass.states.is_state('light.fireplace', 'on')
    is_home = hass.states.is_state('binary_sensor.home', 'on')
    is_sleep_mode = hass.states.is_state('input_boolean.sleep_mode_enabled', 'on')
    target_temp = float(hass.states.get('input_number.fireplace_temp').state)
    current_temp = float(hass.states.get('sensor.netatmo_home_indoor_temperature').state)

    is_target_temp_almost_reached = current_temp >= target_temp
    is_temp_low_enough_to_turn_on = (target_temp - current_temp) >= TEMP_LOWER_THRESHOLD
    is_target_temp_exceeded = (current_temp - target_temp) > TEMP_UPPER_THRESHOLD

    current_minute = datetime.datetime.now().minute

    if is_target_temp_exceeded:
        logger.warn('turning off fireplace due to excessive heat')
        hass.services.call('notify', 'notify', {
            'message': 'Fireplace turning off due to excessive heat',
            'data': {
                'push': {
                    'badge': 1
                }
            }
        }, False)
        call_service_repeat('turn_off')
    elif is_fireplace_probably_on:
        if is_cool_mode:
            logger.info('turning off fireplace because cool mode')
            call_service_repeat('turn_off')
        elif not is_home:
            logger.info('turning off fireplace because not home')
            call_service_repeat('turn_off')
        elif is_sleep_mode:
            logger.info('turning off fireplace because sleep mode on')
            call_service_repeat('turn_off')
        elif not current_temp:
            logger.info('turning off fireplace because unknown current temp')
            call_service_repeat('turn_off')
        elif is_heat_mode and is_target_temp_almost_reached:
            logger.info('turning off fireplace because target temp reached')
            call_service_repeat('turn_off')
        elif current_minute == 0:
            logger.info('sending fireplace keepalive')
            call_service_repeat('turn_on')
    elif not is_fireplace_probably_on and is_heat_mode and is_temp_low_enough_to_turn_on and is_home and not is_sleep_mode:
            logger.info('turning on fireplace because below target temp')
            call_service_repeat('turn_on')

main()
