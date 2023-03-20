"""Configuration for the steno dictionary generator."""

import logging
import re


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
    "ɪ": "EU",
    "ɛ": "E",
    "æ": "A",
    "ə": "U",
    "ʊ": "AO",
    "i": "AOE",
    "ɔ": "AU",
    "u": "AOU",  # Note: this is the same as for 'ju'.
    "ɝ": "UR",
    "ɑ": "O",
    "aɪ": "AOEU",
    "eɪ": "AEU",
    "ɔɪ": "OEU",
    "aʊ": "OU",
    "oʊ": "OE",
    "ɪɹ": "AOER",
    "ɛɹ": "AEUR",
    "ɔɹ": "OR",
    "ʊɹ": "AOUR",
    "ɑɹ": "AR",
    ############ Extra Vowel Clusters ############
    "ju": "AOU",  # Note: this is the same as for just 'u'.
    "jə": "AOU",
    "ɝtʃ": "UFRPB",
    "ɑɹtʃ": "AFRPB",
    "ɔɹtʃ": "OFRPB",
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
    "b": "PW",
    "d": "TK",
    "f": "TP",
    "h": "H",
    "j": "KWR",
    "k": "K",
    "m": "PH",
    "n": "TPH",
    "p": "P",
    "s": "S",
    "t": "T",
    "v": "SR",
    "w": "W",
    "z": "SWR",
    "ð": "TH",
    "ŋ": NO_STENO_MAPPING,
    "ɡ": "TKPW",
    "ɫ": "HR",
    "ɹ": "R",
    "ʃ": "SH",
    "ʒ": "SKH",
    "θ": "TH",
    "tʃ": "KH",
    "dʒ": "SKWR",
    "st": "ST",
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
    "b": "B",
    "d": "D",
    "f": "F",
    "h": NO_STENO_MAPPING,
    "j": NO_STENO_MAPPING,
    "k": "BG",
    "m": "PL",
    "n": "PB",
    "p": "P",
    "s": ["S", "F"],
    "t": "T",
    "v": "FB",
    "w": NO_STENO_MAPPING,
    "z": "Z",
    "ð": "*T",
    "ŋ": "PBG",
    "ɡ": "G",
    "ɫ": "L",
    "ɹ": "R",
    "ʃ": "RB",
    "ʒ": NO_STENO_MAPPING,
    "θ": "*T",
    "tʃ": "FP",
    "dʒ": "PBLG",
    "st": ["FT", "*S"],
    "ŋk": "PBG",  # Note: this colides with 'ŋ'.
    "mp": "*PL",
    "ntʃ": "FRPB",
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

    syllables_steno = steno_sequence.split("/")
    new_syllables_steno = syllables_steno.copy()

    # If a stroke after the first has 'U', 'EU', or 'E' as its vowel and it has
    # following consonants, replace the vowel cluster with '-' (or '*' if the
    # stroke is starred).
    for i in range(1, len(syllables_steno)):
        pattern = "([STKPWHR]*)([AO]*)([*]?)([EU]*)([FRPBLGTSDZ]*)"
        match = re.match(pattern, syllables_steno[i])

        if match:
            (left, a_and_o, star, e_and_u, right) = match.groups()

        if a_and_o == "" and len(e_and_u) != 0 and right != "":
            # Remove the vowels.
            middle = "*" if star == "*" else "-"
            new_syllables_steno[i] = left + middle + right

    # If the final sound in a syllable is an 's', it should be with the 'S' key
    # not the 'F' key, even though making 's' with 'F' is allowed if there's
    # another sound later in the syllable.
    for steno, ipa in zip(new_syllables_steno, syllables_ipa):
        if steno[-1] == "F" and len(ipa.coda) > 0 and ipa.coda[-1] == "s":
            # This is invalid.
            return None

    # If the final stroke is 'SH-PB', fold it into the previous stroke as '-GS'.
    if len(new_syllables_steno) > 1 and new_syllables_steno[-1] == "SH-PB":
        prev = new_syllables_steno[-2]
        if prev[-1] not in ["T", "D", "Z"] and "GS" not in prev:
            # We can fold it in; just make sure not to repeat a key.
            if prev[-1] == "G":
                prev += "S"
            elif prev[-1] == "S":
                # We already know there's not a right-side 'T' or 'G', so we
                # can put a 'G' immediately before the 'S'.
                prev = prev[:-1] + "GS"
            else:
                prev += "GS"

            # Now actually replace the strokes.
            new_syllables_steno = new_syllables_steno[:-1]
            new_syllables_steno[-1] = prev

    return "/".join(new_syllables_steno)


# Perform custom postprocessing after the entire dictionary's been generated.
def postprocess_generated_dictionary(word_and_definitions):
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
    used_definitions = set()

    for _, (_, definitions) in enumerate(word_and_definitions):
        for k, strokes in enumerate(definitions):
            while strokes in used_definitions:
                strokes += "/W-B"

            definitions[k] = strokes
            used_definitions.add(strokes)

    return word_and_definitions
