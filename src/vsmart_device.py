import logging

from homie.device_base import Device_Base
from homie.node.node_base import Node_Base
from homie.node.property.property_float import Property_Float
from homie.node.property.property_enum import Property_Enum
from homie.node.property.property_battery import Property_Battery
from homie.node.property.property_boolean import Property_Boolean

logger = logging.getLogger(__name__)

class vSmartDevice(Device_Base):

    def __init__(self, device_id='vsmart', name='vSmart', homie_settings=None, mqtt_settings=None, connection=None):
        super().__init__ (device_id, name, homie_settings, mqtt_settings)

        self.connection = connection

        self.add_node(ThermostatNode(self))
        self.add_node(OutdoorNode(self))
        self.add_node(BoilerNode(self))

        self.start()

class ThermostatNode(Node_Base):
    def __init__(self, device, id='thermostat', name='thermostat', type_='thermostat', retain=True, qos=1): 
        super().__init__(device,id,name,type_,retain,qos)

        self.add_property(Property_Float(self,'current-temp', 'Current Temp', settable=False, unit='ºC'))
        self.add_property(Property_Float(self,'setpoint-temp', 'Setpoint Temp', unit='ºC', set_value=self.set_setpoint_temp))
        self.add_property(Property_Enum(self,'setpoint-mode', 'Setpoint Mode', data_format="auto,manual,away,hwb" ,set_value=self.set_setpoint_mode))
        self.add_property(Property_Enum(self,'system-mode', 'System Mode', data_format="winter,summer,frostguard" ,set_value=self.set_system_mode))
        self.add_property(Property_Battery(self))

    def set_setpoint_temp(self, value):
        logger.debug('New setpoint request {}'.format(value))
        self.device.connection.activate("manual", value)

    def set_setpoint_mode(self, value):
        if value == "auto":
            logger.debug('New setpoint request {}'.format(value))
            self.device.connection.disable("manual")

    def set_system_mode(self, value):
        logger.debug("New system mode: {}".format(value))
        self.device.connection.setSystemMode(value)
        

class OutdoorNode(Node_Base):
    def __init__(self, device, id='outdoor', name='Outdoor', type_='outdoor', retain=True, qos=1): 
        super().__init__(device,id,name,type_,retain,qos)

        self.add_property(Property_Float(self,'outdoor-temp', 'Outdoor Temp', settable=False, unit='ºC'))


class BoilerNode(Node_Base):
    def __init__(self, device, id='boiler', name='Boiler', type_='boiler', retain=True, qos=1): 
        super().__init__(device,id,name,type_,retain,qos)

        self.add_property(Property_Boolean(self,'ebus-error', 'eBus Error', settable=False))
        self.add_property(Property_Boolean(self,'boiler-error', 'Boiler Error', settable=False))
        self.add_property(Property_Boolean(self,'maintenance-status', 'Maintenance Status', settable=False))
        self.add_property(Property_Boolean(self,'refill-water', 'Refill Water', settable=False))