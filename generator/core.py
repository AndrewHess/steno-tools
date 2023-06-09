"""Generate a steno dictionary by converting words to strokes."""

import logging

import ipa_utils
import postprocessing
import stroke_builder


def generate_dictionary(ipa_file, word_list_file, config):
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
        A list of tuples where the first item in each tuple is a word from
        `word_list_file` and the second item in the tuple is a list of
        StrokeSequences, giving the valid ways to steno that word.
    """

    # Make a list of tuples. The first part of the tuple is the desired word,
    # and the second part is a list of ways to write it in steno.
    words_and_translations = []
    word_to_ipa = ipa_utils.create_ipa_lookup_dictionary(ipa_file)

    num_words_requested = 0
    num_words_translated = 0

    log = logging.getLogger("dictionary_generator")

    with open(word_list_file, "r", encoding="UTF-8") as file:
        for line in file:
            num_words_requested += 1
            word = line.strip()
            word_lower = word.lower()
            translations_for_word = []  # A list of ways to write the word.

            log.debug("Translating `%s`", word)

            if word_lower not in word_to_ipa:
                log.warning("No translation for `%s` (missing IPA entry)", word)
                continue

            for ipa in word_to_ipa[word_lower]:
                syllables = ipa_utils.split_ipa_into_syllables(ipa, config)

                if syllables is None:
                    continue

                log.debug("Converting %s to steno", [str(s) for s in syllables])
                translations = stroke_builder.syllables_to_steno(syllables, config)
                if translations is not None:
                    log.debug("Generated %s for `%s`", translations, word)
                    translations_for_word += translations

            # Remove duplicate translations.
            translations_for_word = sorted(list(set(translations_for_word)))

            if len(translations_for_word) == 0:
                log.warning("No translation for `%s`", word)
            else:
                words_and_translations.append((word, translations_for_word))
                num_words_translated += 1

    print(
        f"Generated translations for {num_words_translated} out of "
        + f"{num_words_requested} words"
    )

    # Perform postprocessing on the whole dictionary.
    words_and_translations = postprocessing.postprocess_generated_dictionary(
        words_and_translations, config
    )

    return words_and_translations


def write_dictionary_to_file(words_and_translations, output_file):
    """Write steno strokes for words to a file in JSON format.

    Args:
        words_and_translations: the returned value from generate_dictionary().
        output_file: the name of the output file. This should be a JSON file.
    """

    num_entries = 0
    num_strokes = 0

    with open(output_file, "w+", encoding="UTF-8") as output:
        output.write("{\n")

        for i, (word, translations) in enumerate(words_and_translations):
            for k, stroke_sequence in enumerate(translations):
                line = f'"{str(stroke_sequence)}": "{word}"'
                if i < len(words_and_translations) - 1 or k < len(translations) - 1:
                    line += ","

                output.write(f"{line}\n")

                num_entries += 1
                num_strokes += len(stroke_sequence.get_strokes())

        output.write("}")

    print(f"Generated {num_strokes} strokes for {num_entries} entries")
