#!/usr/bin/env python3
"""
Convert a PNG sprite to 4-bit indexed format required by gbagfx.

Usage:
    python3 tools/convert_sprite.py graphics/object_events/pics/people/merchant.png

The file is converted in-place. Edit your sprite in any image editor,
then run this before 'make'. Requires pypng (pip install pypng).
"""

import sys
import png


def convert_to_4bit(path):
    r = png.Reader(filename=path)
    w, h, rows, info = r.read()
    rows = list(rows)

    palette = info.get('palette')
    if palette is None:
        print(f"ERROR: {path} is not an indexed (palette) PNG.")
        print("In GIMP: Image → Mode → Indexed, max 16 colors, then export.")
        sys.exit(1)

    if len(palette) > 16:
        print(f"ERROR: {path} has {len(palette)} colors — max is 16.")
        print("In GIMP: Image → Mode → Indexed, max 16 colors, then export.")
        sys.exit(1)

    if info.get('bitdepth') == 4:
        print(f"{path}: already 4-bit, nothing to do.")
        return

    # Write back as 4-bit indexed
    writer = png.Writer(width=w, height=h, palette=palette, bitdepth=4)
    with open(path, 'wb') as f:
        writer.write(f, rows)

    print(f"{path}: converted {info['bitdepth']}-bit → 4-bit ({len(palette)} colors).")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 tools/convert_sprite.py <sprite.png>")
        sys.exit(1)
    for path in sys.argv[1:]:
        convert_to_4bit(path)
