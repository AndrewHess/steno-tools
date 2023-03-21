"""Combine JSON files in a directory into a single JSON file."""

import argparse
import json
import os
import sys


def combine_json_files_directory(directory, force_overwrite=False):
    """Combine all JSON files in a directory into a single JSON file.

    The created file is named <directory>.json.

    Args:
        directory: The name of a directory.
        force_overwrite: True if the output file should be written even if it
            already exists. If the file doesn't already exist, this parameter
            doesn't do anything.

    Raises:
        ValueError: If the input argument is not a directory.

    Returns:
        None
    """

    if not os.path.isdir(directory):
        raise ValueError(f"`{directory}` is not a directory")

    json_files = [
        os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".json")
    ]

    if not json_files:
        print(f"No JSON files found in directory `{directory}`", file=sys.stderr)

    # Check if the output file already exists.
    new_filename = os.path.basename(directory) + ".json"

    if not force_overwrite and os.path.exists(new_filename):
        # If the file exists, prompt the user before overwriting it
        response = input(
            f"The file {new_filename} already exists. Do you want to overwrite it? (y/n) "
        )
        if response.lower() != "y":
            print(f"{new_filename} not overwritten.")
            return

    # Combine contents of JSON files.
    combined_json = {}
    for file in json_files:
        with open(file, "r", encoding="UTF-8") as file:
            file_contents = json.load(file)
            combined_json.update(file_contents)

    # Write the combined JSON a file.
    with open(new_filename, "w+", encoding="UTF-8") as file:
        json.dump(combined_json, file)
        print(f"{new_filename} written successfully.")


def main():
    """Main function that calls combine_json_files_directory."""

    parser = argparse.ArgumentParser(
        description="Combine all JSON files in a directory into a single JSON file."
    )
    parser.add_argument("directory", help="The directory containing JSON files to be combined.")
    parser.add_argument(
        "-f", "--force", action="store_true", help="force overwriting the output file"
    )
    args = parser.parse_args()

    combine_json_files_directory(args.directory, force_overwrite=args.force)


if __name__ == "__main__":
    main()
