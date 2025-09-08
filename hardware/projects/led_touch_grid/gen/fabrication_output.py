#!/usr/bin/env python3
"""
Fabrication Output Generation System for LED Touch Grid

Implements:
- Automated Gerber, drill, and pick-and-place file generation using KiCad CLI
- DRC validation using KiCad CLI
- BOM generation with part numbers, quantities, supplier info (via KiCad BOM plugin or CLI)
- DAID metadata injection for traceability (git SHA, timestamp, versions)
- Output completeness and accuracy validation

Outputs:
- out/led_touch_grid/fabrication/gerber/
- out/led_touch_grid/fabrication/drill/
- out/led_touch_grid/fabrication/pnp.csv
- out/led_touch_grid/fabrication/bom.csv
- out/led_touch_grid/fabrication/daid_metadata.json

Requires:
- kicad-cli (KiCad 7+)
- git (for SHA)
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_kicad_cli(args, cwd=None):
    """Run a kicad-cli command and return output, raise on error."""
    result = subprocess.run(
        ["kicad-cli"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"kicad-cli {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout


def get_git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "UNKNOWN"


class FabricationOutputBuilder:
    """
    Fabrication output generation system for LED Touch Grid.
    """

    def __init__(self, project_name: str = "led_touch_grid"):
        self.project_name = project_name
        self.out_dir = Path("out") / project_name / "fabrication"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.kicad_pcb = Path("out") / project_name / f"{project_name}.kicad_pcb"

    def _generate_gerbers(self):
        """Generate Gerber files using KiCad CLI."""
        gerber_dir = self.out_dir / "gerber"
        gerber_dir.mkdir(parents=True, exist_ok=True)
        run_kicad_cli(["pcb", "export", "gerbers", str(self.kicad_pcb), "--output", str(gerber_dir)])
        if not any(gerber_dir.glob("*.gbr")):
            raise RuntimeError("No Gerber files generated!")

    def _generate_drill_files(self):
        """Generate drill files using KiCad CLI."""
        drill_dir = self.out_dir / "drill"
        drill_dir.mkdir(parents=True, exist_ok=True)
        run_kicad_cli(["pcb", "export", "drill", str(self.kicad_pcb), "--output", str(drill_dir)])
        if not any(drill_dir.glob("*.drl")):
            raise RuntimeError("No drill files generated!")

    def _generate_pick_and_place(self):
        """Generate pick-and-place CSV using KiCad CLI."""
        pnp_csv = self.out_dir / "pnp.csv"
        run_kicad_cli(["pcb", "export", "pos", str(self.kicad_pcb), "--output", str(pnp_csv)])
        if not pnp_csv.exists():
            raise RuntimeError("Pick-and-place file not generated!")

    def _run_drc_validation(self):
        """Run DRC validation using KiCad CLI."""
        drc_report = self.out_dir / "drc_report.txt"
        out = run_kicad_cli(["pcb", "drc", str(self.kicad_pcb)])
        drc_report.write_text(out)

    def _generate_bom(self):
        """Generate BOM CSV using KiCad CLI."""
        bom_csv = self.out_dir / "bom.csv"
        run_kicad_cli(["sch", "export", "bom", str(self.kicad_pcb.with_suffix(".kicad_sch")), "--output", str(bom_csv)])
        if not bom_csv.exists():
            raise RuntimeError("BOM file not generated!")

    def _inject_daid_metadata(self):
        """Inject DAID metadata (git SHA, timestamp, tool versions)."""
        meta = {
            "git_sha": get_git_sha(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tool_versions": {
                "python": sys.version,
                "generator": "fabrication_output.py",
                "kicad_cli": self._get_kicad_cli_version(),
            },
        }
        meta_json = self.out_dir / "daid_metadata.json"
        meta_json.write_text(json.dumps(meta, indent=2))

    def _get_kicad_cli_version(self):
        try:
            out = subprocess.check_output(["kicad-cli", "--version"]).decode().strip()
            return out
        except Exception:
            return "UNKNOWN"

    def _validate_outputs(self):
        """Validate output completeness and accuracy."""
        required = [
            self.out_dir / "gerber",
            self.out_dir / "drill",
            self.out_dir / "pnp.csv",
            self.out_dir / "bom.csv",
            self.out_dir / "daid_metadata.json",
        ]
        missing = [str(p) for p in required if not (p.exists() or (p.is_dir() and any(p.iterdir())))]
        if missing:
            raise RuntimeError(f"Missing fabrication outputs: {missing}")
        (self.out_dir / "validation_report.txt").write_text("All outputs present.\n")

    def build(self):
        self._run_drc_validation()
        self._generate_gerbers()
        self._generate_drill_files()
        self._generate_pick_and_place()
        self._generate_bom()
        self._inject_daid_metadata()
        self._validate_outputs()
        print(f"Fabrication outputs generated in {self.out_dir}")


def generate_fabrication_output(project_name: str = "led_touch_grid") -> None:
    builder = FabricationOutputBuilder(project_name=project_name)
    builder.build()
    print("Fabrication output generated.")


if __name__ == "__main__":
    generate_fabrication_output()
