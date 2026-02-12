"""Constants for the NSK Gortrans integration."""

from __future__ import annotations

DOMAIN = "nskgortrans"
PLATFORMS = ["sensor"]

CONF_STOP_URL = "stop_url"
CONF_ROUTE = "route"
CONF_TRANSPORT_TYPE = "transport_type"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "NSK Gortrans"
DEFAULT_SCAN_INTERVAL = 60

TRANSPORT_TYPES = {
    "bus": "автобус",
    "trolleybus": "троллейбус",
    "shuttle_taxi": "маршрутное такси",
    "tram": "трамвай",
}
