"""Tools for updating strokes after they've been generated.

Changes that can be made without knowing about other strokes that were
generated should be performed in postprocess_steno_sequence(), while changes
that need to know about all other generated strokes should be made in
postprocess_generated_dictionary().
"""

from steno import Key


def postprocess_steno_sequence(stroke_sequence, syllables_ipa, config):
    """Make custom modifications to a generated stroke sequence.

    Args:
        stroke_sequence: A StrokeSequence.
        syllables_ipa: A list of Syllables, giving the pronunciation for the
            translated word via IPA. See syllable.py for more info on a
            Syllable.
        config: The Config specifying how strokes should be generated.

    Returns:
        A list of updated StrokeSequences.
    """

    strokes = stroke_sequence.get_strokes()

    if config.should_disallow_f_for_final_s_sound():
        _disallow_f_for_final_s_sound(strokes, syllables_ipa)

    return config.postprocess_stroke_sequence(stroke_sequence)


def _disallow_f_for_final_s_sound(strokes, syllables_ipa):
    """Disallow -F as the final 's' sound in a stroke.

    If the final sound in a syllable is an 's', it should be with the 'S' key
    not the 'F' key, even though making 's' with 'F' is allowed if there's
    another sound later in the syllable.


    Args:
        strokes: a list of Strokes that correspond to one definition.
        syllables_ipa: A list of Syllables, giving the pronunciation for the
            translated word via IPA. See syllable.py for more info on a
            Syllable.
    """

    for stroke, syllable in zip(strokes, syllables_ipa):
        if stroke.get_last_key() == Key.RF and syllable.is_last_phoneme_s():
            # This is invalid.
            strokes.clear()


def postprocess_generated_dictionary(word_and_translations, config):
    """Make custom modifications to the generated steno dictionary.

    This can be used to resolve homophone conflicts for example, by looping
    through all entries and checking if the the stroke sequence for the
    current word is already taken and if so, appending some distinguishing
    stroke to make it unique.

    Args:
        word_and_definitions: A list of tuples where the first item in each
            tuple is the word to translate into steno and the second item in
            the tuple is a StrokeSequences, with each StrokeSequence being a way
            to write the word in steno.
        config: The Config specifying how strokes should be generated.

    Returns:
        An updated version of the input after applying any modifications to the
        each StrokeSequence.
    """

    if config.should_append_disambiguator_stroke():
        # If a desired definition is already taken, append a the disambiguator
        # stroke until it's unique.
        used_translation_strings = set()
        disambiguator_stroke = config.get_disambiguator_stroke()

        for _, translations in word_and_translations:
            for translation in translations:
                while str(translation) in used_translation_strings:
                    translation.append_stroke(disambiguator_stroke)

                used_translation_strings.add(str(translation))

    return word_and_translations
