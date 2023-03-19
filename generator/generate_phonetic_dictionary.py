import argparse

import config, core


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

    words_and_strokes = core.generate_dictionary(args.ipa_file, args.word_list_file)
    words_and_strokes = config.postprocess_generated_dictionary(words_and_strokes)
    core.write_dictionary_to_file(words_and_strokes, args.output_file)


if __name__ == '__main__':
    main()