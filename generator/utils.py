import random
import sys


STENO_ORDER = 'STKPWHRAOEUFRPBLGTSDZ'
NO_STENO_MAPPING = 'NO_STENO_MAPPING'

def create_ipa_lookup_dictionary(filename):
    word_to_ipa = {}
    try:
        with open(filename, newline='') as csv_file:
            for line in csv_file:
                (key, value) = extract_key_and_value(line)
                word_to_ipa[key] = value

    except FileNotFoundError:
        print(f'The file `{filename}` does not exist.', file=sys.stderr)
        sys.exit(1)

    return word_to_ipa


def extract_key_and_value(line):
    split_line = line.strip().split(',', 1)  # Only split at the first comma.
    key = split_line[0]

    # Each value is between a pair of slashes.
    split_value = split_line[1].split('/')
    # Extract every second element.
    return (key, split_value[1::2])


# Find all the IPA symbols used by this dictionary.
def get_ipa_symbols(word_to_ipa):
    # Check the IPA symbols used in a bunch of random words.
    num_words_to_check = 10000

    words = []
    keys = list(word_to_ipa.keys())
    for _ in range(num_words_to_check):
        words.append(random.choice(keys))

    symbols = set()
    for word in words:
        for ipa in word_to_ipa[word]:
            for char in ipa:
                symbols.add(char)

    return symbols


# Each of the parameters is a list of keys to stroke. Each element of each
# paramter is the keys corresponding to one phoneme in the syllable.
def build_stroke_from_components(components):
    info = build_stroke_helper(components)

    if info is None:
        return None

    (stroke, has_star) = info

    # Make sure there's a vowel key. If there arn't any, then we need to place
    # a '-' where the vowels would be. However, the logic gets a bit tricky
    # because some consonants are on both the left and right sides. So to make
    # it easier and becuase all English syllables have vowels, I'm going to
    # require that each stroke as a vowel key.
    has_vowel = False
    for vowel in ['A', 'O', 'E', 'U']:
        if vowel in stroke:
            has_vowel = True

    if not has_vowel:
        print(f'Error: No vowel key in the stroke')
        return None

    if has_star:
        # Place the star. It goes between 'O' and 'E' in steno order. This is
        # a bit easier since we're requiring a vowel key in each stroke.
        pos = stroke.find('O') + 1

        if pos == 0:
            pos = stroke.find('A') + 1

        if pos == 0:
            pos = stroke.find('E')

        if pos == -1:
            pos = stroke.find('U')

        if pos == -1:
            print(f'Error: all generated strokes must have a vowel key')
            return None

        # Add the star.
        stroke = stroke[:pos] + '*' + stroke[pos:]

    return stroke


def build_stroke_helper(components):
    stroke = ''
    has_star = False
    order_pos = 0

    for keys_for_phoneme in components:
        for letter in keys_for_phoneme:
            if letter == '*':
                has_star = True
                continue
            elif len(stroke) > 0 and letter == stroke[-1]:
                # We're repeating a letter; this is valid, just don't double
                # the letter in the returned steno stroke.
                continue

            order_pos = STENO_ORDER.find(letter, order_pos)
            if order_pos == -1:
                if letter in STENO_ORDER:
                    # The letter is out of steno order.
                    return None
                else:
                    print(f'Error: invalid symbol `{letter}` in steno stroke')
                    return None
            else:
                # This letter is a valid addition to the stroke.
                stroke += letter

    return (stroke, has_star)


def get_stroke_components(phonemes, phonemes_to_steno):
    ways_to_stroke = [[]]

    for i, phoneme in enumerate(phonemes):
        steno = phonemes_to_steno[phoneme]
        if steno is None:
            print(f'Warning: No mapping given for phoneme {phoneme} in {phonemes}')
        elif steno == NO_STENO_MAPPING:
            print(f'Warning: No steno mapping for phoneme {phoneme} in {phonemes}')
            return None
        elif isinstance(steno, list):
            new_ways_to_stroke = []
            for keys in steno:
                for partial_stroke in ways_to_stroke:
                    new_ways_to_stroke.append(partial_stroke + [keys])

            ways_to_stroke = new_ways_to_stroke
        else:
            for i in range(len(ways_to_stroke)):
                ways_to_stroke[i] += [steno]

    return ways_to_stroke
