import requests
import json
import os
import logging
from dataclasses import dataclass, field


logger = logging.getLogger('pyhue')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


@dataclass
class HueBridge:
    """Class for Hue Bridge"""
    bridge_id: str
    internalipaddress: str
    temperature_sensors: list


def search_dict_keys(dictionary, key):
    if key in dictionary: return dictionary[key]
    for k, v in dictionary.items():
        if isinstance(v,dict):
            item = search_dict_keys(v, key)
            if item is not None:
                return item


def discover_hue_bridges(hue_url, hue_api_key):
    response = requests.get(hue_url)
    hue_bridges = []
    for bridge in json.loads(response.text):
        bridge_id = bridge.get("id")
        bridge_address = bridge.get("internalipaddress")
        temp_sensors = [discover_temp_sensors(bridge_address, hue_api_key)]
        hue_bridges.append(HueBridge(bridge_id, bridge_address, temp_sensors))
    return hue_bridges


def discover_temp_sensors(hue_address, hue_api_key):
    response = requests.get(f"http://{hue_address}/api/{hue_api_key}/sensors")
    sensors = json.loads(response.text)
    temperature_sensors = {}
    for sensor, sensor_type in sensors.items():
        if search_dict_keys(sensor_type, "temperature"):
            temperature_sensors[sensor] = sensor_type
    return temperature_sensors


def main():
    """ Main entry point of the app """

    hue_url = "https://discovery.meethue.com/"
    influx_address = os.environ["INFLUX_DB_ADDRESS"]
    hue_api_key = os.environ["HUE_API_KEY"]
    
    hue_ecosystem = discover_hue_bridges(hue_url, hue_api_key)

    for bridge in hue_ecosystem:
        for temp_sensor in bridge.temperature_sensors:
            for key, value in temp_sensor.items():
                temp_sensor_name = search_dict_keys(value, "name")
                temperature = (search_dict_keys(value, "temperature")) / 100

                cleaned_temp_sensor_name = temp_sensor_name.replace(" ", "_")
                influx_data = f"temperature,name={cleaned_temp_sensor_name} value={temperature}"
                logger.info(influx_data)
                request = requests.post(influx_address, data=influx_data, headers={'Content-Type': 'application/octet-stream'})
                logger.info(request.status_code)

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
