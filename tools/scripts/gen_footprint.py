#!/usr/bin/env python3
"""
gen_footprint.py

Generate a simple parameterized QFN-56 footprint kicad_mod.

Usage:
  python3 gen_footprint.py --out path.kicad_mod --pad_w 0.45 --pad_l 0.9 --ep 4.4
"""

import argparse
from pathlib import Path


FOOT_TEMPLATE = """(module {name} (layer F.Cu) (tedit 00000000)
    (descr "Generated footprint — verify dimensions against datasheet")
    (tags "generated footprint")
    (attr smd)
    (fp_text reference U1 (at 0 -4.5) (layer F.SilkS))
    (fp_text value {name} (at 0 6.5) (layer F.Fab))
{pads}
{ep_vias}
{tent_note}
    {ep_pad}
{paste_fp}
{courtyard_fp}
)
"""


def make_pads(pad_w, pad_l, pitch=0.5, pads_per_side=14, pad_shape="rect"):
    pads = []
    half_span = (pads_per_side - 1) * pitch / 2.0
    # top pads 1..N
    for i in range(pads_per_side):
        x = -half_span + i * pitch
        x_str = f"{x:.2f}"
        half_str = f"{half_span:.2f}"
        pads.append(
            f"  (pad {i + 1} smd {pad_shape} (at {x_str} {half_str}) "
            f"(size {pad_w} {pad_l}) (layers F.Cu F.Paste F.Mask))"
        )
    # right side
    for i in range(pads_per_side):
        y = half_span - i * pitch
        y_str = f"{y:.2f}"
        half_str = f"{half_span:.2f}"
        pads.append(
            f"  (pad {pads_per_side + 1 + i} smd {pad_shape} (at {half_str} {y_str}) "
            f"(size {pad_l} {pad_w}) (layers F.Cu F.Paste F.Mask))"
        )
    # bottom
    for i in range(pads_per_side):
        x = half_span - i * pitch
        x_str = f"{x:.2f}"
        neg_half_str = f"{-half_span:.2f}"
        pads.append(
            f"  (pad {2 * pads_per_side + 1 + i} smd {pad_shape} (at {x_str} {neg_half_str}) "
            f"(size {pad_w} {pad_l}) (layers F.Cu F.Paste F.Mask))"
        )
    # left
    for i in range(pads_per_side):
        y = -half_span + i * pitch
        y_str = f"{y:.2f}"
        neg_half_str = f"{-half_span:.2f}"
        pads.append(
            f"  (pad {3 * pads_per_side + 1 + i} smd {pad_shape} (at {neg_half_str} {y_str}) "
            f"(size {pad_l} {pad_w}) (layers F.Cu F.Paste F.Mask))"
        )
    return "\n".join(pads)


def make_ep(ep, ep_shape="rect"):
    if ep_shape == "round":
        return f'  (pad "EP" smd circle (at 0 0) (size {ep} {ep}) (layers F.Cu F.Paste F.Mask) (thermal))'
    else:
        return f'  (pad "EP" smd rect (at 0 0) (size {ep} {ep}) (layers F.Cu F.Paste F.Mask) (thermal))'


def make_paste_fp(ep, paste_reduction=0.0, ep_shape="rect"):
    # return an fp for paste mask if reduction requested (simple approach)
    if paste_reduction <= 0:
        return ""
    size = max(0.0, ep - paste_reduction)
    if ep_shape == "round":
        return f'  (pad "EP_PASTE" smd circle (at 0 0) (size {size:.2f} {size:.2f}) (layers F.Paste))'
    return f'  (pad "EP_PASTE" smd rect (at 0 0) (size {size:.2f} {size:.2f}) (layers F.Paste))'


def make_ep_vias(
    ep,
    via_pitch=1.5,
    via_drill=0.3,
    via_diameter=0.6,
    margin=0.5,
    pattern="grid",
):
    """Generate EP thermal vias inside the exposed pad.

    Vias are placed either on a square grid or a hex pattern inside the
    exposed pad area reduced by `margin` on each side. Returns a string
    containing KiCad thru-hole pad definitions for the vias.
    """
    # area available inside EP after margin
    avail = max(0.0, ep - 2 * margin)
    if avail <= 0:
        return ""

    positions = []
    if pattern == "grid":
        # compute counts that will fit in the available space
        count = max(1, int((avail + 1e-6) // via_pitch))
        if count == 1:
            positions = [(0.0, 0.0)]
        else:
            start = -(((count - 1) * via_pitch) / 2.0)
            for i in range(count):
                for j in range(count):
                    x = start + i * via_pitch
                    y = start + j * via_pitch
                    positions.append((x, y))
    else:
        # hex pattern: vertical spacing is pitch * sqrt(3)/2

        y_pitch = via_pitch * 0.8660254037844386
        nx = max(1, int((avail + 1e-6) // via_pitch))
        ny = max(1, int((avail + 1e-6) // y_pitch))
        start_x = -(((nx - 1) * via_pitch) / 2.0)
        start_y = -(((ny - 1) * y_pitch) / 2.0)
        for row in range(ny):
            row_offset = (via_pitch / 2.0) if (row % 2 == 1) else 0.0
            for col in range(nx):
                x = start_x + col * via_pitch + row_offset
                y = start_y + row * y_pitch
                if abs(x) <= avail / 2.0 and abs(y) <= avail / 2.0:
                    positions.append((x, y))

    pads = []
    idx = 1
    for x, y in positions:
        x_str = f"{x:.2f}"
        y_str = f"{y:.2f}"
        dia_str = f"{via_diameter:.2f}"
        drill_str = f"{via_drill:.2f}"
        pads.append(
            (
                f"  (pad EP_VIA_{idx} thru_hole circle (at {x_str} {y_str}) "
                f"(size {dia_str} {dia_str}) "
                f"(drill {drill_str}) (layers *.Cu *.Mask))"
            )
        )
        idx += 1
    return "\n".join(pads)


def make_courtyard(ep, half_span, courtyard=0.5):
    # draws a rectangle around the device on F.CrtYd
    extent = max(half_span, ep / 2.0) + courtyard
    x1 = -extent
    x2 = extent
    y1 = -extent
    y2 = extent
    w = 0.15
    lines = []
    lines.append(f"  (fp_line (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y1:.2f}) (layer F.CrtYd) (width {w}))")
    lines.append(f"  (fp_line (start {x2:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (layer F.CrtYd) (width {w}))")
    lines.append(f"  (fp_line (start {x2:.2f} {y2:.2f}) (end {x1:.2f} {y2:.2f}) (layer F.CrtYd) (width {w}))")
    lines.append(f"  (fp_line (start {x1:.2f} {y2:.2f}) (end {x1:.2f} {y1:.2f}) (layer F.CrtYd) (width {w}))")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument(
        "--name",
        default="REPO-MCU-QFN56",
        help="Module name to use in the kicad_mod",
    )
    p.add_argument("--pad_w", type=float, default=0.45)
    p.add_argument("--pad_l", type=float, default=0.9)
    p.add_argument("--ep", type=float, default=4.4)
    p.add_argument(
        "--pitch",
        type=float,
        default=0.5,
        help="Pad center-to-center pitch",
    )
    p.add_argument(
        "--pads_per_side",
        type=int,
        default=14,
        help="Number of pads per side",
    )
    p.add_argument(
        "--pad_shape",
        choices=["rect", "oval", "round"],
        default="rect",
    )
    p.add_argument(
        "--ep_shape",
        choices=["rect", "round"],
        default="rect",
    )
    p.add_argument(
        "--paste_reduction",
        type=float,
        default=0.0,
        help="Paste reduction in mm for EP",
    )
    p.add_argument(
        "--courtyard",
        type=float,
        default=0.5,
        help="Courtyard margin in mm",
    )
    p.add_argument(
        "--ep_via_pitch",
        type=float,
        default=1.5,
        help="Pitch between EP thermal vias in mm",
    )
    p.add_argument(
        "--ep_via_drill",
        type=float,
        default=0.3,
        help="Drill diameter for EP vias in mm",
    )
    p.add_argument(
        "--ep_via_dia",
        type=float,
        default=0.6,
        help="Finished diameter for EP vias in mm",
    )
    p.add_argument(
        "--ep_via_margin",
        type=float,
        default=0.5,
        help="Margin from EP edge where vias are not placed",
    )
    p.add_argument(
        "--ep_via_pattern",
        choices=["grid", "hex"],
        default="grid",
        help="Via placement pattern inside EP",
    )
    p.add_argument(
        "--ep_via_tenting",
        choices=["none", "top", "both"],
        default="none",
        help="Suggest via tenting for EP (note only)",
    )
    p.add_argument(
        "--no-ep-vias",
        dest="no_ep_vias",
        action="store_true",
        help="Do not generate EP thermal vias",
    )
    args = p.parse_args()
    pads = make_pads(
        args.pad_w,
        args.pad_l,
        pitch=args.pitch,
        pads_per_side=args.pads_per_side,
        pad_shape=args.pad_shape,
    )
    half_span = (args.pads_per_side - 1) * args.pitch / 2.0
    ep_pad = make_ep(args.ep, ep_shape=args.ep_shape)
    paste_fp = make_paste_fp(
        args.ep,
        paste_reduction=args.paste_reduction,
        ep_shape=args.ep_shape,
    )
    courtyard_fp = make_courtyard(args.ep, half_span, courtyard=args.courtyard) if args.courtyard > 0 else ""
    ep_vias = (
        ""
        if args.no_ep_vias
        else make_ep_vias(
            args.ep,
            via_pitch=args.ep_via_pitch,
            via_drill=args.ep_via_drill,
            via_diameter=args.ep_via_dia,
            margin=args.ep_via_margin,
            pattern=args.ep_via_pattern,
        )
    )
    # add a small user text note about tenting preference for human reviewers
    tent_note = ""
    if args.ep_via_tenting != "none":
        tent_y = -args.ep / 2 - 1.0
        tent_note = ('  (fp_text user "EP_VIA_TENT={}" (at 0 {}) (layer F.Fab))\n').format(args.ep_via_tenting, tent_y)
        # prefer placing note before courtyard/paste for visibility
        if courtyard_fp:
            courtyard_fp = tent_note + courtyard_fp
        else:
            paste_fp = tent_note + paste_fp
    content = FOOT_TEMPLATE.format(
        name=args.name,
        pads=pads,
        ep_pad=ep_pad,
        paste_fp=paste_fp,
        courtyard_fp=courtyard_fp,
        ep_vias=ep_vias,
        tent_note=tent_note,
    )
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(content)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
