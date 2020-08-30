sprinkler_rate_per_hour = 11.43
amount_to_water = 12.7
cycles = 2

zones = data.get('zones')

rain_two_days_ago = float(hass.states.get('sensor.rain_two_days_ago').state) or 0
rain_one_days_ago = float(hass.states.get('sensor.rain_one_days_ago').state) or 0
rain_today = float(hass.states.get('sensor.netatmo_weather_rain_sum_rain_24').state) or 0

water_last_two_days = rain_two_days_ago + rain_one_days_ago + rain_today

logger.setLevel('INFO')

if water_last_two_days < amount_to_water:
	adjusted_amount_to_water = ((amount_to_water - water_last_two_days) / sprinkler_rate_per_hour) * 60
	complete_cycle_time = ((len(zones) * adjusted_amount_to_water) / cycles)
	zone_run_time = (adjusted_amount_to_water / cycles) * 60

	message = f'Starting maintenance watering for {zones} for {int(round(adjusted_amount_to_water))} minutes per zone across {cycles} cycles'
	logger.info(message)
	hass.services.call('script', 'post_slack_message', { 'message':  message }, False)

	for cycle in range(cycles):
		for zone in zones:
			running = False
			retries = 5
			attempt = 0

			while (not running):
				if attempt > 5:
					message = f'Zone {zone} cycle {cycle + 1} exceeded retries and will be skipped'
					logger.error(message)
					hass.services.call('script', 'post_slack_message', { 'message':  message }, False)

				attempt = attempt + 1
				service_data = { 'zone_id': zone, 'zone_run_time': zone_run_time }
				hass.services.call('rainmachine', 'start_zone', service_data, True)
				time.sleep(60)
				running = hass.states.get(f'switch.zone_{zone}').state == 'on'

			time.sleep(zone_run_time)

	message = f'Completed maintenance watering for {zones} for {int(round(adjusted_amount_to_water))} minutes per zone across {cycles} cycles'
	logger.info(message)
	hass.services.call('script', 'post_slack_message', { 'message':  message }, False)
else:
	message = f'Maintenance watering not needed today because water the last two days was {water_last_two_days}mm'
	logger.info(message)
	hass.services.call('script', 'post_slack_message', { 'message':  message }, False)
