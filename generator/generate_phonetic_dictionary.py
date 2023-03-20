import argparse
import logging

import config, core


def get_args():
    # Create an ArgumentParser object.
    parser = argparse.ArgumentParser(description='Generate steno strokes phonetically.')

    # Add arguments.
    parser.add_argument('ipa_file', type=str, help='the IPA CSV dictionary')
    parser.add_argument('word_list_file', type=str, help='the file containing words generate strokes for')
    parser.add_argument('-o', '--output_file', help='Path to the output file', default='output.json')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase output verbosity')

    # Parse the command line arguments
    return parser.parse_args()


def main():
    args = get_args()

    log_level = logging.WARNING
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >=2:
        log_level = logging.DEBUG

    log_format = '%(levelname)s: %(message)s'
    logging.basicConfig(level=log_level, format=log_format)
    log = logging.getLogger('dictionary_generator')

    # Make sure the config is valid.
    if not core.vowel_to_steno_is_complete() or \
       not core.consonant_to_steno_is_complete():
        log.info(f'Not generating dictionary')
        return

    words_and_strokes = core.generate_dictionary(args.ipa_file, args.word_list_file)
    words_and_strokes = config.postprocess_generated_dictionary(words_and_strokes)
    core.write_dictionary_to_file(words_and_strokes, args.output_file)


if __name__ == '__main__':
    main()