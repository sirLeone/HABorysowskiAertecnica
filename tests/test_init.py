"""Tests for integration setup, entities and options handling."""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aertecnica.const import CONF_SCAN_INTERVAL


async def setup_integration(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Add the entry to hass and set it up."""
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_setup_and_unload(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_client: MagicMock
) -> None:
    """The entry loads, creates entities with stable unique ids and unloads."""
    await setup_integration(hass, config_entry)

    assert config_entry.state is ConfigEntryState.LOADED
    mock_client.connect.assert_awaited()

    registry = er.async_get(hass)
    unique_ids = {
        entity.unique_id
        for entity in er.async_entries_for_config_entry(registry, config_entry.entry_id)
    }
    assert {
        "test_entry_motor_hours",
        "test_entry_pressure_level",
        "test_entry_residual_max_time",
        "test_entry_motor_status",
        "test_entry_any_lock",
        "test_entry_motor_switch",
        "test_entry_reset_lock",
    } <= unique_ids

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
    mock_client.disconnect.assert_awaited()


async def test_entity_states(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_client: MagicMock
) -> None:
    """Sensor, binary sensor and switch states reflect the parsed data."""
    await setup_integration(hass, config_entry)

    motor_hours = hass.states.get("sensor.aertecnica_perfect_motor_hours")
    assert motor_hours is not None
    assert motor_hours.state == "56.7"
    assert motor_hours.attributes["unit_of_measurement"] == "h"

    pressure_level = hass.states.get("sensor.aertecnica_perfect_pressure_level")
    assert pressure_level.state == "OK"
    assert pressure_level.attributes["pressure_diff"] == 10

    residual = hass.states.get("sensor.aertecnica_perfect_residual_max_time")
    assert residual.state == "42.0"
    assert residual.attributes["unit_of_measurement"] == "min"

    temperature = hass.states.get("sensor.aertecnica_perfect_temperature")
    assert temperature.state == "25.0"

    assert hass.states.get("binary_sensor.aertecnica_perfect_motor_status").state == STATE_ON
    assert hass.states.get("binary_sensor.aertecnica_perfect_pre_alarm").state == STATE_ON
    assert hass.states.get("binary_sensor.aertecnica_perfect_lock").state == STATE_OFF

    switch = hass.states.get("switch.aertecnica_perfect_motor")
    assert switch.state == STATE_ON
    assert switch.attributes["active_prealarms"] == ["Full Bag"]
    assert "active_locks" not in switch.attributes


async def test_switch_and_button_write(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_client: MagicMock
) -> None:
    """Switch and button services send the matching Modbus commands."""
    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        "switch",
        "turn_off",
        {ATTR_ENTITY_ID: "switch.aertecnica_perfect_motor"},
        blocking=True,
    )
    mock_client.write_motor_control.assert_awaited_with(False)

    await hass.services.async_call(
        "switch",
        "turn_on",
        {ATTR_ENTITY_ID: "switch.aertecnica_perfect_motor"},
        blocking=True,
    )
    mock_client.write_motor_control.assert_awaited_with(True)

    await hass.services.async_call(
        "button",
        "press",
        {ATTR_ENTITY_ID: "button.aertecnica_perfect_reset_lock"},
        blocking=True,
    )
    mock_client.write_reset_lock.assert_awaited_once()


async def test_options_update_reloads_with_new_interval(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_client: MagicMock
) -> None:
    """Changing the scan interval in options is applied after the reload."""
    await setup_integration(hass, config_entry)
    assert config_entry.runtime_data.update_interval == timedelta(seconds=5)

    hass.config_entries.async_update_entry(config_entry, options={CONF_SCAN_INTERVAL: 30})
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.runtime_data.update_interval == timedelta(seconds=30)


async def test_setup_retries_when_device_unreachable(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_client: MagicMock
) -> None:
    """A connection failure during setup puts the entry into retry state."""
    mock_client.connect.return_value = False

    config_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.SETUP_RETRY
