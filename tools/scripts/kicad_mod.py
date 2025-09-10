import re
from dataclasses import dataclass
from typing import List


@dataclass
class Pad:
    name: str
    type: str
    shape: str
    position: tuple[float, float]
    size: tuple[float, float]
    layers: List[str]


@dataclass
class KicadMod:
    name: str
    pads: List[Pad]
    size: tuple[float, float]
    courtyard_clearance: float

    @classmethod
    def from_file(cls, path: str) -> "KicadMod":
        with open(path) as f:
            content = f.read()

        # Parse module name
        name_match = re.search(r'\(footprint "(.*?)"', content)
        name: str = name_match.group(1) if name_match else ""

        # Parse pads
        pads: List[Pad] = []
        pad_re = re.compile(
            r"\(pad \"?(.+?)\"? [^\(]*\(at ([\d\.\-]+) ([\d\.\-]+)\)" r"[^\(]*\(size ([\d\.\-]+) ([\d\.\-]+)\)"
        )
        for match in pad_re.findall(content):
            pads.append(
                Pad(
                    name=match[0],
                    type="smd" if "smd" in match else "tht",
                    shape="rect",
                    position=(float(match[1]), float(match[2])),
                    size=(float(match[3]), float(match[4])),
                    layers=["F.Cu", "F.Mask", "F.Paste"],
                )
            )

        # Parse courtyard clearance
        # Fixed regex to properly handle nested parentheses in KiCad format
        courtyard_lines = re.findall(
            r"""(?x)
            \(fp_line
            \s+ \(start \s+ ([\d\.-]+) \s+ ([\d\.-]+)\)  # Start coords
            \s+ \(end \s+ ([\d\.-]+) \s+ ([\d\.-]+)\)     # End coords
            \s+ \(layer \s+ F\.CrtYd \)                  # Layer after coordinates
            \s+ \(width \s+ [\d\.-]+ \)                  # Width parameter
            """,
            content,
            re.DOTALL,
        )

        # Process coordinates with correct indices
        x_coords: List[float] = []
        y_coords: List[float] = []
        for line in courtyard_lines:
            x1 = float(line[0])
            y1 = float(line[1])
            x2 = float(line[2])
            y2 = float(line[3])
            x_coords.extend([x1, x2])
            y_coords.extend([y1, y2])

        if not x_coords or not y_coords:
            raise ValueError("No valid F.CrtYd courtyard boundaries found")

        # Direct courtyard measurement (no added clearance)
        size_x = round(max(x_coords) - min(x_coords), 2)
        size_y = round(max(y_coords) - min(y_coords), 2)

        return cls(
            name=name,
            pads=pads,
            size=(size_x, size_y),
            courtyard_clearance=0.25,
        )
