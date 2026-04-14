"""Tests for Wibeee constants validation."""

from __future__ import annotations

from custom_components.wibeee.const import (
    PUSH_PARAM_TO_SENSOR,
    PUSH_PHASE_MAP,
    SENSOR_TYPES,
    WibeeeSensorEntityDescription,
)


def test_push_param_to_sensor_maps_to_valid_sensor_types() -> None:
    """Verify every PUSH_PARAM_TO_SENSOR value exists in SENSOR_TYPES."""
    for push_prefix, sensor_key in PUSH_PARAM_TO_SENSOR.items():
        assert sensor_key in SENSOR_TYPES, (
            f"Push prefix '{push_prefix}' maps to '{sensor_key}' "
            f"which is not in SENSOR_TYPES"
        )


def test_push_phase_map_completeness() -> None:
    """Verify push phase map covers all expected phases."""
    assert PUSH_PHASE_MAP == {
        "1": "fase1",
        "2": "fase2",
        "3": "fase3",
        "t": "fase4",
    }


def test_sensor_types_have_required_fields() -> None:
    """Verify all sensor types have key and translation_key."""
    for key, desc in SENSOR_TYPES.items():
        assert desc.key == key, f"Sensor type key mismatch: {desc.key} != {key}"
        assert desc.translation_key is not None, (
            f"Sensor type '{key}' has no translation_key"
        )


def test_sensor_types_translation_keys_unique() -> None:
    """Verify all translation_keys are unique across sensor types."""
    translation_keys = [desc.translation_key for desc in SENSOR_TYPES.values()]
    assert len(translation_keys) == len(set(translation_keys)), (
        "Duplicate translation_keys found in SENSOR_TYPES"
    )


def test_energy_sensors_have_total_increasing() -> None:
    """Verify energy sensors use TOTAL_INCREASING state class."""
    from homeassistant.components.sensor import SensorStateClass

    energy_keys = [k for k in SENSOR_TYPES if "energia" in k]
    assert len(energy_keys) > 0, "No energy sensors found"
    for key in energy_keys:
        desc = SENSOR_TYPES[key]
        assert desc.state_class == SensorStateClass.TOTAL_INCREASING, (
            f"Energy sensor '{key}' should use TOTAL_INCREASING, "
            f"got {desc.state_class}"
        )
