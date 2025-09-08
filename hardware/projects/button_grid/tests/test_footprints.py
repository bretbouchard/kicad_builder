from tools.scripts.kicad_mod import KicadMod


def test_apa102_footprint() -> None:
    """Validate APA102-2020 footprint against datasheet specifications"""
    mod: KicadMod = KicadMod.from_file("inbox/APA-102-2020-256-8/LED_APA-102-2020-256-8.kicad_mod")

    # Physical dimensions (page 3 of datasheet) with courtyard clearance
    # Original X: 2.0±0.1mm + 0.25 clearance per side = 2.5±0.1mm total
    assert 2.4 <= mod.size[0] <= 2.6, f"Courtyard X {mod.size[0]}mm invalid (expected 2.5±0.1mm)"
    # Original Y: 2.0±0.1mm + 0.25 clearance per side = 2.5±0.1mm total
    assert 2.4 <= mod.size[1] <= 2.6, f"Courtyard Y {mod.size[1]}mm invalid (expected 2.5±0.1mm)"

    # Key pad verification
    vcc_pads = [p for p in mod.pads if p.name in ["1", "4"]]
    assert len(vcc_pads) == 2, "Missing VCC pads"
    data_pads = [p for p in mod.pads if any(n in p.name for n in ["2_1", "2_2"])]
    assert len(data_pads) >= 2, "Insufficient data/clock pads"

    # Thermal requirements
    thermal_pads = [p for p in mod.pads if p.name in ["5_1", "5_2"]]
    thermal_area = sum(p.size[0] * p.size[1] for p in thermal_pads)
    assert thermal_area >= 1.0, "Thermal pads too small (min 1.0mm² total)"

    # Clearance checks
    for p in mod.pads:
        adjacent = [op for op in mod.pads if op != p]
        for op in adjacent:
            dx = p.position[0] - op.position[0]
            dy = p.position[1] - op.position[1]
            distance = (dx**2 + dy**2) ** 0.5
            assert distance >= 0.2, f"{p.name}-{op.name}: {distance:.2f}mm < 0.2mm"

    # Manufacturing specs
    paste_layers_present = any("F.Paste" in p.layers for p in mod.pads)
    assert paste_layers_present, "Missing F.Paste layers in pad layers"

    target_clearance = 0.25
    assert 0.24 <= mod.courtyard_clearance <= 0.26, (
        f"Courtyard clearance {mod.courtyard_clearance:.3f}mm invalid " f"(should be {target_clearance}±0.01mm)"
    )
