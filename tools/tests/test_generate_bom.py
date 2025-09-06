import subprocess
from pathlib import Path

def test_generate_bom_creates_csv(tmp_path):
    # Create test netlist
    netlist = tmp_path / "test.net"
    netlist.write_text("""$COMPONENT
Ref C1
Value 100nF
Footprint C_0603
Part CAP-0603
$ENDCOMPONENT
$COMPONENT
Ref R1
Value 1k
Footprint R_0603
Part RES-0603
$ENDCOMPONENT""")

    output_dir = tmp_path / "bom_output"
    
    # Run generator
    subprocess.check_call([
        "python", 
        "-m", "tools.scripts.generate_bom",
        str(netlist),
        str(output_dir)
    ])
    
    # Verify output
    bom_file = output_dir / "bom.csv"
    assert bom_file.exists(), "BOM file not created"
    
    content = bom_file.read_text()
    assert "C1" in content, "Capacitor not in BOM"
    assert "R1" in content, "Resistor not in BOM"
    assert "Kemet" in content, "Manufacturer data missing"
    assert "Panasonic" in content, "Manufacturer data missing"
