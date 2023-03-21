"""Generate a steno dictionary by converting words to strokes."""

import logging

import config
import ipa_utils
import stroke_builder


def vowel_to_steno_is_complete():
    """Check if all vowels in config.py have a specified mapping to steno.

    Returns:
        True if for each entry in config.VOWELS, there is an entry in
        config.VOWEL_TO_STENO, even if it's config.NO_STENO_MAPPING.
    """

    all_defined = True
    log = logging.getLogger("dictionary_generator")

    for vowel in config.VOWELS:
        if vowel not in config.VOWEL_TO_STENO:
            all_defined = False
            log.error("`%s` is in VOWELS but not mapped in VOWEL_TO_STENO", vowel)

    return all_defined


def consonant_to_steno_is_complete():
    """Check if all consonants in config.py have a specified mapping to steno.

    Returns:
        True if for each entry in config.CONSONANTS, there is an entry in
        config.CONSONANT_TO_STENO, even if it's config.NO_STENO_MAPPING.
    """

    all_defined = True
    log = logging.getLogger("dictionary_generator")

    for consonant in config.CONSONANTS:
        if consonant not in config.LEFT_CONSONANT_TO_STENO:
            all_defined = False
            log.error("`%s` is in CONSONANTS but not mapped in LEFT_CONSONANT_TO_STENO", consonant)

        if consonant not in config.RIGHT_CONSONANT_TO_STENO:
            all_defined = False
            log.error(
                "`%s` is in CONSONANTS but not mapped in RIGHT_CONSONANT_TO_STENO", consonant
            )

    return all_defined


def generate_dictionary(ipa_file, word_list_file):
    """Create a dictionary mapping a word to ways to write it in steno.

    Args:
        ipa_file: A CSV file that gives the pronunciation in IPA for a word.
            Each line should be "<word>,/<ipa1>/,/<ipa2>/..." so that each
            prononciation (ipa1, ipa2, ...) is between slashes.
        word_list_file: A file of words that should be translated into steno
            strokes. Each word should be on its own line. If the word does not
            have an entry in the `ipa_file` then its steno strokes cannot be
            generated.
    Returns:
        A list of tuples where theh first item in each tuple is a word from
        `word_list_file` and the second item in the tuple is a list of strings,
        with each string being a way to write the word in steno.
    """

    # Make a list of tuples. The first part of the tuple is the desired word,
    # and the second part is a list of ways to write it in steno.
    words_and_strokes = []
    word_to_ipa = ipa_utils.create_ipa_lookup_dictionary(ipa_file)

    num_words_requested = 0
    num_words_translated = 0

    log = logging.getLogger("dictionary_generator")

    with open(word_list_file, "r", encoding="UTF-8") as file:
        for line in file:
            num_words_requested += 1
            word = line.strip()
            word_lower = word.lower()
            word_in_steno = []  # A list of ways to write the word.

            log.debug("Translating `%s`", word)

            if word_lower not in word_to_ipa:
                log.warning("No translation for `%s` (missing IPA entry)", word)
                continue

            for ipa in word_to_ipa[word_lower]:
                syllables = ipa_utils.split_ipa_into_syllables(ipa)

                if syllables is None:
                    continue

                log.debug("Converting %s to steno", [str(s) for s in syllables])
                translations = stroke_builder.syllables_to_steno(syllables)
                if translations is not None:
                    log.debug("Generated %s for `%s`", translations, word)
                    word_in_steno += translations

            # Remove duplicate steno sequences.
            word_in_steno = list(set(word_in_steno))

            if len(word_in_steno) == 0:
                log.warning("No translation for `%s`", word)
            else:
                words_and_strokes.append((word, word_in_steno))
                num_words_translated += 1

    print(
        f"Generated translations for {num_words_translated} out of "
        + f"{num_words_requested} words"
    )

    return words_and_strokes


def write_dictionary_to_file(words_and_strokes, output_file):
    """Write steno strokes for words to a file in JSON format.

    Args:
        words_and_strokes: the returned value from generate_dictionary()
        output_file: the name of the output file. This should be a JSON file.
    """

    num_entries = 0
    num_strokes = 0

    with open(output_file, "w+", encoding="UTF-8") as output:
        output.write("{\n")

        for i, (word, ways_to_stroke) in enumerate(words_and_strokes):
            for k, strokes in enumerate(ways_to_stroke):
                line = f'"{strokes}": "{word}"'
                if i < len(words_and_strokes) - 1 or k < len(ways_to_stroke) - 1:
                    line += ","

                output.write(f"{line}\n")

                num_entries += 1
                num_strokes += 1 + strokes.count("/")

        output.write("}")

    print(f"Generated {num_strokes} strokes for {num_entries} entries")
