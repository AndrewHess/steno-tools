import argparse

import config, utils

def get_args():
    # Create an ArgumentParser object.
    parser = argparse.ArgumentParser(description='Generate steno strokes phonetically.')

    # Add arguments.
    parser.add_argument('ipa_file', type=str, help='the IPA CSV dictionary')
    parser.add_argument('word_list_file', type=str, help='the file containing words generate strokes for')
    parser.add_argument('-o', '--output_file', help='Path to the output file', default='output.json')

    # Parse the command line arguments
    return parser.parse_args()


def main():
    args = get_args()

    word_to_ipa = utils.create_ipa_lookup_dictionary(args.ipa_file)
    symbols = list(utils.get_ipa_symbols(word_to_ipa))
    symbols.sort()
    print(f'IPA symbols: {symbols}')

    # Make a list of tuples. The first part of the tuple is the desired word,
    # and the second part is a list of ways to write it in steno.
    words_and_strokes = []

    with open(args.word_list_file, 'r') as file:
        for line in file:
            word = line.strip()
            word_in_steno = []  # A list of ways to write the word.

            if word not in word_to_ipa:
                print(f'Warning: No translation for `{word}` (missing IPA entry)')
                continue

            for ipa in word_to_ipa[word]:
                syllables = config.split_ipa_into_syllables(ipa)

                if syllables is None:
                    continue

                translations = config.syllables_to_steno(syllables)
                if translations is not None:
                    word_in_steno += translations

            # Remove duplicate steno sequences.
            word_in_steno = list(set(word_in_steno))

            if len(word_in_steno) == 0:
                print(f'Warning: No translation for `{word}`')
            else:
                words_and_strokes.append((word, word_in_steno))

    # Run postprocessing on the whole dictionary.
    words_and_strokes = config.postprocess_generated_dictionary(words_and_strokes)

    with open(args.output_file, 'w+') as output:
        output.write('{\n')

        for i, (word, ways_to_stroke) in enumerate(words_and_strokes):
            for k, strokes in enumerate(ways_to_stroke):
                line = f'"{strokes}": "{word}"'
                if i < len(words_and_strokes) - 1 or k < len(ways_to_stroke) - 1:
                    line += ','

                output.write(f'{line}\n')

        output.write('}')


if __name__ == '__main__':
    main()
