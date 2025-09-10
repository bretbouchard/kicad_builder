from skidl import SKIDL, TEMPLATE, Alias, Part, SchLib

SKIDL_lib_version = "0.0.1"

__init__ = SchLib(tool=SKIDL).add_parts(
    *[
        Part(
            **{
                "name": "RP2040",
                "dest": TEMPLATE,
                "tool": SKIDL,
                "aliases": Alias({"RP2040"}),
                "ref_prefix": "U",
                "fplist": None,
                "footprint": None,
                "keywords": "",
                "description": "",
                "datasheet": "https://datasheets.raspberrypi.org/rp2040/rp2040-datasheet.pdf",
            }
        )
    ]
)
