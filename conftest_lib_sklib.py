from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

conftest_lib = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'RP2040', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'RP2040'}), 'ref_prefix':'U', 'fplist':['Package_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP5.5x5.5mm'], 'footprint':'Package_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP5.5x5.5mm', 'keywords':'', 'description':'', 'datasheet':'https://datasheets.raspberrypi.org/rp2040/rp2040-datasheet.pdf', 'pins':[
            Pin(num='1',name='VCC',func=pin_types.PWRIN),
            Pin(num='2',name='GND',func=pin_types.PWRIN),
            Pin(num='4',name='VBUS',func=pin_types.PWRIN),
            Pin(num='9',name='RESET',func=pin_types.INPUT),
            Pin(num='3',name='GPIO0',func=pin_types.BIDIR),
            Pin(num='5',name='GPIO1',func=pin_types.BIDIR),
            Pin(num='6',name='GPIO2',func=pin_types.BIDIR),
            Pin(num='7',name='GPIO3',func=pin_types.BIDIR),
            Pin(num='8',name='GPIO4',func=pin_types.BIDIR),
            Pin(num='10',name='SWDIO',func=pin_types.BIDIR),
            Pin(num='11',name='SWCLK',func=pin_types.BIDIR)], 'unit_defs':[] })])