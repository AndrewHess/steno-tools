"""Sort words by their frequency.

This can also be used to check which words in one file are not in another file.
To do this, use the --no-output flag.
"""

import argparse


def parse_args():
    """Parse command-line arguments.

    Returns:
        Parsed args
    """

    parser = argparse.ArgumentParser(
        description="Reorders words in an input word list based on a frequency list"
    )
    parser.add_argument("-w", "--word-list", required=True, help="input word list filename")
    parser.add_argument("-f", "--frequency-file", required=True, help="frequency list filename")

    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument("-o", "--output-file", help="output word list filename")
    output_group.add_argument(
        "--no-output", action="store_true", help="don't write the sorted words to a file"
    )

    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Ignore the capitalization of words when searching for them in the frequency list",
    )

    return parser.parse_args()


def get_frequency(word, frequency_dict, frequency_file):
    """Get the frequency rank of a word.

    This also prints a message if the word was not found in the dictionary.

    Returns:
        A tuple where the first element is the frequency rank of the word, and
        the second element is the input word.
    """
    frequency = frequency_dict.get(word)
    if frequency is None:
        print(f"Not found in {frequency_file}: `{word}`")
        return (len(frequency_dict), word)

    return (frequency, word)


def identity(anything):
    """Return the input."""

    return anything


def lowercased(string):
    """Return the input string lowercased."""

    return string.lower()


def main():
    """Sort a word list by frequency and optionally write the results to a file.

    If a word in the input list is not in the frequency list, a message is
    printed noting that. This can also be used to check which words are in the
    word list but not in the frequency list by using the --no-output flag.
    """

    args = parse_args()

    # Load the input word list
    with open(args.word_list, "r", encoding="UTF-8") as file:
        input_words = [line.strip() for line in file.readlines()]

    maybe_ignore_case = identity
    if args.ignore_case:
        maybe_ignore_case = lowercased

    # Load the frequency list and create a dictionary mapping words to their frequency rank
    with open(args.frequency_file, "r", encoding="UTF-8") as file:
        frequency_dict = {maybe_ignore_case(word.strip()): rank for rank, word in enumerate(file)}

    # Sort the input word list based on the frequency rank and word itself
    sorted_words = sorted(
        input_words,
        key=lambda x: get_frequency(maybe_ignore_case(x), frequency_dict, args.frequency_file),
    )

    # Remove duplicates
    unique_words = []
    prev = ""
    for word in sorted_words:
        if word != prev:
            unique_words.append(word)
            prev = word

    sorted_words = unique_words

    if not args.no_output:
        # Write the sorted words to the output file
        with open(args.output_file, "w", encoding="UTF-8") as file:
            file.write("\n".join(sorted_words))


if __name__ == "__main__":
    main()
