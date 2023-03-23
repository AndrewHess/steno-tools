"""Convert IPA syllables into steno strokes."""

import copy
import logging

import config
import steno


def get_stroke_components(phonemes, phonemes_to_steno):
    """Convert phonemes into their corresponding steno keys.

    Args:
        phonemes: A list of phonemes to convert to steno keys. The list should
            correspond to one steno stroke.
        phonemes_to_steno: A dictionary mapping phonemes to possible ways to
            write that phoneme with steno. If there is only one way to write
            the phoneme, the value will be a string specifying the steno keys.
            If there are multiple ways to write the phoneme, the value will be
            a list of strings with each element specifying the steno keys to
            write the phoneme in a different way. If there is no way to write
            the phoneme, the value should be config.NO_STENO_MAPPING.

    Returns:
        A list of list of strings. Each element of the returnd list is a way to
        write the provided phonemes. Each character of each string within the
        an inner list is the name of a steno key; for example, "K", "O", or "*".

    """

    log = logging.getLogger("dictionary_generator")
    ways_to_stroke = [[]]

    for phoneme in phonemes:
        ways_to_write_phoneme = phonemes_to_steno[phoneme]
        if ways_to_write_phoneme is None:
            log.error("No mapping given for phoneme `%s` in `%s`", phoneme, phonemes)
        elif ways_to_write_phoneme == config.NO_STENO_MAPPING:
            log.error("No steno mapping for phoneme `%s` in `%s`", phoneme, phonemes)
            return None

        new_ways_to_stroke = []
        for keys in ways_to_write_phoneme:
            # Append the `keys` list to each list of how to stroke the previous
            # components.
            for partial_stroke in ways_to_stroke:
                new_ways_to_stroke.append(partial_stroke + keys)

        ways_to_stroke = new_ways_to_stroke

    return ways_to_stroke


def syllables_to_steno(syllables):
    """Create a list of possible steno strokes to form the given syllables.

    Args:
        syllables: A list of Syllables (see syllable.py)

    Returns:
        A list of strings. Each string is way to write `syllables` in steno
        given the rules for syllable splitting, postprocessing, and phoneme to
        steno key conversion in config.py.
    """

    log = logging.getLogger("dictionary_generator")
    translations = []  # List of all ways to stroke the syllable sequence.

    for syllable in syllables:
        ways_to_stroke_onset = get_stroke_components(
            syllable.onset, config.LEFT_CONSONANT_TO_STENO
        )
        ways_to_stroke_nucleus = get_stroke_components([syllable.nucleus], config.VOWEL_TO_STENO)
        ways_to_stroke_coda = get_stroke_components(syllable.coda, config.RIGHT_CONSONANT_TO_STENO)

        if (
            ways_to_stroke_onset is None
            or ways_to_stroke_nucleus is None
            or ways_to_stroke_coda is None
        ):
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
        for keys_list in ways_to_stroke_syllable:
            try:
                stroke = steno.Stroke(keys_list)
            except steno.OutOfStenoOrderError:
                log.debug("Out of steno order `%s`", keys_list)
            else:
                potential_strokes.append(stroke)

        if len(potential_strokes) == 0:
            log.info("No valid way to stroke the syllable `%s`", syllable)
            return None

        if len(translations) == 0:
            # translations = potential_strokes
            for stroke in potential_strokes:
                translations.append(steno.StrokeSequence([stroke]))
        else:
            new_translations = []
            for stroke_sequence in translations:
                for stroke in potential_strokes:
                    new_sequence = copy.deepcopy(stroke_sequence)
                    new_sequence.append_stroke(stroke)
                    new_translations.append(new_sequence)

            translations = new_translations.copy()

    # Run custom postprocessing.
    new_translations = []
    for stroke_sequence in translations:
        new_stroke_sequence = config.postprocess_steno_sequence(stroke_sequence, syllables)

        if new_stroke_sequence is not None:
            new_translations.append(new_stroke_sequence)

    translations = new_translations

    return translations
