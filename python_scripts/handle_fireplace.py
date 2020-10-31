REPEAT_TIMES = 5
TEMP_UPPER_THRESHOLD = 3
TEMP_LOWER_THRESHOLD = 0.5

def call_service_repeat(action):
    for cycle in range(REPEAT_TIMES):
        hass.services.call('light', action, { 'entity_id': 'light.fireplace' }, True)

def main():
    is_cool_mode = hass.states.is_state('sensor.hallway_thermostat_operation_mode', 'cool')
    is_heat_mode = hass.states.is_state('sensor.hallway_thermostat_operation_mode', 'heat')
    is_fireplace_probably_on = hass.states.is_state('light.fireplace', 'on')
    is_home = hass.states.is_state('device_tracker.tom_phone', 'home')
    is_sleep_mode = hass.states.is_state('input_boolean.sleep_mode', 'on')
    target_temp = float(hass.states.get('sensor.hallway_thermostat_target').state)
    current_temp = float(hass.states.get('sensor.avg_living_room_temperature').state)

    is_target_temp_almost_reached = current_temp >= target_temp
    is_temp_low_enough_to_turn_on = (target_temp - current_temp) >= TEMP_LOWER_THRESHOLD
    is_target_temp_exceeded = (current_temp - target_temp) > TEMP_UPPER_THRESHOLD

    if is_target_temp_exceeded:
        logger.warning('turning off fireplace due to excessive heat')
        hass.services.call('script', 'post_slack_message', { 'message':  'Fireplace turning off due to excessive heat' }, False)
        call_service_repeat('turn_off')
    elif is_fireplace_probably_on:
        if is_cool_mode:
            logger.warning('turning off fireplace because cool mode')
            call_service_repeat('turn_off')
        if not is_home:
            logger.warning('turning off fireplace because not home')
            call_service_repeat('turn_off')
        if is_sleep_mode:
            logger.warning('turning off fireplace because sleep mode on')
            call_service_repeat('turn_off')
        if not current_temp:
            logger.warning('turning off fireplace because unknown current temp')
            call_service_repeat('turn_off')
        elif is_heat_mode and is_target_temp_almost_reached:
            logger.warning('turning off fireplace because target temp reached')
            call_service_repeat('turn_off')
    elif not is_fireplace_probably_on and is_heat_mode and is_temp_low_enough_to_turn_on and is_home and not is_sleep_mode:
            logger.warning('turning on fireplace because below target temp')
            call_service_repeat('turn_on')

main()