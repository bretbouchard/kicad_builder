import numpy as np
from hardware.projects.led_touch_grid.gen import touch_simulation


def test_rc_transfer_function_shape():
    """Test transfer function numerator/denominator shape."""
    sys = touch_simulation.rc_transfer_function(1e6, 20e-12)
    assert hasattr(sys, "num") and hasattr(sys, "den")


def test_snr_calculation():
    """Test SNR calculation for known values."""
    assert np.isclose(touch_simulation.calculate_snr(1.0, 0.01), 40.0)


def test_recommend_component_values():
    """Test recommended R for known fc and C."""
    R = touch_simulation.recommend_component_values(target_fc=1e3, pad_C=20e-12)
    assert 7.9e6 < R < 8.1e6  # Should be ~7.96 MΩ


def test_simulate_touch_sensitivity_runs():
    """Test that simulate_touch_sensitivity runs without error."""
    # Should not raise
    touch_simulation.simulate_touch_sensitivity(1e6, 20e-12, delta_C=2e-12)
