# Hardware Bring-Up Test Plan

## Initial Power-Up
1. Verify 5V supply within 5% tolerance.
2. Check quiescent current < 50mA before enabling drivers.

## LED Matrix
1. Verify each row/column lights correctly at nominal current.
2. Measure voltage drop and total current vs spec.

## Capacitive Touch
1. Baseline capacitance measurement at startup.
2. Verify signal-to-noise ratio above threshold during touch.

## Expansion
- Add new test steps here when modules or rules change.
