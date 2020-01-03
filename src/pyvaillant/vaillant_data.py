import logging
import time
from . import _BASE_URL, NoConnection, NoDevice, NoValidMode, NoValidSystemMode, postRequest

logger = logging.getLogger(__name__)

_GETTHERMOSTATDATA_REQ = _BASE_URL + "api/getthermostatsdata"
_SETTEMP_REQ = _BASE_URL + "api/setminormode"
_SETSYSTEMMODE_REQ = _BASE_URL + "api/setsystemmode"

# # The default offset is 2 hours (when you use the thermostat itself)
DEFAULT_TIME_OFFSET = 7200

class VaillantData(object):
    """
    Representation of a Vaillant/Bulex Thermostat
    """

    def __init__(self, authData):
        self.station_name = None            # Station name
        self.module_name = None             # Module Name        
        self.current_temp = None            # Current Temperature
        self.setpoint_temp = None           # Setpoint Temperature
        self.setpoint_modes = []            # Active setpoint modes
        self.setpoint_mode = None           # Active setpoint mode
        self.system_mode = None             # System Mode (winter, summer, frostguard)
        self.battery = None                 # Battery
        self.outdoor_temperature = None     # Outdoor Temperature
        self.ebus_error = None              # eBus Error
        self.boiler_error = None            # Boiler Error
        self.maintenance_status = None      # Maintenance Status
        self.refill_water = None            # Refill Water
        self.token = authData.accessToken   # Access Token
        self.update()                       # Get latest data        
    
    def update(self):
        # Get latest data from server
        postParams = {
            "access_token": self.token,
            "device_type": "NAVaillant",
        }
        resp = postRequest(_GETTHERMOSTATDATA_REQ, postParams)

        if resp is None:
            raise NoConnection("No response from Netatmo server")

        if resp['body'] is None:
            raise NoDevice("No thermostat data returned by Netatmo server")
        self.rawData = resp['body']

        self.devList = self.rawData['devices']
        if not self.devList:
            raise NoDevice("No thermostat available")
        
        if not self.rawData['devices'][0]['modules']:
            raise NoDevice("No modules available")


        # Get station name
        self.station_name = self.devList[0]["station_name"]

        self.modList = self.devList[0]['modules']

        # Get name, current temperature and setpoint temperature
        if 'module_name' in self.modList[0]:
            self.name = self.modList[0]['module_name']
        if 'battery_percent' in self.modList[0]:
            self.battery = self.modList[0]['battery_percent']
        if 'temperature' in self.modList[0]['measured']:
            self.current_temp = self.modList[0]['measured']['temperature']
        if 'setpoint_temp' in self.modList[0]['measured']:
            self.setpoint_temp = self.modList[0]['measured']['setpoint_temp']
        
        # Get active setpoint mode(s)
        self.setpoint_modes = []
        if 'setpoint_manual' in self.modList[0] and self.modList[0]['setpoint_manual']['setpoint_activate']:
            self.setpoint_modes.append("manual")
        if 'setpoint_away' in self.modList[0] and self.modList[0]['setpoint_away']['setpoint_activate']:
            self.setpoint_modes.append("away")
        if 'setpoint_hwb' in self.devList[0] and self.devList[0]['setpoint_hwb']['setpoint_activate']:
            self.setpoint_modes.append("hwb")

        # Get active setpoint mode
        if not self.setpoint_modes:
            self.setpoint_mode = "auto"
        elif len(self.setpoint_modes) == 1:
            self.setpoint_mode = self.setpoint_modes[0]

        # Get system mode
        self.system_mode = self.devList[0]['system_mode']

        # Get outdoor temperature
        self.outdoor_temperature = self.devList[0]['outdoor_temperature']['te']

        # Get Boiler status
        self.ebus_status = self.devList[0]['ebus_status']
        self.ebus_error = self.ebus_status['ebus_error']
        self.boiler_error = self.ebus_status['boiler_error']
        self.maintenance_status = self.ebus_status['maintenance_status']
        self.refill_water = self.ebus_status['refill_water']
 
    def reset(self, deviceId = None, moduleId = None):
        '''
        Disable all setpoint modes and go back to schedule
        '''
        for mode in list(self.setpoint_modes):
            # Note that we created a copy because we will be modifying the list
            self.disable(mode, deviceId, moduleId)


    def activate(self, setpointMode, setpointTemperature, endTimeOffset = None, deviceId = None, moduleId = None):
        '''
        Activate a setpoint mode (manual, away or hwb)
        For manual mode, the setpoint temperature is required.
        '''
        if setpointMode not in ["manual", "away", "hwb"]:
            raise NoValidMode("No valid setpoint mode: [{}]".format(setpointMode))

        postParams = {"access_token": self.token}
        postParams['device_id'] = deviceId if deviceId else self.devList[0]['_id']
        postParams['module_id'] = moduleId if moduleId else self.modList[0]['_id']            
        postParams['setpoint_mode'] = setpointMode            
        postParams['activate'] = "true"
        if setpointMode in ["manual", "hwb"]:
            if endTimeOffset:
                postParams['setpoint_endtime'] = int(time.time() + endTimeOffset)
            else:
                postParams['setpoint_endtime'] = int(time.time() + DEFAULT_TIME_OFFSET)
            if setpointMode == "manual":
                if not setpointTemperature:
                    raise NoValidMode("Setpoint Temperature required for manual mode")
                postParams['setpoint_temp'] = setpointTemperature
                self.setpoint_temp = setpointTemperature

        if setpointMode not in self.setpoint_modes:
            self.setpoint_modes.append(setpointMode)

        postRequest(_SETTEMP_REQ, postParams)

    def disable(self, setpointMode, deviceId = None, moduleId = None):
        '''
        Disable a setpoint mode (manual, away or hwb)
        '''
        if setpointMode not in ["manual", "away", "hwb"]:
            raise NoValidMode("No valid setpoint mode: [{}]".format(setpointMode))

        postParams = {"access_token": self.token}
        postParams['device_id'] = deviceId if deviceId else self.devList[0]['_id']
        postParams['module_id'] = moduleId if moduleId else self.modList[0]['_id']
        postParams['setpoint_mode'] = setpointMode
        postParams['activate'] = "false"
        if setpointMode in self.setpoint_modes:
            self.setpoint_modes.remove(setpointMode)
        postRequest(_SETTEMP_REQ, postParams)

    def setSystemMode(self, systemMode, deviceId = None, moduleId = None):
        """
        Set the system mode (winter, summer, frostguard)
        """
        if systemMode not in ["winter", "summer", "frostguard"]:
            raise NoValidSystemMode("No valid system mode: [{}]".format(systemMode))

        postParams = {"access_token": self.token}
        postParams['device_id'] = deviceId if deviceId else self.devList[0]['_id']
        postParams['module_id'] = moduleId if moduleId else self.modList[0]['_id']
        postParams['system_mode'] = systemMode
        postRequest(_SETSYSTEMMODE_REQ, postParams)