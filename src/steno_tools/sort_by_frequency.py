"""Sort words by their frequency.

This can also be used to check which words in one file are not in another file.
To do this, use the --no-output flag.
"""


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


def sort_words(words_file, ordering_file, ignore_case, output_file):
    """Sort words by their order in another file.

    Args:
        words_file: File containing the words to sort. Each word should be on
            its own line.
        ordering_file: File listing words in the order they should be sorted.
            Each word should be on its own line. This file may contain words
            that are not in `words_file`. On the other hand, if a word in
            `words_file` is not in this file, that word will be sorted below
            all words in `words_file` that are in this file.
        ignore_case: True if when searching for a word in `ordering_file`,
            it's considered a match as long as all the letters match, even if
            they have different capitalization.
        output_file: File to write the sorted words to. This can be None to
            indicate that no file should be written to; this can be useful to
            check which words in `words_file` are not in `ordering_file`
            because a message is printed for each such word.
    """

    # Load the input word list
    with open(words_file, "r", encoding="UTF-8") as file:
        input_words = [line.strip() for line in file.readlines()]

    maybe_ignore_case = identity
    if ignore_case:
        maybe_ignore_case = lowercased

    # Load the frequency list and create a dictionary mapping words to their frequency rank
    with open(ordering_file, "r", encoding="UTF-8") as file:
        frequency_dict = {maybe_ignore_case(word.strip()): rank for rank, word in enumerate(file)}

    # Sort the input word list based on the frequency rank and word itself
    sorted_words = sorted(
        input_words,
        key=lambda x: get_frequency(maybe_ignore_case(x), frequency_dict, ordering_file),
    )

    # Remove duplicates
    unique_words = []
    prev = ""
    for word in sorted_words:
        if word != prev:
            unique_words.append(word)
            prev = word

    sorted_words = unique_words

    if output_file is not None:
        # Write the sorted words to the output file
        with open(output_file, "w", encoding="UTF-8") as file:
            file.write("\n".join(sorted_words))
