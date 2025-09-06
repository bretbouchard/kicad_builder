"""
BOM Generator (US-9 Implementation)
Generates normalized BOM with manufacturer/supplier data from lib_map
"""
import csv
from pathlib import Path
from typing import List, Dict, Optional, TypedDict
from tools.lib_map import get_part_info  # Absolute import path

class Component(TypedDict):
    Ref: str
    Value: str
    Footprint: str
    Part: str

class ComponentGroup(TypedDict):
    refs: List[str]
    value: str
    footprint: str
    mpn: Optional[str]
    manufacturer: Optional[str]
    supplier: Optional[str]
    supplier_pn: Optional[str]

def generate_bom(netlist_path: str, output_dir: str = "out") -> str:
    """Main BOM generation function meeting US-9 requirements"""
    components = parse_netlist(netlist_path)
    normalized = normalize_components(components)
    return write_bom_csv(normalized, output_dir)

def parse_netlist(netlist_path: str) -> List[Component]:
    """Parse KiCad netlist into structured components"""
    components = []
    current: Dict[str, str] = {}
    
    with open(netlist_path) as f:
        for line in f:
            line = line.strip()
            if line == "$COMPONENT":
                current = {}
            elif line == "$ENDCOMPONENT":
                components.append(Component(
                    Ref=current.get("Ref", ""),
                    Value=current.get("Value", ""),
                    Footprint=current.get("Footprint", ""),
                    Part=current.get("Part", "")
                ))
            else:
                if " " in line:
                    key, value = line.split(" ", 1)
                    current[key] = value
    return components

def normalize_components(components: List[Component]) -> Dict[str, ComponentGroup]:
    """Group and enrich components with library data"""
    groups: Dict[str, ComponentGroup] = {}
    
    for comp in components:
        part_info = get_part_info(comp["Part"])
        key = (comp["Value"], comp["Footprint"])
        
        if key not in groups:
            groups[key] = ComponentGroup(
                refs=[],
                value=comp["Value"],
                footprint=comp["Footprint"],
                mpn=part_info.get("mpn"),
                manufacturer=part_info.get("manufacturer"),
                supplier=part_info.get("supplier"),
                supplier_pn=part_info.get("supplier_pn")
            )
            
        groups[key]["refs"].append(comp["Ref"])
    
    return groups

def write_bom_csv(groups: Dict[str, ComponentGroup], output_dir: str) -> str:
    """Write normalized BOM data to CSV file"""
    output_path = Path(output_dir) / "bom.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Reference", "Quantity", "Value", "Footprint",
            "MPN", "Manufacturer", "Supplier", "Supplier PN"
        ])
        writer.writeheader()
        
        for group in groups.values():
            writer.writerow({
                "Reference": ",".join(group["refs"]),
                "Quantity": len(group["refs"]),
                "Value": group["value"],
                "Footprint": group["footprint"],
                "MPN": group.get("mpn", ""),
                "Manufacturer": group.get("manufacturer", ""),
                "Supplier": group.get("supplier", ""),
                "Supplier PN": group.get("supplier_pn", "")
            })
    
    return str(output_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m tools.scripts.generate_bom <netlist> [output_dir]")
        sys.exit(1)
    
    bom_path = generate_bom(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "out")
    print(f"Generated BOM at: {bom_path}")
