# vSmart2Homie gateway

This service reads boiler and thermostat values from vSmart platform (Vaillant) and exposes the data to an MQTT broker following the Homie V4 convention.

The data is modeled as:

- vSmart (Device)
    - Thermostat (Node)
        - Current Temperature
        - Setpoint Temperature
        - Setpoint Mode
        - System Mode
        - Battery
    - Outdoor (Node)
        - Outdoor Temperature
    - Boiler (Node)
        - eBus Error
        - Boiler Error
        - Maintenance Status
        - Refill Water

To connect to the vSmart platform the app needs the following required environment variables ([instructions](https://github.com/pjmaenh/home-assistant-vaillant#installation-and-configuration)):

- CLIENT_ID
- CLIENT_SECRET
- USERNAME
- PASSWORD

Aditionally, the (optional) MQTT connection parameters can be stablished using:

- MQTT_BROKER (default: localhost)
- MQTT_PORT (default: 1883)
- MQTT_USER (default: None)
- MQTT_PASSWORD (default: None)
- MQTT_CLIENT_ID (default: vsmart2homie)

Finally, the project is based on the following libraries:

- [Homie4](https://github.com/mjcumming/homie4) Thanks @mjcumming!
- [pyvaillant](https://github.com/pjmaenh/pyvaillant) Thanks @pjmaenh!