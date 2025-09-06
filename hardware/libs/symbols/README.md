# Minimal KiCad Symbol Stubs for SKiDL Testing

This directory contains minimal .lib files for common symbols (C, R, U, LED, SW, J, PWR_FLAG, MCU) to allow SKiDL-based tests to instantiate Parts without requiring the full system KiCad symbol libraries. These are for test/dev use only.

To use in SKiDL, set the environment variable:

    export KICAD_SYMBOL_DIR=$(pwd)

and ensure SKiDL's lib_search_paths includes this directory.
