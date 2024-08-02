#!/usr/bin/env python3

"""
This script prints the metadata of a Focus Point puzzle (.ZOO file).
"""

import os
import sys
from io import BufferedReader


def main() -> None:
    """Entry point of the script"""
    # Check command-line arguments
    if len(sys.argv) != 2:
        print("Usage: dump-fpn-metadata.py <path to Focus Point ZOO file>")
        return

    if not os.path.isfile(sys.argv[1]):
        print("Error: first argument should be a path to a ZOO file.")
        return

    with open(sys.argv[1], "rb") as file:
        parse_metadata(file)


def parse_metadata(file: BufferedReader) -> None:
    """Prints the integers in range 0x088...0x3A0"""
    file.seek(0x88)
    for i in range(198): # 792 bytes / 4 bytes per integer
        print(f"{read_i32(file)}\t", end="")
        # Print a maximum of 8 values per line
        if i % 8 == 7:
            print()


def read_i32(file: BufferedReader) -> int:
    """Reads a 32-bit integer from the current seek in the given file."""
    return int.from_bytes(file.read(4), byteorder="little")


if __name__ == "__main__":
    main()