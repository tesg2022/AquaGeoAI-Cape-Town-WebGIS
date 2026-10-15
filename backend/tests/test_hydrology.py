from app.hydrology import water_availability_screening
import pytest

def test_p_minus_et_screening():
    result = water_availability_screening(600, 420)
    assert result["p_minus_et_mm"] == 180
    assert "not a direct groundwater recharge estimate" in result["interpretation"]

def test_reject_negative_inputs():
    with pytest.raises(ValueError):
        water_availability_screening(-1, 0)
