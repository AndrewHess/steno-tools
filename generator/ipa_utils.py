import random
import re
import sys

import config
from syllable import Syllable


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
    # The vowels and consonants lists must be sorted so that entries with more
    # characters appear earlier. This is so that when we look for these
    # phonemes in an IPA definition, we match the longest phonemes if we can.
    vowels = config.VOWELS
    consonants = config.CONSONANTS
    vowels = sorted(vowels, key=len, reverse=True)
    consonants = sorted(consonants, key=len, reverse=True)

    phonemes = vowels + consonants
    phoneme_to_marker = {}
    for i, phoneme in enumerate(phonemes):
        phoneme_to_marker[phoneme] = '(' + str(i) + ')'
    marker_to_phoneme = {value: key for key, value in phoneme_to_marker.items()}

    # Step 1: Locate each nucleus.
    ipa_copy = ipa
    for vowel in vowels:
        ipa_copy = ipa_copy.replace(vowel, phoneme_to_marker[vowel])

    syllables = []
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
    for consonant in consonants:
        leftovers = leftovers.replace(consonant, phoneme_to_marker[consonant])

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
        for consonant in consonants:
            onset = onset.replace(consonant, phoneme_to_marker[consonant])

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
            if config.can_prepend_to_onset(phoneme, new_onset):
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