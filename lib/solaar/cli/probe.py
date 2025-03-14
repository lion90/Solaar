## Copyright (C) 2020
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from logitech_receiver import base
from logitech_receiver.common import strhex
from logitech_receiver.hidpp10_constants import ErrorCode
from logitech_receiver.hidpp10_constants import Registers

from solaar.cli.show import _print_device
from solaar.cli.show import _print_receiver


def run(receivers, args, find_receiver, _ignore):
    assert receivers

    if args.receiver:
        receiver_name = args.receiver.lower()
        receiver = find_receiver(receivers, receiver_name)
        if not receiver:
            raise Exception(f"no receiver found matching '{receiver_name}'")
    else:
        receiver = receivers[0]

    assert receiver is not None

    if receiver.isDevice:
        _print_device(receiver, 1)
        return

    _print_receiver(receiver)

    print("")
    print("  Register Dump")
    rgst = receiver.read_register(Registers.NOTIFICATIONS)
    print("    Notifications         %#04x: %s" % (Registers.NOTIFICATIONS % 0x100, f"0x{strhex(rgst)}" if rgst else "None"))
    rgst = receiver.read_register(Registers.RECEIVER_CONNECTION)
    print(
        "    Connection State      %#04x: %s"
        % (Registers.RECEIVER_CONNECTION % 0x100, f"0x{strhex(rgst)}" if rgst else "None")
    )
    rgst = receiver.read_register(Registers.DEVICES_ACTIVITY)
    print(
        "    Device Activity       %#04x: %s" % (Registers.DEVICES_ACTIVITY % 0x100, f"0x{strhex(rgst)}" if rgst else "None")
    )

    for sub_reg in range(0, 16):
        rgst = receiver.read_register(Registers.RECEIVER_INFO, sub_reg)
        print(
            "    Pairing Register %#04x %#04x: %s"
            % (Registers.RECEIVER_INFO % 0x100, sub_reg, f"0x{strhex(rgst)}" if rgst else "None")
        )
    for device in range(0, 7):
        for sub_reg in [0x10, 0x20, 0x30, 0x50]:
            rgst = receiver.read_register(Registers.RECEIVER_INFO, sub_reg + device)
            print(
                "    Pairing Register %#04x %#04x: %s"
                % (Registers.RECEIVER_INFO % 0x100, sub_reg + device, f"0x{strhex(rgst)}" if rgst else "None")
            )
        rgst = receiver.read_register(Registers.RECEIVER_INFO, 0x40 + device)
        print(
            "    Pairing Name     %#04x %#02x: %s"
            % (Registers.RECEIVER_INFO % 0x100, 0x40 + device, rgst[2 : 2 + ord(rgst[1:2])] if rgst else "None")
        )
        for part in range(1, 4):
            rgst = receiver.read_register(Registers.RECEIVER_INFO, 0x60 + device, part)
            print(
                "    Pairing Name     %#04x %#02x %#02x: %2d %s"
                % (
                    Registers.RECEIVER_INFO % 0x100,
                    0x60 + device,
                    part,
                    ord(rgst[2:3]) if rgst else 0,
                    rgst[3 : 3 + ord(rgst[2:3])] if rgst else "None",
                )
            )
    for sub_reg in range(0, 5):
        rgst = receiver.read_register(Registers.FIRMWARE, sub_reg)
        print(
            "    Firmware         %#04x %#04x: %s"
            % (Registers.FIRMWARE % 0x100, sub_reg, f"0x{strhex(rgst)}" if rgst is not None else "None")
        )

    print("")
    for reg in range(0, 0xFF):
        for offset, reg_type in [(0x00, "Short"), (0x200, "Long")]:
            last = None
            for sub in range(0, 0xFF):
                rgst = base.request(receiver.handle, 0xFF, 0x8100 | (offset + reg), sub, return_error=True)
                if isinstance(rgst, int) and rgst == ErrorCode.INVALID_ADDRESS:
                    break
                elif isinstance(rgst, int) and rgst == ErrorCode.INVALID_VALUE:
                    continue
                else:
                    if not isinstance(last, bytes) or not isinstance(rgst, bytes) or last != rgst:
                        print(
                            "    Register %s   %#04x %#04x: %s"
                            % (reg_type, reg, sub, "0x" + strhex(rgst) if isinstance(rgst, bytes) else str(rgst))
                        )
                last = rgst
