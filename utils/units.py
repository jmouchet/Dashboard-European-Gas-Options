"""Explicit energy conversions. No universal gas-volume conversion is assumed."""
import math


def energy_to_mwh(value: float | None, unit: str) -> float | None:
    factors = {"MWh": 1, "GWh": 1_000, "TWh": 1_000_000}
    if unit not in factors:
        raise ValueError("Supported energy units: MWh, GWh, TWh.")
    if value is None:
        return None
    if not math.isfinite(value):
        raise ValueError("Energy must be finite.")
    return value * factors[unit]


def mcm_to_gwh(volume: float | None, calorific_kwh_per_m3: float) -> float | None:
    """1 mcm = 10^6 m³; 1 GWh = 10^6 kWh. Specify HHV/LHV basis upstream."""
    if not math.isfinite(calorific_kwh_per_m3) or calorific_kwh_per_m3 <= 0:
        raise ValueError("Supply a positive, finite calorific value in kWh/m³.")
    if volume is None:
        return None
    if not math.isfinite(volume):
        raise ValueError("Volume must be finite.")
    return volume * calorific_kwh_per_m3
