"""A command-line interface for generating and managing steno dictionaries."""

import argparse

from steno_tools.combine_dictionaries import combine_json_files
from steno_tools.generator.core import generate_phonetic_dictionary
from steno_tools.sort_by_frequency import sort_words


def parse_args():
    """Returns arguments parsed via argparse."""

    parser = argparse.ArgumentParser(description="Steno Tools CLI")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # generate subcommand
    generate_parser = subparsers.add_parser(
        "generate", help="Generate a phonetic steno dictionary"
    )
    generate_parser.add_argument(
        "--ipa-notation",
        type=str,
        required=True,
        help="CSV file containing phonetic transcriptions for words",
    )
    generate_parser.add_argument(
        "--words",
        type=str,
        required=True,
        help="File containing the words to generate entries for. Each line contains a single word.",
    )
    generate_parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="File specifying how to generate entries for words",
    )
    generate_parser.add_argument(
        "-o", "--output", type=str, default="output.json", help="File to write to"
    )
    generate_parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Print progress information"
    )

    # merge subcommand
    merge_parser = subparsers.add_parser("merge", help="Merge dictionaries into a single file")
    merge_parser.add_argument("directory", type=str, help="Directory containing dictionary files")
    merge_parser.add_argument(
        "-f", "--force", action="store_true", help="Overwrite output file if it exists"
    )
    merge_parser.add_argument(
        "-r", "--recursive", action="store_true", help="Recursively search directory"
    )
    merge_parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Print progress information"
    )

    # sort-words subcommand
    sort_parser = subparsers.add_parser(
        "sort-words", help="Sort words by their order in a different file"
    )
    sort_parser.add_argument("--words", required=True, help="File containing words to reorder")
    sort_parser.add_argument(
        "--canonical-order", required=True, help="File listing words sorted in the desired way"
    )
    sort_parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Ignore capitalization when searching for words in the sorted list",
    )
    sort_parser_output_group = sort_parser.add_mutually_exclusive_group(required=True)
    sort_parser_output_group.add_argument("-o", "--output", help="File to write to")
    sort_parser_output_group.add_argument(
        "--no-output", action="store_true", help="Don't write the sorted words to a file"
    )

    return parser.parse_args()


def main():
    """Parse args and delegate to the appropriate script."""

    args = parse_args()

    if args.subcommand == "generate":
        generate_phonetic_dictionary(
            args.ipa_notation, args.words, args.config, args.output, args.verbose
        )
    elif args.subcommand == "merge":
        combine_json_files(args.directory, args.recursive, args.force, args.verbose)
    elif args.subcommand == "sort-words":
        output = None if args.no_output else args.output
        sort_words(args.words, args.canonical_order, args.ignore_case, output)
    else:
        print("Bug: unknown subcommand `{args.subcommand}`")


if __name__ == "__main__":
    main()
