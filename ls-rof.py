#!/usr/bin/env python3

import os
import sys
from io import BufferedReader


def main() -> None:
    """Entry point of the script"""
    # Check command-line arguments
    if len(sys.argv) != 2:
        print("Usage: ls-rof.py <path to ROF file>")
        return

    if not os.path.isfile(sys.argv[1]):
        print("Error: first argument should be a path to a ROF file.")
        return

    # Read the ROF file and start parsing the first directory
    with open(sys.argv[1], "rb") as rof_file:
        parse_directory(rof_file, 0)


def read_i32(file: BufferedReader) -> int:
    """Reads a 32-bit integer from the current seek in the given file."""
    return int.from_bytes(file.read(4), byteorder="little")


def read_string(file: BufferedReader, length: int) -> str:
    """Reads a string of the given length from the current seek in the given file."""
    return file.read(length).decode("ascii")


def read_string_offset(file: BufferedReader, offset: int, length: int) -> str:
    """Reads a string of the given length from a given offset in the given file."""
    # Save the current offset
    previous_offset = file.tell()

    # Seek to the given offset
    file.seek(offset)

    # Read the actual string
    string = read_string(file, length)

    # Seek to the original offset
    file.seek(previous_offset)

    # Return the read string
    return string


def parse_directory(file: BufferedReader, offset: int, indent=0):
    """
    Reads metadata for the directory at the given offset. Recurses for every directory found
    and calls parse_file() for every file found.
    """
    # Directories found in the current directory
    directories = []
    # Files found in the current directory
    files = []

    # Seek to the start of the directory metadata
    file.seek(offset)

    # Read the number of entries in the directory
    item_count = read_i32(file)

    # Read the length of the file name table
    name_table_length = read_i32(file)

    # From here on there is 20 bytes of metadata for each item in the directory.
    # We can determine the name table offset by taking the current position and calculating the
    # size of the metadata in between.
    name_table_offset = file.tell() + item_count * 20

    for i in range(0, item_count):
        # First integer gives the start of the directory or file
        item_offset = read_i32(file)

        # Second integer gives the length of the directory (always zero) or file
        item_size = read_i32(file)

        # Third integer gives the type of the item (0 = file, 1 = directory)
        item_type = read_i32(file)

        # Fourth integer gives the length of the directory or file name
        # Subtract one to exclude the null terminator
        item_name_length = read_i32(file) - 1

        # The last integer gives the offset of the directory or file name in the name table
        item_name_offset = read_i32(file)

        # Read the directory or file name from the name table
        item_name = read_string_offset(
            file, name_table_offset + item_name_offset, item_name_length
        )

        # Parse the entry
        if item_type == 0:
            # File
            files.append((item_name, item_offset, item_size))
        elif item_type == 1:
            # Directory
            directories.append((item_name, item_offset, item_size))

    for dir_name, dir_offset, _ in directories:
        # Print directory name and recurse
        print(f"{'  ' * indent}{dir_name}:")
        parse_directory(file, dir_offset, indent + 1)

    for file_name, file_offset, file_size in files:
        # Print file name
        print(f"{'  ' * (indent + 1)}{file_name}")
        parse_file(file, file_offset, file_size)


def parse_file(file: BufferedReader, offset: int, size: int):
    """TODO"""
    pass


if __name__ == "__main__":
    main()
