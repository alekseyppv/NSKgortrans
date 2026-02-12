"""Data coordinator for NSK Gortrans."""

from __future__ import annotations

import logging
from datetime import timedelta

from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ROUTE,
    CONF_SCAN_INTERVAL,
    CONF_STOP_URL,
    CONF_TRANSPORT_TYPE,
    DOMAIN,
    TRANSPORT_TYPES,
)
from .parser import extract_minutes

_LOGGER = logging.getLogger(__name__)


class NskgortransCoordinator(DataUpdateCoordinator[int | None]):
    """Coordinator that fetches and parses stop arrival data."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        data = {**entry.data, **entry.options}
        self._stop_url: str = data[CONF_STOP_URL]
        self._route: str = data[CONF_ROUTE]
        self._transport_type_key: str = data[CONF_TRANSPORT_TYPE]

        scan_interval = int(data.get(CONF_SCAN_INTERVAL, 60))
        self._session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> int | None:
        transport_type_ru = TRANSPORT_TYPES[self._transport_type_key]

        try:
            async with self._session.get(self._stop_url, timeout=20) as response:
                response.raise_for_status()
                page = await response.text()
        except (TimeoutError, ClientError) as err:
            raise UpdateFailed(f"Error fetching {self._stop_url}: {err}") from err

        minutes = extract_minutes(page, self._route, transport_type_ru)
        if minutes is None:
            _LOGGER.debug(
                "Route %s (%s) was not found on page %s",
                self._route,
                transport_type_ru,
                self._stop_url,
            )
        return minutes
