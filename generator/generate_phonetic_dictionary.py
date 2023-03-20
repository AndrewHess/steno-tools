"""Create a steno dictionary from a word list and their pronunciations.

The word list is given by a file containing each word to make an entry for on a
separate line. The pronunciations are given by a separate file that lists words
along with their IPA pronunciation; for example, the files found here:
https://github.com/open-dict-data/ipa-dict
"""

import argparse
import logging

import config
import core


def get_args():
    """Parse command-line arguments."""

    # Create an ArgumentParser object.
    parser = argparse.ArgumentParser(description="Generate steno strokes phonetically.")

    # Add arguments.
    parser.add_argument("ipa_file", type=str, help="the IPA CSV dictionary")
    parser.add_argument(
        "word_list_file", type=str, help="the file containing words generate strokes for"
    )
    parser.add_argument(
        "-o", "--output_file", help="Path to the output file", default="output.json"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="increase output verbosity"
    )

    # Parse the command line arguments
    return parser.parse_args()


def main():
    """Run the dictionary generator using command-line arguments."""

    args = get_args()

    # Setup logging.
    log_level = logging.WARNING
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG

    log_format = "%(levelname)s: %(message)s"
    logging.basicConfig(level=log_level, format=log_format)
    log = logging.getLogger("dictionary_generator")

    # Make sure the config is valid.
    if not core.vowel_to_steno_is_complete() or not core.consonant_to_steno_is_complete():
        log.info("Not generating dictionary")
        return

    # Create the dictionary.
    words_and_strokes = core.generate_dictionary(args.ipa_file, args.word_list_file)
    words_and_strokes = config.postprocess_generated_dictionary(words_and_strokes)
    core.write_dictionary_to_file(words_and_strokes, args.output_file)


if __name__ == "__main__":
    main()
