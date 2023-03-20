import logging

import config
import ipa_utils


# Each of the parameters is a list of keys to stroke. Each element of each
# paramter is the keys corresponding to one phoneme in the syllable.
def build_stroke_from_components(components):
    log = logging.getLogger('dictionary_generator')
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
        log.error(f'No vowel key in the stroke')
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
            log.error(f'All generated strokes must have a vowel key')
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

            order_pos = config.STENO_ORDER.find(letter, order_pos)
            if order_pos == -1:
                if letter in config.STENO_ORDER:
                    # The letter is out of steno order.
                    return None
                else:
                    log = logging.getLogger('dictionary_generator')
                    log.error(f'Invalid symbol `{letter}` in steno stroke')
                    return None
            else:
                # This letter is a valid addition to the stroke.
                stroke += letter

    return (stroke, has_star)


def get_stroke_components(phonemes, phonemes_to_steno):
    log = logging.getLogger('dictionary_generator')
    ways_to_stroke = [[]]

    for i, phoneme in enumerate(phonemes):
        steno = phonemes_to_steno[phoneme]
        if steno is None:
            log.error(f'No mapping given for phoneme {phoneme} in {phonemes}')
        elif steno == config.NO_STENO_MAPPING:
            log.error(f'No steno mapping for phoneme {phoneme} in {phonemes}')
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


def syllables_to_steno(syllables):
    translations = []  # List of all ways to stroke the syllable sequence.

    for i, syllable in enumerate(syllables):
        ways_to_stroke_onset = get_stroke_components(syllable.onset, config.LEFT_CONSONANT_TO_STENO)
        ways_to_stroke_nucleus = get_stroke_components([syllable.nucleus], config.VOWEL_TO_STENO)
        ways_to_stroke_coda = get_stroke_components(syllable.coda, config.RIGHT_CONSONANT_TO_STENO)

        if ways_to_stroke_onset is None or \
           ways_to_stroke_nucleus is None or \
           ways_to_stroke_coda is None:
            # There's no way to stroke this syllable.
            return None

        # Combine the parts of the stroke.
        # First add the onset parts of the stroke.
        ways_to_stroke_syllable = ways_to_stroke_onset.copy()

        # Next add the nucleus of the stroke.
        temp = []
        for partial_stroke in ways_to_stroke_syllable:
            for nucleus_part in ways_to_stroke_nucleus:
                temp.append(partial_stroke + nucleus_part)
        ways_to_stroke_syllable = temp.copy()

        # Finally add the coda of the stroke.
        temp.clear()
        for partial_stroke in ways_to_stroke_syllable:
            for coda_part in ways_to_stroke_coda:
                temp.append(partial_stroke + coda_part)
        ways_to_stroke_syllable = temp.copy()

        potential_strokes = []
        for stroke_components in ways_to_stroke_syllable:
            stroke = build_stroke_from_components(stroke_components)

            if stroke is not None:
                potential_strokes.append(stroke)

        if len(potential_strokes) == 0:
            log = logging.getLogger('dictionary_generator')
            log.info(f'No valid way to stroke the syllable `{syllable}`')
            return None

        if len(translations) == 0:
            translations = potential_strokes
        else:
            new_translations = []
            for prev_strokes in translations:
                for stroke in potential_strokes:
                    new_translations.append(prev_strokes + '/' + stroke)

            translations = new_translations.copy()

    # Run custom postprocessing.
    new_translations = []
    for steno in translations:
        new_steno = config.postprocess_steno_sequence(steno, syllables)

        if new_steno is not None:
            new_translations.append(new_steno)

    translations = new_translations

    return translations