"""
Touch Circuit Simulation and Validation

Simulates RC circuit for capacitive touch pad, models frequency response, validates touch sensitivity and SNR, generates plots, and provides component value recommendations.

Usage:
    python -m hardware.projects.led_touch_grid.gen.touch_simulation

Requirements:
    - numpy
    - scipy
    - matplotlib

"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal

# RC circuit parameters (example values, override as needed)
R = 1e6  # 1 MOhm
C = 20e-12  # 20 pF (touch pad + parasitics)


def rc_transfer_function(R, C):
    """Return transfer function (H(s)) for RC low-pass filter."""
    num = [1]
    den = [R * C, 1]
    return signal.TransferFunction(num, den)


def plot_frequency_response(R, C, save_path=None):
    """Plot magnitude and phase response of RC circuit."""
    sys = rc_transfer_function(R, C)
    w, mag, phase = signal.bode(sys)
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.semilogx(w, mag)
    plt.title("RC Circuit Frequency Response")
    plt.ylabel("Magnitude (dB)")
    plt.subplot(2, 1, 2)
    plt.semilogx(w, phase)
    plt.ylabel("Phase (deg)")
    plt.xlabel("Frequency (rad/s)")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def simulate_touch_sensitivity(R, C, delta_C=2e-12, save_prefix=None):
    """
    Simulate change in frequency response when touch increases capacitance.
    delta_C: Capacitance change due to touch (F)
    """
    print(f"Simulating baseline (C={C*1e12:.1f} pF), touch (C+ΔC={C+delta_C:.1e} F)")
    if save_prefix:
        plot_frequency_response(R, C, save_path=f"{save_prefix}_baseline.png")
        plot_frequency_response(R, C + delta_C, save_path=f"{save_prefix}_touched.png")
    else:
        plot_frequency_response(R, C)
        plot_frequency_response(R, C + delta_C)


def calculate_snr(signal_level, noise_level):
    """Return signal-to-noise ratio in dB."""
    return 20 * np.log10(signal_level / noise_level)


def recommend_component_values(target_fc=1e3, pad_C=20e-12):
    """
    Recommend R for a given target cutoff frequency and pad capacitance.
    fc = 1/(2πRC)
    """
    R = 1 / (2 * np.pi * target_fc * pad_C)
    print(f"Recommended R for fc={target_fc:.1f} Hz, C={pad_C*1e12:.1f} pF: {R/1e6:.2f} MΩ")
    return R


if __name__ == "__main__":
    # Example usage
    from pathlib import Path

    sim_dir = Path("out/led_touch_grid/sim")
    sim_dir.mkdir(parents=True, exist_ok=True)
    print("Touch Circuit Simulation")
    plot_frequency_response(R, C, save_path="out/led_touch_grid/sim/baseline.png")
    simulate_touch_sensitivity(R, C, save_prefix="out/led_touch_grid/sim/touch")
    snr = calculate_snr(1.0, 0.01)
    print(f"Example SNR: {snr:.1f} dB")
    recommend_component_values()
