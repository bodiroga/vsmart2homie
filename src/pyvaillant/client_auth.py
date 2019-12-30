# Python library for managing a Vaillant / Bulex MiGo Thermostat
# Based on the pyatmo library by Philippe Larduinat
# Revised July 2019
# Public domain source code
"""
This API provides access to the Vaillant / Bulex smart thermostat
This package can be used with Python3 applications
PythonAPI Vaillant/Bulex REST data access
"""
import logging
import time

from . import _BASE_URL, NoDevice, postRequest

LOG = logging.getLogger(__name__)

# Common definitions
_AUTH_REQ = _BASE_URL + "oauth2/token"
_WEBHOOK_URL_ADD = _BASE_URL + "api/addwebhook"
_WEBHOOK_URL_DROP = _BASE_URL + "api/dropwebhook"
_DEFAULT_SCOPE = "read_station read_camera access_camera read_thermostat write_thermostat read_presence access_presence"
_DEFAULT_APP_VERSION = "1.0.4.0"
_DEFAULT_USER_PREFIX = "vaillant"

class ClientAuth(object):
    """
    Request authentication and keep access token available through token method. Renew it automatically if necessary
    Args:
        clientId (str): Application clientId delivered by Netatmo on dev.netatmo.com
        clientSecret (str): Application Secret key delivered by Netatmo on dev.netatmo.com
        username (str)
        password (str)
        scope (Optional[str]): Default value is 'read_station'
            read_station: to retrieve weather station data (Getstationsdata, Getmeasure)
            read_camera: to retrieve Welcome data (Gethomedata, Getcamerapicture)
            access_camera: to access the camera, the videos and the live stream.
            read_thermostat: to retrieve thermostat data (Getmeasure, Getthermostatsdata)
            write_thermostat: to set up the thermostat (Syncschedule, Setthermpoint)
            read_presence: to retrieve Presence data (Gethomedata, Getcamerapicture)
            read_homecoach: to retrieve Home Coache data (Gethomecoachsdata)
            access_presence: to access the live stream, any video stored on the SD card and to retrieve Presence's lightflood status
            Several value can be used at the same time, ie: 'read_station read_camera'
    """

    def __init__(
        self, clientId, clientSecret, username, password, scope=_DEFAULT_SCOPE, app_version=_DEFAULT_APP_VERSION, user_prefix=_DEFAULT_USER_PREFIX
    ):
        postParams = {
            "grant_type": "password",
            "client_id": clientId,
            "client_secret": clientSecret,
            "username": username,
            "password": password,
            "scope": scope,
        }

        if user_prefix:
            postParams.update({"user_prefix": user_prefix})
        if app_version:
            postParams.update({"app_version": app_version})

        resp = postRequest(_AUTH_REQ, postParams)
        self._clientId = clientId
        self._clientSecret = clientSecret
        try:
            self._accessToken = resp["access_token"]
        except (KeyError):
            LOG.error("Netatmo API returned %s", resp["error"])
            raise NoDevice("Authentication against Netatmo API failed")
        self.refreshToken = resp["refresh_token"]
        self._scope = resp["scope"]
        self.expiration = int(resp["expire_in"] + time.time() - 1800)


    @property
    def accessToken(self):

        if self.expiration < time.time():  # Token should be renewed
            postParams = {
                "grant_type": "refresh_token",
                "refresh_token": self.refreshToken,
                "client_id": self._clientId,
                "client_secret": self._clientSecret,
            }
            resp = postRequest(_AUTH_REQ, postParams)
            self._accessToken = resp["access_token"]
            self.refreshToken = resp["refresh_token"]
            self.expiration = int(resp["expire_in"] + time.time() - 1800)
        return self._accessToken
