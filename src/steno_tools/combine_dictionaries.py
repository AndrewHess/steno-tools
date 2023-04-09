"""Combine JSON files in a directory into a single JSON file."""

import json
import logging
import os
import re

from steno_tools import utils


def natural_sort_key(string):
    """Break a string into a list of substrings and numbers.

    This is intended to be used as a sorting key.

    Example input: "123hello-word.45.txt"
            output: [123, "hello-world.", 45, ".txt"]

    Returns:
        A list of strings and non-negative integers. Each digit in the input
        string is converted to a number; converting each element of the list
        to a string and joining them all gives the input value.
    """

    return [int(substr) if substr.isdigit() else substr for substr in re.split("([0-9]+)", string)]


def get_sorted_json_files(directory, recursive):
    """Returns a list of JSON files sorted by directory and by natural_sort_key.

    Args:
        directory: The directory to search for JSON files.
        recursive: True if the given directory should be searched recursively.
            If False, only JSON files directly inside the specified directory
            will be returned.

    Returns:
        A list of JSON filenames with the paths starting with the path of the
        `directory` input.
    """

    json_files = []

    for item in sorted(os.listdir(directory), key=natural_sort_key):
        path = os.path.join(directory, item)

        if os.path.isfile(path):
            if path.endswith(".json"):
                json_files.append(path)
        elif recursive:
            json_files += get_sorted_json_files(path, recursive)

    return json_files


def combine_json_files(directory, recursive, force_overwrite, verbosity):
    """Combine all JSON files in a directory into a single JSON file.

    The created file is named <directory>.json.

    Args:
        directory: The name of a directory.
        recursive: Whether subdirectories should be recursively searched for
            JSON files which would be added to the final JSON file.
        force_overwrite: True if the output file should be written even if it
            already exists. If the file doesn't already exist, this parameter
            doesn't do anything.
        verbosity: Integer specifying how verbose to make the emitted logs.
            Higher values mean more verbose.

    Raises:
        ValueError: If the input argument is not a directory.

    Returns:
        None
    """

    # Setup logging.
    utils.setup_logging(verbosity)
    log = logging.getLogger("merge_dictionaries")

    # Ensure the directory exists.
    if not os.path.isdir(directory):
        log.critical("`%s` is not a directory", directory)
        return

    # Check if the output file already exists.
    new_filename = os.path.basename(directory) + ".json"

    if not force_overwrite and os.path.exists(new_filename):
        # If the file exists, prompt the user before overwriting it
        response = input(f"Do you want to overwrite the existing {new_filename} file? (y/n) ")
        if response.lower() != "y":
            print(f"`{new_filename}` not overwritten")
            return

    # Get all JSON files.
    json_files = get_sorted_json_files(directory, recursive)

    if not json_files:
        log.warning("No JSON files found in directory `%s`", directory)
        return

    # Combine contents of JSON files.
    combined_json = {}
    for file in json_files:
        log.info("Merging `%s`", file)

        with open(file, "r", encoding="UTF-8") as file:
            contents = json.load(file)

            for key in contents:
                if key in combined_json:
                    log_func = log.debug if contents[key] == combined_json[key] else log.warning
                    log_func(
                        "Ignoring `%s` rule `%s: %s`; `%s: %s` has higher priority",
                        file.name,
                        key,
                        contents[key],
                        key,
                        combined_json[key],
                    )
                else:
                    combined_json[key] = contents[key]

    # Write the combined JSON a file.
    with open(new_filename, "w+", encoding="UTF-8") as file:
        json.dump(combined_json, file, indent=0)
        print(f"{new_filename} written successfully.")
