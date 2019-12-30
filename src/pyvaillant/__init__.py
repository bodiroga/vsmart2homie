import logging
import requests
import time

logger = logging.getLogger(__name__)

# Common definitions
_BASE_URL = "https://api.netatmo.com/"


class NoDevice(Exception):
    pass

class NoValidMode(Exception):
    pass

class NoValidSystemMode(Exception):
    pass

# Utilities routines


def postRequest(url, params=None, timeout=10):
    resp = requests.post(url, data=params, timeout=timeout)
    if not resp.ok:
        logger.error("The Netatmo API returned %s", resp.status_code)
    try:
        return (
            resp.json()
            if "application/json" in resp.headers.get("content-type")
            else resp.content
        )
    except TypeError:
        logger.debug("Invalid response %s", resp)
    return None


def toTimeString(value):
    return time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(int(value)))


def toEpoch(value):
    return int(time.mktime(time.strptime(value, "%Y-%m-%d_%H:%M:%S")))


def todayStamps():
    today = time.strftime("%Y-%m-%d")
    today = int(time.mktime(time.strptime(today, "%Y-%m-%d")))
    return today, today + 3600 * 24
