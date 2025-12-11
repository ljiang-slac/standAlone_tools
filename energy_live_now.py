#!/usr/bin/env python3
# filename: energy_live_calibrate.py
# Standalone script to read live PVs via caget, compute energy (in eV), print parameters
# And calibrate TOFF given a known true energy

import numpy as np
import subprocess

# Constants
H = 6.62607015e-34  # Planck's constant (J s)
C = 299792458       # Speed of light (m/s)
E_CHARGE = 1.60217663e-19  # Elementary charge (C)
D_ZERO = 1.920156e-10  # d-spacing for channel 1 (Si(220)?) in meters

# PV names for channel 1 (Crystal motor)
REP_PV = "BL22:SCAN:MASTER:MOTOR1.REP"
EREV_PV = "BL22:SCAN:MASTER:MOTOR1.EREV"
TOFF_PV = "BL22:SCAN:MASTER:MOTOR1.TOFF"

# Fallback values if caget fails
FALLBACK_REP = -472343
FALLBACK_EREV = 31489533  # Approximate based on theta ~19.95°
FALLBACK_TOFF = 25.3550848364545

def get_pv_value(pv, fallback):
    try:
        value_str = subprocess.check_output(["caget", "-t", pv], timeout=3).decode().strip()
        return float(value_str)
    except Exception as exc:
        print(f"Warning: Failed to caget {pv}, using fallback {fallback}")
        return fallback

# Read values
rep = get_pv_value(REP_PV, FALLBACK_REP)
erev = get_pv_value(EREV_PV, FALLBACK_EREV)
toff = get_pv_value(TOFF_PV, FALLBACK_TOFF)

# Compute Bragg angle (degrees)
bragg_angle = rep * 360 / erev + toff
if bragg_angle < 0:
    print("Warning: Negative Bragg angle, clamping to 0 as per code")
    bragg_angle = 0.0

# Compute energy in eV
if bragg_angle == 0:
    energy = np.nan
else:
    bragg_rad = np.radians(bragg_angle)
    sin_theta = abs(np.sin(bragg_rad))
    if sin_theta == 0:
        energy = np.nan
    else:
        energy = (H * C / (2 * D_ZERO * sin_theta)) / E_CHARGE

# Print all parameters and energy
print("\n" + "=" * 70)
print("          LIVE MONOCHROMATOR ENERGY READOUT (Channel 1)")
print("=" * 70)
print(f"REP               : {rep:.0f}")
print(f"EREV              : {erev:.0f}")
print(f"TOFF (current)    : {toff:.9f} °")
print(f"Bragg angle       : {bragg_angle:.4f} °")
print(f"d_zero            : {D_ZERO:.6e} m")
print(f"Calculated Energy : {energy:.3f} eV")
print("=" * 70)

# Calibration function
def calibrate_toff(true_energy_ev, rep, erev, d_zero=D_ZERO, h=H, c=C, e_charge=E_CHARGE):
    sin_theta_needed = (h * c) / (2 * d_zero * true_energy_ev * e_charge)
    if not 0 < sin_theta_needed <= 1:
        raise ValueError(f"Impossible sin_theta={sin_theta_needed:.4f} for {true_energy_ev} eV")
    theta_needed_deg = np.degrees(np.arcsin(sin_theta_needed))
    new_toff = theta_needed_deg - (rep * 360 / erev)
    return new_toff

# Interactive calibration
try:
    true_energy_str = input("\nEnter known STANDARD energy in eV (or press Enter to skip): ")
    if true_energy_str:
        true_energy = float(true_energy_str)
        new_toff = calibrate_toff(true_energy, rep, erev)
        delta = new_toff - toff
        print("\n" + "=" * 70)
        print("                TOFF CALIBRATION RESULT")
        print("=" * 70)
        print(f"Standard energy   : {true_energy:.3f} eV")
        print(f"Current TOFF      : {toff:.9f} °")
        print(f"New TOFF          : {new_toff:.9f} °")
        print(f"Correction needed : {delta:+.9f} °")
        print("\nTo apply (if TOFF is a PV):")
        print(f"   caput {TOFF_PV} {new_toff:.9f}")
        print("\nOr update config_dict.py theta_offset[1] to the new value.")
        print("=" * 70)
except ValueError as ve:
    print(ve)
except Exception:
    print("Invalid input, skipping calibration.")

print("\nDone!\n")
