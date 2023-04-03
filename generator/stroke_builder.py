"""Convert IPA syllables into steno strokes."""

import copy
import itertools
import logging
import more_itertools

import postprocessing
import steno


def syllables_to_steno(syllables, config):
    """Create a list of possible steno strokes to form the given syllables.

    Args:
        syllables: A list of Syllables (see syllable.py)

    Returns:
        A list of StrokeSequences. Each stroke sequence is a way to steno the
        word for the input syllables given the rules for syllable splitting,
        postprocessing, and phoneme to steno key conversion.
    """

    log = logging.getLogger("dictionary_generator")
    translations = []  # List of all ways to stroke the syllable sequence.
    phoneme_tuples_to_possible_key_clusters = config.get_phoneme_tuples_to_possible_key_clusters()

    possible_strokes_for_each_syllable = []

    for syllable in syllables:
        possible_keys_for_each_phoneme_cluster = syllable.map_atoms(
            phoneme_tuples_to_possible_key_clusters
        )

        possible_keys_for_syllable = itertools.product(*possible_keys_for_each_phoneme_cluster)
        possible_keys_for_syllable = [
            list(more_itertools.flatten(tpl)) for tpl in possible_keys_for_syllable
        ]

        possible_strokes_for_syllable = []
        for keys in possible_keys_for_syllable:
            try:
                stroke = steno.Stroke(keys)
            except steno.OutOfStenoOrderError:
                log.debug("Out of steno order `%s`", keys)
            else:
                possible_strokes_for_syllable.append(stroke)

        if len(possible_strokes_for_syllable) == 0:
            log.info("No valid way to stroke the syllable `%s`", syllable)
            return None

        possible_strokes_for_each_syllable.append(possible_strokes_for_syllable)

    possible_strokes = itertools.product(*possible_strokes_for_each_syllable)
    translations = [
        steno.StrokeSequence(copy.deepcopy(list(strokes_tuple)))
        for strokes_tuple in possible_strokes
    ]

    # Run custom postprocessing.
    new_translations = []
    for stroke_sequence in translations:
        new_sequences = postprocessing.postprocess_steno_sequence(
            stroke_sequence, syllables, config
        )

        for sequence in new_sequences:
            if sequence.get_strokes() != []:
                new_translations.append(sequence)

    translations = new_translations

    return translations
