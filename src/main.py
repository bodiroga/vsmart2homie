import logging
import os
import time
import sys

from pyvaillant.client_auth import ClientAuth
from pyvaillant.vaillant_data import VaillantData
from vsmart_device import vSmartDevice

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

logger = logging.getLogger()

mqtt_settings = {
        "MQTT_BROKER" : "localhost",
        "MQTT_PORT" : 1883,
        "MQTT_USERNAME": None,
        "MQTT_PASSWORD": None,
        "MQTT_CLIENT_ID": "vsmart2homie"
    }

if __name__ == "__main__":
    try:
        # Get vSmart connection values
        client_id = os.environ.get("CLIENT_ID")
        client_secret = os.environ.get("CLIENT_SECRET")
        username = os.environ.get("USERNAME")
        password = os.environ.get("PASSWORD")

        if not client_id or not client_secret or not username or not password:
            logger.error("Not all vSmart parameters are set")
            sys.exit(0)

        # Get mqtt connection values
        for value in ["MQTT_BROKER", "MQTT_PORT", "MQTT_USERNAME", "MQTT_PASSWORD", "MQTT_CLIENT_ID"]:
            mqtt_settings[value] = os.environ.get(value) or mqtt_settings[value]

        clientAuth = ClientAuth(client_id, client_secret, username, password)
        vaillant_connection = VaillantData(clientAuth)

        # Get data interval value
        data_interval = int(os.environ.get("DATA_INTERVAL")) or 300

        system_name = "vSmart ({})".format(vaillant_connection.station_name)
        vsmart = vSmartDevice(device_id="vsmart", name=system_name, mqtt_settings=mqtt_settings, connection=vaillant_connection)

        while True:
            vaillant_connection.update()
            vsmart.get_node("thermostat").set_property_value("current-temp", vaillant_connection.current_temp)
            vsmart.get_node("thermostat").set_property_value("setpoint-temp", vaillant_connection.setpoint_temp)
            vsmart.get_node("thermostat").set_property_value("setpoint-mode", vaillant_connection.setpoint_mode)
            vsmart.get_node("thermostat").set_property_value("system-mode", vaillant_connection.system_mode)
            vsmart.get_node("thermostat").set_property_value("battery", vaillant_connection.battery)

            vsmart.get_node("outdoor").set_property_value("outdoor-temp", vaillant_connection.outdoor_temperature)

            vsmart.get_node("boiler").set_property_value("ebus-error", vaillant_connection.ebus_error)
            vsmart.get_node("boiler").set_property_value("boiler-error", vaillant_connection.boiler_error)
            vsmart.get_node("boiler").set_property_value("maintenance-status", vaillant_connection.maintenance_status)
            vsmart.get_node("boiler").set_property_value("refill-water", vaillant_connection.refill_water)

            time.sleep(data_interval)

    except (KeyboardInterrupt, SystemExit):
        logger.info("Exiting.")   