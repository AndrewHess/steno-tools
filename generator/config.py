import re
import sys

from syllable import Syllable
import utils
from utils import NO_STENO_MAPPING

def split_ipa_into_syllables(ipa):
    single_vowels = []
    single_vowels.append('ɪ')  # Ex: mYth, prEtty, wOmen
    single_vowels.append('ɛ')  # Ex: brEAd, mAny, mEn
    single_vowels.append('æ')  # Ex: cAt, fAst, pAss
    single_vowels.append('ə')  # Ex: bUn, dOne, crUmb
    single_vowels.append('ʊ')  # Ex: wOOd, pUt
    single_vowels.append('i')  # Ex: bEE, mEAt
    single_vowels.append('ɔ')  # Ex: brAWl, tAll, wrOUght, but not rot
    single_vowels.append('u')  # Ex: fOOd, whO, blUE
    single_vowels.append('ɝ')  # Ex: pURR, pERson, dIRty, doctOR
    single_vowels.append('ɑ')  # Ex: rOt, but not wrought

    double_vowels = []
    double_vowels.append('aɪ')  # Ex: EYE, trY, nIght
    double_vowels.append('eɪ')  # Ex: AYE, glAde
    double_vowels.append('ɔɪ')  # Ex: bOY, nOIse
    double_vowels.append('aʊ')  # Ex: clOWn, nOUn
    double_vowels.append('oʊ')  # Ex: OWE, blOW
    double_vowels.append('ɪɹ')  # Ex: fEAR, dEER, drEARy
    double_vowels.append('ɛɹ')  # Ex: AIR, glARe, stARE
    double_vowels.append('ɔɹ')  # Ex: gORe, bOAR, dOOR
    double_vowels.append('ʊɹ')  # Ex: pURe, ensURe
    double_vowels.append('ɑɹ')  # Ex: cAR, sonAR, ARctic
    double_vowels.append('ju')  # Ex: YOU, fEW, pEWter

#    triple_vowels = []
#    triple_vowels.append('ʃən')  # Ex: ruSSIAN, addiTIONal, SHUNNed

    single_consonants = ['b', 'd', 'f', 'h', 'j', 'k', 'm', 'n', 'p', 's', 't', 'v', 'w', 'z']
    single_consonants.append('ð')  # Ex: worTHy, furTHer
    single_consonants.append('ŋ')  # Ex: struNG, fliNG
    single_consonants.append('ɡ')  # Ex: doG, Glue  Note: this is a UTF-8 char, not the letter G.
    single_consonants.append('ɫ')  # Ex: fiLL, terminaL
    single_consonants.append('ɹ')  # Ex: bRook, gRay
    single_consonants.append('ʃ')  # Ex: wiSH, puSH
    single_consonants.append('ʒ')  # Ex: leiSure, fuSion
    single_consonants.append('θ')  # Ex: youTH, THin

    double_consonants = []
    double_consonants.append('tʃ')  # Ex: gliTCH, beaCH
    double_consonants.append('dʒ')  # Ex: JuDGe, friDGe, Germ
    double_consonants.append('st')  # Ex: firST heiST, burST

    stress_markers = ['ˈ', 'ˌ']

    phonemes = single_vowels + double_vowels + single_consonants + double_consonants
    phoneme_to_marker = {}
    for i, phoneme in enumerate(phonemes):
        phoneme_to_marker[phoneme] = '(' + str(i) + ')'
    marker_to_phoneme = {value: key for key, value in phoneme_to_marker.items()}

    # Step 1: Locate each nucleus.
    ipa_copy = ipa
    for dv in double_vowels:
        ipa_copy = ipa_copy.replace(dv, phoneme_to_marker[dv])
    for sv in single_vowels:
        ipa_copy = ipa_copy.replace(sv, phoneme_to_marker[sv])

    syllables = []
    vowels = single_vowels + double_vowels
    syllable_start_index = 0
    matches = [match for match in re.finditer('\([0-9]+\)', ipa_copy)]

    for match in matches:
        onset = ipa_copy[syllable_start_index:match.start()]
        marker = ipa_copy[match.start():match.end()]
        nucleus = marker_to_phoneme[marker]
        coda = []
        syllables.append(Syllable(onset, nucleus, coda))
        syllable_start_index = match.end()

    if len(syllables) == 0:
        print(f'Warning: No syllables found for {ipa}', file=sys.stderr)
        return None

    # Step 2: Work backwards from each nucleus to form the onset.
    leftovers = ipa_copy[syllable_start_index:]
    for dc in double_consonants:
        leftovers = leftovers.replace(dc, phoneme_to_marker[dc])
    for sc in single_consonants:
        leftovers = leftovers.replace(sc, phoneme_to_marker[sc])

    matches = [match for match in re.finditer('\([0-9]+\)', leftovers)]
    leftovers_lst = []
    for match in matches:
        marker = leftovers[match.start():match.end()]
        leftovers_lst.append(marker_to_phoneme[marker])

    syllables[-1].coda = leftovers_lst

    for i in range(len(syllables) - 1, -1, -1):
        onset = syllables[i].onset
        new_onset = []

        # Convert the onset to a list of consonant phonemes.
        for dc in double_consonants:
            onset = onset.replace(dc, phoneme_to_marker[dc])
        for sc in single_consonants:
            onset = onset.replace(sc, phoneme_to_marker[sc])

        matches = [match for match in re.finditer('\([0-9]+\)', onset)]
        onset_lst = []
        for match in matches:
            marker = onset[match.start():match.end()]
            onset_lst.append(marker_to_phoneme[marker])

        # Try to prepend each element of `onset_lst` to `new_onset`, but
        # comply with English orthography rules.
        # We need to iterate backwards since we'll be prepending.
        for k in range(len(onset_lst) - 1, -1, -1):
            phoneme = onset_lst[k]
            if can_prepend_to_onset(phoneme, new_onset):
                new_onset = [phoneme] + new_onset
            else:
                if i == 0:
                    # This syllable must take the leading consonants.
                    print(f'Warning: unable to assign leading consonants for {ipa}')
                    return None

                # We can't prepend this phoneme to the syllable, so give
                # all the unused phonems to the previous syllable's coda.
                assert(i > 0)
                syllables[i - 1].coda = onset_lst[:k + 1]
                break

        syllables[i].onset = new_onset

    return syllables


def can_prepend_to_onset(phoneme, onset):
    consonant_phonemes = ['b', 'd', 'f', 'h', 'j', 'k', 'm', 'n', 'p', 's', \
            't', 'v', 'w', 'z', 'ð', 'ŋ', 'ɡ', 'ɫ', 'ɹ', 'ʃ', 'ʒ', 'θ', \
            'tʃ', 'dʒ', 'st']

    if phoneme not in consonant_phonemes:
        print(f'Unknown consonant phoneme: {phoneme}')
        return False

    # English syllable structure is (C)^{3}V(C)^{5}, so no more than three
    # consonant sounds in the onset.
    if len(onset) >= 3:
        return False

    # All following rules are from https://en.wikipedia.org/wiki/English_phonology
    if onset == []:
        return phoneme != 'ŋ'

    prev = onset[0]

    # Allow stop plus approximant other than 'j'.
    if (prev == 'ɫ' and phoneme in ['p', 'b', 'k', 'ɡ']) or \
       (prev == 'ɹ' and phoneme in ['p', 'b', 't', 'd', 'k', 'ɡ']) or \
       (prev == 'w' and phoneme in ['p', 't', 'd', 'g', 'k']):
        return True

    # Allow voicless fricative or 'v' plus approximant other than 'j'.
    if (prev == 'ɫ' and phoneme in ['f', 's', 'θ', 'ʃ']) or \
       (prev == 'ɹ' and phoneme in ['f', 'θ', 'ʃ']) or \
       (prev == 'w' and phoneme in ['h', 's', 'θ', 'v']):
        return True

    # Allow consonants other than 'ɹ' and 'w' followed by 'j' (which should
    # be followed by some form of 'u').
    if len(onset) == 1 and prev == 'j' and phoneme not in ['ɹ', 'w']:
        return True

    # Allow 's' plus voiceless stop:
    if phoneme == 's' and prev in ['p', 't', 'k']:
        return True

    # Allow 's' plus nasal other than 'ŋ'.
    if phoneme == 's' and prev in ['m', 'n']:
        return True

    # Allow 's' plus voiceless non-sibilant fricative:
    if phoneme == 's' and prev in ['f', 'θ']:
        return True

    ####################### Custom Rules #######################
    if phoneme == 'st' and prev in ['ɹ', 'w']:
        return True

    return False


def syllables_to_steno(syllables):
    vowel_to_steno = {
        'ɪ': 'EU',
        'ɛ': 'E',
        'æ': 'A',
        'ə': 'U',
        'ʊ': 'AO',
        'i': 'AOE',
        'ɔ': 'AU',
        'u': 'AOU',  # Note: this is the same as for 'ju'.
        'ɝ': 'UR',
        'ɑ': 'O',
        'aɪ': 'AOEU',
        'eɪ': 'AEU',
        'ɔɪ': 'OEU',
        'aʊ': 'OU',
        'oʊ': 'OE',
        'ɪɹ': 'AOER',
        'ɛɹ': 'AEUR',
        'ɔɹ': 'OR',
        'ʊɹ': 'AOUR',
        'ɑɹ': 'AR',
        'ju': 'AOU',  # Note: this is the same as for just 'u'.
    }
    left_consonant_to_steno = {
        'b': 'PW',
        'd': 'TK',
        'f': 'TP',
        'h': 'H',
        'j': 'KWR',
        'k': 'K',
        'm': 'PH',
        'n': 'TPH',
        'p': 'P',
        's': 'S',
        't': 'T',
        'v': 'SR',
        'w': 'W',
        'z': 'SWR',
        'ð': 'TH',
        'ŋ': NO_STENO_MAPPING,
        'ɡ': 'TKPW',
        'ɫ': 'HR',
        'ɹ': 'R',
        'ʃ': 'SH',
        'ʒ': 'SKH',
        'θ': 'TH',
        'tʃ': 'KH',
        'dʒ': 'SKWR',
        'st': 'ST',
    }
    right_consonant_to_steno = {
        'b': 'B',
        'd': 'D',
        'f': 'F',
        'h': NO_STENO_MAPPING,
        'j': NO_STENO_MAPPING,
        'k': 'BG',
        'm': 'PL',
        'n': 'PB',
        'p': 'P',
        's': ['S', 'F'],
        't': 'T',
        'v': 'FB',
        'w': NO_STENO_MAPPING,
        'z': 'Z',
        'ð': '*T',
        'ŋ': 'PBG',
        'ɡ': 'G',
        'ɫ': 'L',
        'ɹ': 'R',
        'ʃ': 'RB',
        'ʒ': NO_STENO_MAPPING,
        'θ': '*T',
        'tʃ': 'FP',
        'dʒ': 'PBLG',
        'st': ['FT', '*S']
    }

    translations = []  # List of all ways to stroke the syllable sequence.

    for i, syllable in enumerate(syllables):
        ways_to_stroke_onset = utils.get_stroke_components(syllable.onset, left_consonant_to_steno)
        ways_to_stroke_nucleus = utils.get_stroke_components([syllable.nucleus], vowel_to_steno)
        ways_to_stroke_coda = utils.get_stroke_components(syllable.coda, right_consonant_to_steno)

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
            stroke = utils.build_stroke_from_components(stroke_components)

            if stroke is not None:
                potential_strokes.append(stroke)

        if len(potential_strokes) == 0:
            print(f'No valid way to stroke the syllable `{syllable}`')
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
        new_steno = postprocess_steno_sequence(steno, syllables)

        if new_steno is not None:
            new_translations.append(new_steno)

    translations = new_translations

    return translations

def postprocess_steno_sequence(steno_sequence, syllables_ipa):
    syllables_steno = steno_sequence.split('/')
    new_syllables_steno = syllables_steno.copy()

    # If a stroke after the first has 'U', 'EU', or 'E' as its vowel and it has
    # following consonants, replace the vowel cluster with '-' (or '*' if the
    # stroke is starred).
    for i in range(1, len(syllables_steno)):
        pattern = '([STKPWHR]*)([AO]*)([*]?)([EU]*)([FRPBLGTSDZ]*)'
        match = re.match(pattern, syllables_steno[i])

        if match:
            (left, ao, star, eu, right) = match.groups()

        if ao == '' and len(eu) != 0 and right != '':
            # Remove the vowels.
            middle = '*' if star == '*' else '-'
            new_syllables_steno[i] = left + middle + right

    # If the final sound in a syllable is an 's', it should be with the 'S' key
    # not the 'F' key, even though making 's' with 'F' is allowed if there's
    # another sound later in the syllable.
    for steno, ipa in zip(new_syllables_steno, syllables_ipa):
        if steno[-1] == 'F' and len(ipa.coda) > 0 and ipa.coda[-1] == 's':
            # This is invalid.
            return None

    # If the final stroke is 'SH-PB', fold it into the previous stroke as '-GS'.
    if len(new_syllables_steno) > 1 and new_syllables_steno[-1] == 'SH-PB':
        prev = new_syllables_steno[-2]
        if prev[-1] not in ['T', 'D', 'Z'] and 'GS' not in prev:
            # We can fold it in; just make sure not to repeat a key.
            if prev[-1] == 'G':
                prev += 'S'
            elif prev[-1] == 'S':
                # We already know there's not a right-side 'T' or 'G', so we
                # can put a 'G' immediately before the 'S'.
                prev = prev[:-1] + 'GS'
            else:
                prev += 'GS'

            # Now actually replace the strokes.
            new_syllables_steno = new_syllables_steno[:-1]
            new_syllables_steno[-1] = prev

    return '/'.join(new_syllables_steno)


# Perform custom postprocessing after the entire dictionary's been generated.
def postprocess_generated_dictionary(word_and_definitions):
    # If a desired definition is already taken, append a 'W-B' stroke until
    # it's unique.
    used_definitions = set()

    for i, (_, definitions) in enumerate(word_and_definitions):
        for k, strokes in enumerate(definitions):
            while strokes in used_definitions:
                strokes += '/W-B'

            definitions[k] = strokes
            used_definitions.add(strokes)

    return word_and_definitions
