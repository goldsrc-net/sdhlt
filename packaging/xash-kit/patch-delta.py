#!/usr/bin/env python3
"""Widen the entity origins of a mod's delta.lst so that entities past +/-4096 reach clients where they are.

    patch-delta.py <delta.lst in> <delta.lst out>

Half-Life's delta.lst sends an entity's origin in 16 bits at a scale of 8 (+/-4096), a player's in 18 at 32
(+/-4096), a custom entity's in 17 at 8 (+/-8192) and an event's (a shot, a step, an impact) in 16 at 8
(+/-4096). Past that it arrives wrapped: the server has the entity where it is, so it collides and is used
there, and the client draws it somewhere else. This gives each 3 bits more, +/-32768, the range of
-worldextent's default: 19 at 8, 21 at 32, 20 at 8 and 19 at 8. Nothing else in the file changes, its line
endings included. It refuses a file that does not have the twelve lines it expects, so that a mod's own
delta.lst is looked at.
"""
import re
import sys

WIDER = {
    ("entity_state_t", "16, 8.0"): "19, 8.0",
    ("entity_state_player_t", "18, 32.0"): "21, 32.0",
    ("custom_entity_state_t", "17, 8.0"): "20, 8.0",
    ("event_t", "16, 8.0"): "19, 8.0",
}
EXPECTED = 12


def main(source, target):
    text = open(source, "rb").read().decode("latin-1")
    lines = text.splitlines(keepends=True)
    block, changed = None, 0
    for i, line in enumerate(lines):
        header = re.match(r"^(\w+)\s+\S+.*_Encode", line) or re.match(r"^(\w+)\s+none\b", line)
        if header:
            block = header.group(1)
        if "origin[" not in line or block is None:
            continue
        for (name, old), new in WIDER.items():
            if block == name and old in line:
                lines[i] = line.replace(old, new)
                changed += 1
                break
    if changed != EXPECTED:
        sys.exit(f"{source}: {changed} origin lines matched, not {EXPECTED}: change it by hand (the kit's README lists them)")
    open(target, "wb").write("".join(lines).encode("latin-1"))
    print(f"{target}: {changed} origin lines widened")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
