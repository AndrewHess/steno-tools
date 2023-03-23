"""Configuration for the steno dictionary generator."""

import logging

import steno
from steno import Key


STENO_ORDER = "STKPWHRAOEUFRPBLGTSDZ"  # Excludes the '*'.
NO_STENO_MAPPING = "NO_STENO_MAPPING"

# Vowel phonemes that may appear in the IPA pronunciation of words that you
# want to generate steno strokes for.
VOWELS = [
    ############ American English Vowels ############
    "ɪ",  # Ex: mYth, prEtty, wOmen
    "ɛ",  # Ex: brEAd, mAny, mEn
    "æ",  # Ex: cAt, fAst, pAss
    "ə",  # Ex: bUn, dOne, crUmb
    "ʊ",  # Ex: wOOd, pUt
    "i",  # Ex: bEE, mEAt
    "ɔ",  # Ex: brAWl, tAll, wrOUght, but not rot
    "u",  # Ex: fOOd, whO, blUE
    "ɝ",  # Ex: pURR, pERson, dIRty, doctOR
    "ɑ",  # Ex: rOt, but not wrought
    "aɪ",  # Ex: EYE, trY, nIght
    "eɪ",  # Ex: AYE, glAde
    "ɔɪ",  # Ex: bOY, nOIse
    "aʊ",  # Ex: clOWn, nOUn
    "oʊ",  # Ex: OWE, blOW
    "ɪɹ",  # Ex: fEAR, dEER, drEARy
    "ɛɹ",  # Ex: AIR, glARe, stARE
    "ɔɹ",  # Ex: gORe, bOAR, dOOR
    "ʊɹ",  # Ex: pURe, ensURe
    "ɑɹ",  # Ex: cAR, sonAR, ARctic
    ############ Extra Vowel Clusters ############
    "ju",  # Ex: YOU, fEW, pEWter
    "jə",  # Sounds the same as 'ju' to me.
    "ɝtʃ",  # Ex: lURCH, resEARCH
    "ɑɹtʃ",  # Ex: ARCH, mARCH,
    "ɔɹtʃ",  # Ex: tORCH, pORCH
]

# Consonant phonemes that may appear in the IPA pronunciation of words that
# you want to generate steno strokes for.
CONSONANTS = [
    "b",
    "d",
    "f",
    "h",
    "j",  # This is a 'y' sound, like Yep, Yarn, You
    "k",
    "m",
    "n",
    "p",
    "s",
    "t",
    "v",
    "w",
    "z",
    "ð",  # Ex: worTHy, furTHer
    "ŋ",  # Ex: struNG, fliNG
    "ɡ",  # Ex: doG, Glue  Note: this is a UTF-8 char, not the letter G.
    "ɫ",  # Ex: fiLL, terminaL
    "ɹ",  # Ex: bRook, gRay
    "ʃ",  # Ex: wiSH, puSH
    "ʒ",  # Ex: leiSure, fuSion
    "θ",  # Ex: youTH, THin
    "tʃ",  # Ex: gliTCH, beaCH
    "dʒ",  # Ex: JuDGe, friDGe, Germ
    ############ Consonant Clusters ############
    "st",  # Ex: firST heiST, burST
    "ŋk",  # Ex: baNK, thaNKs
    "mp",  # Ex: raMP, cluMP
    "ntʃ",  # Ex: lauNCH, braNCH
]

# IPA symbols used to denote the stress of the following syllable.
STRESS_MARKERS = ["ˈ", "ˌ"]

# Specify how each vowel in VOWELS should be translated to steno.
#
# Each vowel in VOWELS must have an entry here.
#
# If there are multiple ways to write the sound, the value should be a list of
# strings with each string being a way to write it.
#
# If the sound should be stenoed with the star key, add a "*" character
# anywhere in the string.
VOWEL_TO_STENO = {
    ############ American English Vowels ############
    "ɪ": [[Key.E, Key.U]],
    "ɛ": [[Key.E]],
    "æ": [[Key.A]],
    "ə": [[Key.U]],
    "ʊ": [[Key.A, Key.O]],
    "i": [[Key.A, Key.O, Key.E]],
    "ɔ": [[Key.A, Key.U]],
    "u": [[Key.A, Key.O, Key.U]],  # Note: this is the same as for 'ju'.
    "ɝ": [[Key.U, Key.RR]],
    "ɑ": [[Key.O]],
    "aɪ": [[Key.A, Key.O, Key.E, Key.U]],
    "eɪ": [[Key.A, Key.E, Key.U]],
    "ɔɪ": [[Key.O, Key.E, Key.U]],
    "aʊ": [[Key.O, Key.U]],
    "oʊ": [[Key.O, Key.E]],
    "ɪɹ": [[Key.A, Key.O, Key.E, Key.RR]],
    "ɛɹ": [[Key.A, Key.E, Key.U, Key.RR]],
    "ɔɹ": [[Key.O, Key.RR]],
    "ʊɹ": [[Key.A, Key.O, Key.U, Key.RR]],
    "ɑɹ": [[Key.A, Key.RR]],
    ############ Extra Vowel Clusters ############
    "ju": [[Key.A, Key.O, Key.U]],  # Note: this is the same as for just 'u'.
    "jə": [[Key.A, Key.O, Key.U]],
    "ɝtʃ": [[Key.U, Key.RF, Key.RR, Key.RP, Key.RB]],
    "ɑɹtʃ": [[Key.A, Key.RF, Key.RR, Key.RP, Key.RB]],
    "ɔɹtʃ": [[Key.O, Key.RF, Key.RR, Key.RP, Key.RB]],
}

# Specify how each consonant in CONSONANTS should be translated to steno using
# the left side consonants.
#
# Each consonant in CONSONANTS must have an entry here; if it's not a valid
# left-side consonant sound its value should be NO_STENO_MAPPING.
#
# If there are multiple ways to write the sound with left-side consonants, the
# value should be a list of strings with each string being a way to write it.
#
# If the sound should be stenoed with the star key, add a "*" character
# anywhere in the string.
LEFT_CONSONANT_TO_STENO = {
    "b": [[Key.LP, Key.LW]],
    "d": [[Key.LT, Key.LK]],
    "f": [[Key.LT, Key.LP]],
    "h": [[Key.LH]],
    "j": [[Key.LK, Key.LW, Key.LR]],
    "k": [[Key.LK]],
    "m": [[Key.LP, Key.LH]],
    "n": [[Key.LT, Key.LP, Key.LH]],
    "p": [[Key.LP]],
    "s": [[Key.LS]],
    "t": [[Key.LT]],
    "v": [[Key.LS, Key.LR]],
    "w": [[Key.LW]],
    "z": [[Key.LS, Key.LW, Key.LR]],
    "ð": [[Key.LT, Key.LH]],
    "ŋ": NO_STENO_MAPPING,
    "ɡ": [[Key.LT, Key.LK, Key.LP, Key.LW]],
    "ɫ": [[Key.LH, Key.LR]],
    "ɹ": [[Key.LR]],
    "ʃ": [[Key.LS, Key.LH]],
    "ʒ": [[Key.LS, Key.LK, Key.LH]],
    "θ": [[Key.LT, Key.LH]],
    "tʃ": [[Key.LK, Key.LH]],
    "dʒ": [[Key.LS, Key.LK, Key.LW, Key.LR]],
    "st": [[Key.LS, Key.LT]],
    "ŋk": NO_STENO_MAPPING,
    "mp": NO_STENO_MAPPING,
    "ntʃ": NO_STENO_MAPPING,
}

# Specify how each consonant in CONSONANTS should be translated to steno using
# the right-side consonants.
#
# Each consonant in CONSONANTS must have an entry here; if it's not a valid
# right-side consonant sound its value should be NO_STENO_MAPPING.
#
# If there are multiple ways to write the sound with right-side consonants, the
# value should be a list of strings with each string being a way to write it.
#
# If the sound should be stenoed with the star key, add a "*" character
# anywhere in the string.
RIGHT_CONSONANT_TO_STENO = {
    "b": [[Key.RB]],
    "d": [[Key.RD]],
    "f": [[Key.RF]],
    "h": NO_STENO_MAPPING,
    "j": NO_STENO_MAPPING,
    "k": [[Key.RB, Key.RG]],
    "m": [[Key.RP, Key.RL]],
    "n": [[Key.RP, Key.RB]],
    "p": [[Key.RP]],
    "s": [[Key.RS], [Key.RF]],
    "t": [[Key.RT]],
    "v": [[Key.RF, Key.RB]],
    "w": NO_STENO_MAPPING,
    "z": [[Key.RZ]],
    "ð": [[Key.STAR, Key.RT]],
    "ŋ": [[Key.RP, Key.RB, Key.RG]],
    "ɡ": [[Key.RG]],
    "ɫ": [[Key.RL]],
    "ɹ": [[Key.RR]],
    "ʃ": [[Key.RR, Key.RB]],
    "ʒ": NO_STENO_MAPPING,
    "θ": [[Key.STAR, Key.RT]],
    "tʃ": [[Key.RF, Key.RP]],
    "dʒ": [[Key.RP, Key.RB, Key.RL, Key.RG]],
    "st": [[Key.RF, Key.RT], [Key.STAR, Key.RS]],
    "ŋk": [[Key.RP, Key.RB, Key.RG]],  # Note: this colides with 'ŋ'.
    "mp": [[Key.STAR, Key.RP, Key.RL]],
    "ntʃ": [[Key.RF, Key.RR, Key.RP, Key.RB]],
}


def can_prepend_to_onset(phoneme, onset):
    """Determine if prepending a phoneme to an onset is valid.

    Args:
        phoneme: an entry in CONSONANTS
        onset: a list of strings, which are each entries in CONSONANTS
    Returns:
        True if prepending `phoneme` to `onset` is phonologically valid.
    """

    if phoneme not in CONSONANTS:
        log = logging.getLogger("dictionary_generator")
        log.error("Unknown consonant phoneme `%s`", phoneme)
        return False

    # Almost any initial sound is allowed.
    if onset == []:
        return phoneme not in ["ŋ", "ŋk", "mp", "ntʃ"]

    prev = onset[0]

    ####################### Custom Rules #######################
    if phoneme == "st" and prev in ["ɹ", "w"]:
        return True

    if phoneme == "ŋk":
        return False

    if phoneme == "mp":
        return False

    if phoneme == "ntʃ":
        return False

    ####################### English Rules ######################
    # All following rules are from https://en.wikipedia.org/wiki/English_phonology
    # English syllable structure is (C)^{3}V(C)^{5}, so no more than three
    # consonant sounds in the onset.
    if len(onset) >= 3:
        return False

    # Allow stop plus approximant other than 'j'.
    if (
        (prev == "ɫ" and phoneme in ["p", "b", "k", "ɡ"])
        or (prev == "ɹ" and phoneme in ["p", "b", "t", "d", "k", "ɡ"])
        or (prev == "w" and phoneme in ["p", "t", "d", "g", "k"])
    ):
        return True

    # Allow voicless fricative or 'v' plus approximant other than 'j'.
    if (
        (prev == "ɫ" and phoneme in ["f", "s", "θ", "ʃ"])
        or (prev == "ɹ" and phoneme in ["f", "θ", "ʃ"])
        or (prev == "w" and phoneme in ["h", "s", "θ", "v"])
    ):
        return True

    # Allow consonants other than 'ɹ' and 'w' followed by 'j' (which should
    # be followed by some form of 'u').
    if len(onset) == 1 and prev == "j" and phoneme not in ["ɹ", "w"]:
        return True

    # Allow 's' plus voiceless stop:
    if phoneme == "s" and prev in ["p", "t", "k"]:
        return True

    # Allow 's' plus nasal other than 'ŋ'.
    if phoneme == "s" and prev in ["m", "n"]:
        return True

    # Allow 's' plus voiceless non-sibilant fricative:
    if phoneme == "s" and prev in ["f", "θ"]:
        return True

    return False


def postprocess_steno_sequence(steno_sequence, syllables_ipa):
    """Make custom modifications to a generated stroke sequence.

    Args:
        steno_sequence: a string specifying the generated steno strokes. Each
            stroke is separated by a forward slash.
        syllables_ipa: A list of Syllables, giving the pronunciation for the
            translated word via IPA. See syllable.py for more info on a
            Syllable.

    Returns:
        A string that is the stroke sequence after applying any modifications.
        This should be the input `steno_sequence` if no modifications are
        desired for this sequence.
    """

    # syllables_steno = steno_sequence.split("/")
    # new_syllables_steno = syllables_steno.copy()

    new_strokes = steno_sequence.get_strokes().copy()

    # If a stroke after the first has 'U', 'EU', or 'E' as its vowel and it has
    # following consonants, replace the vowel cluster with '-' (or '*' if the
    # stroke is starred).
    for stroke in new_strokes[1:]:
        active_vowels = stroke.get_vowels()
        last_key = stroke.get_last_key()

        if active_vowels in [[Key.E], [Key.E, Key.U], [Key.U]] and (
            last_key is not None and last_key.index > Key.U.index
        ):
            stroke.clear_all_vowels()

    # If the final sound in a syllable is an 's', it should be with the 'S' key
    # not the 'F' key, even though making 's' with 'F' is allowed if there's
    # another sound later in the syllable.
    for stroke, ipa in zip(new_strokes, syllables_ipa):
        if stroke.get_last_key() == Key.RF and len(ipa.coda) > 0 and ipa.coda[-1] == "s":
            # This is invalid.
            return None

    # If the final stroke is 'SH-PB', fold it into the previous stroke as '-GS'.
    shun_stroke = steno.Stroke([Key.LS, Key.LH, Key.RP, Key.RB])
    if len(new_strokes) > 1 and new_strokes[-1] == shun_stroke:
        prev_stroke = new_strokes[-2]
        prev_stroke_keys = prev_stroke.get_keys()

        if (
            len(prev_stroke_keys) > 0
            and prev_stroke_keys[-1] not in [Key.RT, Key.RD, Key.RZ]
            and (Key.RG not in prev_stroke_keys or Key.RS not in prev_stroke_keys)
        ):
            prev_stroke.add_keys_maintain_steno_order([Key.RG, Key.RS])

            # Now actually replace the strokes.
            new_strokes = new_strokes[:-1]

    # If a stroke other than the last one in a multistroke entry conssists
    # entirely of 'TK' plus either 'AOE', 'E', 'EU', or 'U', then remvoe the
    # vowels. This is becuase such words (such as 'develop') can often be
    # pronunced in several of these ways.
    for stroke in new_strokes[:-1]:
        stroke_str = str(stroke)
        if (
            len(stroke_str) > 2
            and stroke_str[:2] == "TK"
            and stroke_str[2:] in ["AOE", "E", "EU", "U"]
        ):
            stroke.clear_all_vowels()

    return steno.StrokeSequence(new_strokes)


# Perform custom postprocessing after the entire dictionary's been generated.
def postprocess_generated_dictionary(word_and_translations):
    """Make custom modifications to the generated steno dictionary.

    This can be used to resolve homophone conflicts for example, by looping
    through all entries and checking if the the stroke sequence for the
    current word is already taken and if so, appending some distinguishing
    stroke to make it unique.

    Args:
        word_and_definitions: A list of tuples where the first item in each
            tuple is the word to translate into steno and the second item in
            the tuple is a list of strings, with each string being a way to
            write the word in steno.

    Returns:
        A string that is the stroke sequence after applying any modifications.
        This should be the input `steno_sequence` if no modifications are
        desired for this sequence.
    """

    # If a desired definition is already taken, append a 'W-B' stroke until
    # it's unique.
    used_translation_strs = set()
    disambiguator_stroke = steno.Stroke([Key.LW, Key.RB])

    for _, translations in word_and_translations:
        for translation in translations:
            while str(translation) in used_translation_strs:
                translation.append_stroke(disambiguator_stroke)

            used_translation_strs.add(str(translation))

    return word_and_translations
