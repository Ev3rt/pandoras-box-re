#!/usr/bin/env python3

"""
This script packs a directory into a ROF file.
"""

import os
import sys
from io import BufferedWriter


def main() -> None:
    """Entry point of the script"""
    # Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: pack-rof.py <path to input> <path to ROF file>")
        return

    if not os.path.isdir(sys.argv[1]):
        print("Error: input path does not exist.")
        return

    # Parse the ROF file
    with open(sys.argv[2], "wb") as rof_file:
        add_directory(rof_file, sys.argv[1])


def add_directory(file: BufferedWriter, directory: str) -> int:
    """Add a directory and its files, subdirectories and metadata to the given file"""
    # Immediately save the current offset for inclusion in metadata of parent directory
    directory_offset = file.tell()

    # Collect subdirectories and files
    items = sorted([f for f in os.listdir(directory)])

    # Build metadata
    # First integer: number of items in the directory
    write_i32(file, len(items))

    # Second integer: length of the name table (add one to each name for the null terminator)
    name_table_size = sum([len(f) + 1 for f in items])
    write_i32(file, name_table_size)

    # The new name table starts at position 0
    name_table_offset = 0

    # Keep track of file names and the position where their offset is stored, so we can fill those in later
    item_offset_map = {}

    # Generate metadata
    for name in items:
        full_path = os.path.join(directory, name)
        name_length = len(name) + 1
        name_offset = name_table_offset
        name_table_offset += name_length

        if os.path.isdir(full_path):
            # Directory has size 0, type 1
            size = 0
            type = 1
        else:
            # File has type 1
            size = os.path.getsize(full_path)
            type = 0

        # Store the offset position so we can fill it in later
        item_offset_map[name] = file.tell()

        # Append metadata
        write_i32(file, 0)
        write_i32(file, size)
        write_i32(file, type)
        write_i32(file, name_length)
        write_i32(file, name_offset)

    # Generate name table
    for name in items:
        write_string(file, name)
        write_null(file)

    for name in items:
        full_path = os.path.join(directory, name)
        if os.path.isdir(full_path):
            # Add subdirectory and get the offset it is stored at
            subdirectory_offset = add_directory(file, full_path)

            # Save the current offset
            current_offset = file.tell()

            # Overwrite the zero value with the actual offset of the subdirectory
            file.seek(item_offset_map[name])
            write_i32(file, subdirectory_offset)

            # Restore the current offset
            file.seek(current_offset)
        else:
            # Process files
            # Add file and get the offset it is stored at
            file_offset = append_file(file, full_path)

            # Save the current offset
            current_offset = file.tell()

            # Overwrite the zero value with the actual offset of the subdirectory
            file.seek(item_offset_map[name])
            write_i32(file, file_offset)

            # Restore the current offset
            file.seek(current_offset)

    # Return the offset of the directory's metadata
    return directory_offset


def write_i32(file: BufferedWriter, value: int) -> None:
    """Writes a 32-bit integer to the current seek in the given file."""
    file.write(value.to_bytes(4, byteorder="little"))


def write_string(file: BufferedWriter, value: str) -> None:
    """Writes a given string to the current seek in the given file."""
    file.write(value.encode("ascii"))


def write_null(file: BufferedWriter) -> None:
    """Writes a null byte to the current seek in the given file."""
    file.write(b"\x00")


def append_file(file: BufferedWriter, path: str) -> int:
    """Appends another file to the current seek in the given file."""
    # Immediately save the current offset for inclusion in metadata of parent directory
    file_offset = file.tell()

    # Open the file to append and write its contents to the open file
    with open(path, "rb") as other_file:
        file.write(other_file.read())

    # Return the offset at which the file data is stored
    return file_offset


if __name__ == "__main__":
    main()
