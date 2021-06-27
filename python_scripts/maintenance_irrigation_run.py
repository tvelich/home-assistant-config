REPEAT_TIMES = 5
SPRINKLER_RATE_PER_HOUR = 11.43
AMOUNT_TO_WATER = 12.7
CYCLES = 2

def call_service_repeat(service_data):
    for cycle in range(REPEAT_TIMES):
        hass.services.call('rainmachine', 'start_zone', service_data, True)

def main():
    zones = data.get('zones')

    rain_three_days_ago_sensor = hass.states.get('sensor.rain_three_days_ago').state
    rain_three_days_ago = float(0 if rain_three_days_ago_sensor == 'unknown' else rain_three_days_ago_sensor)
    rain_two_days_ago_sensor = hass.states.get('sensor.rain_two_days_ago').state
    rain_two_days_ago = float(0 if rain_two_days_ago_sensor == 'unknown' else rain_two_days_ago_sensor)
    rain_one_day_ago_sensor = hass.states.get('sensor.rain_one_day_ago').state
    rain_one_day_ago = float(0 if rain_one_day_ago_sensor == 'unknown' else rain_one_day_ago_sensor)
    rain_today_sensor = hass.states.get('sensor.netatmo_home_indoor_rain_rain_today').state
    rain_today = float(0 if rain_today_sensor == 'unknown' else rain_today_sensor)
    excessive_heat_today = hass.states.get('sensor.excessive_heat_today').state == 'on'

    past_water = rain_two_days_ago + rain_one_day_ago + rain_today

    if not excessive_heat_today:
        past_water = past_water + rain_three_days_ago

    logger.setLevel('INFO')

    if past_water < AMOUNT_TO_WATER:
        adjusted_amount_to_water = ((AMOUNT_TO_WATER - past_water) / SPRINKLER_RATE_PER_HOUR) * 60
        zone_run_time = (adjusted_amount_to_water / CYCLES) * 60

        message = f'Starting maintenance watering for {zones} for {int(round(adjusted_amount_to_water))} minutes per zone across {CYCLES} cycles'
        logger.info(message)
        hass.services.call('script', 'post_slack_message', { 'message':  message }, False)

        for cycle in range(CYCLES):
            for zone in zones:
                service_data = {'zone_id': zone, 'zone_run_time': zone_run_time}
                call_service_repeat(service_data)
                time.sleep(zone_run_time)

        message = f'Completed maintenance watering for {zones} for {int(round(adjusted_amount_to_water))} minutes per zone across {CYCLES} cycles'
        logger.info(message)
        hass.services.call('script', 'post_slack_message', { 'message':  message }, False)
    else:
        message = f'Maintenance watering not needed today because water the last few days was {round(past_water, 2)}mm'
        logger.info(message)
        hass.services.call('script', 'post_slack_message', { 'message':  message }, False)

main()
