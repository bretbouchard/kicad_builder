import os
from skidl import Part, Net, ERC, generate_netlist


def _set_stub_symbol_env() -> None:
    symbol_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/symbols"))
    os.environ["KICAD6_SYMBOL_DIR"] = symbol_dir
    os.environ["KICAD8_SYMBOL_DIR"] = symbol_dir
    os.environ["KICAD_SYMBOL_DIR"] = symbol_dir
    # Confirm MCU.kicad_sym exists
    mcu_path = os.path.join(symbol_dir, "MCU.kicad_sym")
    if not os.path.isfile(mcu_path):
        print("WARNING: MCU.kicad_sym not found in KICAD symbol dir.")


def test_mcu_erc_with_stub() -> None:
    _set_stub_symbol_env()
    u = Part("RP2040", "RP2040", tool="kicad8")
    vcc = Net("VCC")
    gnd = Net("GND")
    u[1] += vcc
    u[2] += gnd
    ERC()
    generate_netlist()


def test_mcu_erc_missing_connection() -> None:
    _set_stub_symbol_env()
    u = Part("RP2040", "RP2040", tool="kicad8")
    vcc = Net("VCC")
    u[1] += vcc
    ERC()


def test_mcu_erc_no_connections() -> None:
    _set_stub_symbol_env()
    _ = Part("RP2040", "RP2040", tool="kicad8")
    ERC()
