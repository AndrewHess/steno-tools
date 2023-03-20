import config
import ipa_utils
import stroke_builder


def vowel_to_steno_is_complete():
    all_defined = True

    for vowel in config.VOWELS:
        if vowel not in config.VOWEL_TO_STENO:
            all_defined = False
            print(f'Error: `{vowel}` is in VOWELS but not mapped in VOWEL_TO_STENO')

    return all_defined


def consonant_to_steno_is_complete():
    all_defined = True

    for consonant in config.CONSONANTS:
        if consonant not in config.LEFT_CONSONANT_TO_STENO:
            all_defined = False
            print(f'Error: `{consonant}` is in CONSONANTS but not mapped in LEFT_CONSONANT_TO_STENO')

        if consonant not in config.RIGHT_CONSONANT_TO_STENO:
            all_defined = False
            print(f'Error: `{consonant}` is in CONSONANTS but not mapped in RIGHT_CONSONANT_TO_STENO')

    return all_defined


def generate_dictionary(ipa_file, word_list_file):
    # Make a list of tuples. The first part of the tuple is the desired word,
    # and the second part is a list of ways to write it in steno.
    words_and_strokes = []
    word_to_ipa = ipa_utils.create_ipa_lookup_dictionary(ipa_file)

    with open(word_list_file, 'r') as file:
        for line in file:
            word = line.strip()
            word_in_steno = []  # A list of ways to write the word.

            if word not in word_to_ipa:
                print(f'Warning: No translation for `{word}` (missing IPA entry)')
                continue

            for ipa in word_to_ipa[word]:
                syllables = ipa_utils.split_ipa_into_syllables(ipa)

                if syllables is None:
                    continue

                translations = stroke_builder.syllables_to_steno(syllables)
                if translations is not None:
                    word_in_steno += translations

            # Remove duplicate steno sequences.
            word_in_steno = list(set(word_in_steno))

            if len(word_in_steno) == 0:
                print(f'Warning: No translation for `{word}`')
            else:
                words_and_strokes.append((word, word_in_steno))

    return words_and_strokes


def write_dictionary_to_file(words_and_strokes, output_file):
    with open(output_file, 'w+') as output:
        output.write('{\n')

        for i, (word, ways_to_stroke) in enumerate(words_and_strokes):
            for k, strokes in enumerate(ways_to_stroke):
                line = f'"{strokes}": "{word}"'
                if i < len(words_and_strokes) - 1 or k < len(ways_to_stroke) - 1:
                    line += ','

                output.write(f'{line}\n')

        output.write('}')