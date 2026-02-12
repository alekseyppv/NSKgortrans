"""Config flow for NSK Gortrans integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ROUTE,
    CONF_SCAN_INTERVAL,
    CONF_STOP_URL,
    CONF_TRANSPORT_TYPE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    TRANSPORT_TYPES,
)


def _build_schema(user_input: dict[str, Any] | None = None) -> vol.Schema:
    data = user_input or {}

    return vol.Schema(
        {
            vol.Required(CONF_STOP_URL, default=data.get(CONF_STOP_URL, "")): str,
            vol.Required(CONF_ROUTE, default=data.get(CONF_ROUTE, "")): str,
            vol.Required(
                CONF_TRANSPORT_TYPE,
                default=data.get(CONF_TRANSPORT_TYPE, next(iter(TRANSPORT_TYPES))),
            ): vol.In(list(TRANSPORT_TYPES)),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=15, max=3600)),
        }
    )


class NskgortransConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NSK Gortrans."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_STOP_URL]}::{user_input[CONF_TRANSPORT_TYPE]}::{user_input[CONF_ROUTE]}".lower()
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="NSK Gortrans", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Create the options flow."""
        return NskgortransOptionsFlow(config_entry)


class NskgortransOptionsFlow(config_entries.OptionsFlow):
    """Handle NSK Gortrans options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_build_schema(current))
