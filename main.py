#!/usr/bin/env python3
"""Entry program for news-image-20261126.

Validates the bundled image (a whole PNG, at most 1 MiB and at most
1024 by 1024 pixels) and copies it to the output directory as entry.png.
Standard library only, no network, fully deterministic: the output bytes
are always exactly the bytes shipped in this repository.
"""

import os
import struct
import sys

MAX_BYTES = 1048576
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_png_size(data):
    """Return (width, height) from a PNG's IHDR chunk, or None."""
    if len(data) < 33 or data[:8] != PNG_MAGIC:
        return None
    if data[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, "entry.png")

    try:
        with open(source, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        print("cannot read entry.png: %s" % exc, file=sys.stderr)
        return 1

    if len(data) > MAX_BYTES:
        print("entry.png is %d bytes, over the 1 MiB limit" % len(data),
              file=sys.stderr)
        return 1

    size = read_png_size(data)
    if size is None:
        print("entry.png is not a whole PNG file", file=sys.stderr)
        return 1
    width, height = size
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        print("entry.png is %dx%d, over the 1024x1024 limit"
              % (width, height), file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    with open(target, "wb") as handle:
        handle.write(data)
    print("wrote %s (%dx%d, %d bytes)" % (target, width, height, len(data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
