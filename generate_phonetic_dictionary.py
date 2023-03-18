import argparse
import random
import re
import sys


NO_STENO_MAPPING = 'NO_STENO_MAPPING'

class Syllable:
    def __init__(self, onset, nucleus, coda):
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda


    def str_debug(self):
        return str(self.onset) + str(self.nucleus) + str(self.coda)


    def __str__(self):
        onset = ''.join(self.onset)
        coda = ''.join(self.coda)
        return f'{onset + self.nucleus + coda}'
 

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

#    s = [syll.str_debug() for syll in syllables]
#    print(f'\t{"/".join(s)} <- deleteme')

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

        # Reverse the list so we can iterate it forwards.
        onset_lst.reverse()

        # Try to prepend each element of `onset_lst` to `new_onset`, but
        # comply with English orthography rules.
        for k, phoneme in enumerate(onset_lst):
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
                syllables[i - 1].coda = onset_lst[k:]
                break

        syllables[i].onset = new_onset

    
    return syllables


def can_prepend_to_onset(phoneme, onset):
    consonant_phonemes = ['b', 'd', 'f', 'h', 'j', 'k', 'm', 'n', 'p', 's', \
            't', 'v', 'w', 'z', 'ð', 'ŋ', 'ɡ', 'ɫ', 'ɹ', 'ʃ', 'ʒ', 'θ', \
            'tʃ', 'dʒ']

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
       (prev == 'ɹ' and phoneme in ['p', 'b', 't', 'ɹ', 'd', 'k', 'ɡ']) or \
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
    if phoneme == 's' and prev in ['s', 'p', 'k']:
        return True

    # Allow 's' plus nasal other than 'ŋ'.
    if phoneme == 's' and prev in ['m', 'n']:
        return True

    # Allow 's' plus voiceless non-sibilant fricative:
    if phoneme == 's' and prev in ['f', 'θ']:
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
        'u': 'AOU',
        'ɝ': 'UR',
        'ɑ': 'O',
        'aɪ': 'AOEU',
        'eɪ': 'AEU',
        'ɔɪ': 'OI',
        'aʊ': 'OU',
        'oʊ': 'OE',
        'ɪɹ': 'AOER',
        'ɛɹ': 'AEUR',
        'ɔɹ': 'OR',
        'ʊɹ': 'AOUR',
        'ɑɹ': 'AR',
    }
    left_consonant_to_steno = {
        'b': 'PW',
        'd': 'TK',
        'f': 'TP',
        'h': 'H',
        'j': 'Y',
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
        's': ['S', 'F', '*S'],
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
    }

    translations = []  # List of all ways to stroke the syllable sequence.

    for i, syllable in enumerate(syllables):
        ways_to_stroke_onset = build_stroke(syllable.onset, left_consonant_to_steno)
        ways_to_stroke_nucleus = build_stroke([syllable.nucleus], vowel_to_steno)
        ways_to_stroke_coda = build_stroke(syllable.coda, right_consonant_to_steno)

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

        if i == 0:
            translations = ways_to_stroke_syllable
        else:
            new_translations = []
            for prev_strokes in translations:
                for stroke in ways_to_stroke_syllable:
                    new_translations.append(prev_strokes + '/' + stroke)

            translations = new_translations

    return translations


def build_stroke(phonemes, phonemes_to_steno):
    ways_to_stroke = ['']

    for i, phoneme in enumerate(phonemes):
        steno = phonemes_to_steno[phoneme]
        if steno == NO_STENO_MAPPING:
            print(f'Warning: No steno mapping for phoneme {phoneme} in {[str(s) for s in syllables]}', file=sys.stderr)
            return None
        elif isinstance(steno, list):
            new_ways_to_stroke = []
            for keys in steno:
                for partial_stroke in ways_to_stroke:
                    new_ways_to_stroke.append(partial_stroke + keys)

            ways_to_stroke = new_ways_to_stroke
        else:
            for i in range(len(ways_to_stroke)):
                ways_to_stroke[i] += steno

    return ways_to_stroke


# Clean up the stroke so it's valid for a steno dictionary. The provided
# stroke may have repeated letters, any number of *'s in any position, and
# may lack the `-` when no vowels are included.
def stroke_to_valid_steno(stroke):
    star = ('*' in stroke)
    contains_vowel = False

    for vowel in ['A', 'O', 'E', 'U']:
        if vowel in stroke:
            contains_vowel = True

    # TODO
    pass


def get_args():
    # Create an ArgumentParser object.
    parser = argparse.ArgumentParser(description='Generate steno strokes phonetically.')

    # Add positional arguments.
    parser.add_argument('ipa_file', type=str, help='the IPA CSV dictionary')
    parser.add_argument('word_list_file', type=str, help='the file containing words generate strokes for')

    # Parse the command line arguments
    return parser.parse_args()


def main():
    args = get_args()

    word_to_ipa = create_ipa_lookup_dictionary(args.ipa_file)
    symbols = list(get_ipa_symbols(word_to_ipa))
    symbols.sort()
    print(f'IPA symbols: {symbols}')

    with open(args.word_list_file, 'r') as file:
        for line in file:
            word = line.strip()

            print(f'{word}')
            for ipa in word_to_ipa[word]:
                syllables = split_ipa_into_syllables(ipa)
                if syllables is None:
                    continue
                s = [str(syll) for syll in syllables]
                print(f'\t{"/".join(s)}', end=' -> ')
                steno = syllables_to_steno(syllables)
                print(f'{", ".join(steno)}')


if __name__ == '__main__':
    main()
