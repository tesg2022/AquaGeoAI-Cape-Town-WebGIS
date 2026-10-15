"""Small pure-Python screening calculation; no EE credentials required."""

def water_availability_screening(
    precipitation_mm: float,
    actual_et_mm: float,
) -> dict:
    """Calculate P - ET for the same period; not groundwater recharge."""
    if precipitation_mm < 0 or actual_et_mm < 0:
        raise ValueError("P and ET must be non-negative.")
    return {
        "precipitation_mm": precipitation_mm,
        "actual_et_mm": actual_et_mm,
        "p_minus_et_mm": precipitation_mm - actual_et_mm,
        "units": "mm for the specified period",
        "interpretation": (
            "Precipitation minus actual evapotranspiration; "
            "not a direct groundwater recharge estimate."
        ),
    }
