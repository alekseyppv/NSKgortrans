"""Sensor platform for NSK Gortrans."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ROUTE, CONF_TRANSPORT_TYPE, CONF_STOP_URL, DOMAIN, TRANSPORT_TYPES
from .coordinator import NskgortransCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor from config entry."""
    coordinator: NskgortransCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NskgortransSensor(entry, coordinator)])


class NskgortransSensor(CoordinatorEntity[NskgortransCoordinator], SensorEntity):
    """Representation of arrival time sensor."""

    _attr_icon = "mdi:bus-clock"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: NskgortransCoordinator) -> None:
        super().__init__(coordinator)

        merged = {**entry.data, **entry.options}
        route = merged[CONF_ROUTE]
        transport_type = merged[CONF_TRANSPORT_TYPE]
        stop_url = merged[CONF_STOP_URL]

        self._attr_unique_id = f"{entry.entry_id}_{transport_type}_{route}"
        self._attr_name = f"{TRANSPORT_TYPES[transport_type].title()} {route}"
        self._attr_extra_state_attributes = {
            "route": route,
            "transport_type": transport_type,
            "transport_type_name": TRANSPORT_TYPES[transport_type],
            "stop_url": stop_url,
        }
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"NSK Gortrans {route}",
            manufacturer="NSK Gortrans",
            model="Public transport stop forecast",
            configuration_url=stop_url,
        )

    @property
    def native_value(self) -> int | None:
        """Return minutes until arrival, or unknown when not found."""
        return self.coordinator.data
