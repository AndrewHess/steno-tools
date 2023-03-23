"""Read IPA pronunciations for words and split IPA words into syllables."""

import logging
import random
import re
import sys

from syllable import Syllable


def create_ipa_lookup_dictionary(filename):
    """Create a dictionary mapping words to IPA pronunciations.

    Args:
        filename: The name of a file specifying pronunciation in IPA for words.
            It should be a CSV file where each line has the format
            <word>,/<ipa1>/,/<ipa2>/...
            so that each prononciation (ipa1, ipa2, ...) is between slashes.

    Returns:
        A dictionary where each key is a word from the specified file and the
        value is a list with each element being the pronunciation for that word
        as specified by the IPA entries in the file for that word.
    """
    word_to_ipa = {}
    try:
        with open(filename, newline="", encoding="UTF-8") as csv_file:
            for line in csv_file:
                (key, value) = extract_key_and_value(line)
                word_to_ipa[key] = value

    except FileNotFoundError:
        log = logging.getLogger("dictionary_generator")
        log.error("The file `%s` does not exist.", filename)
        sys.exit(1)

    return word_to_ipa


def extract_key_and_value(line):
    """Extract the key and values from a string.

    Args:
        line: A string which should be of the form
            <key>,/<value1>/,/<value2>/,/<value3>/...
            so that everything before the first comma is the key, and each
            value is enclosed in forward slashes.

    Returns:
        A tuple where the first element is the key as a string and the second
        element is the list of values as strings.
    """
    split_line = line.strip().split(",", 1)  # Only split at the first comma.
    key = split_line[0]

    # Each value is between a pair of slashes.
    split_value = split_line[1].split("/")
    # Extract every second element.
    return (key, split_value[1::2])


# Find all the IPA symbols used by this dictionary.
def get_ipa_symbols(word_to_ipa):
    """Compile a set of IPA symbols used in the provided corpus.

    This function randomly selects entries of `word_to_ipa` and collects the
    IPA symbols used. So it's possible that not all symbols used in
    `word_to_ipa` will be given in the returned value.

    Args:
        word_to_ipa: A dictionary where each key is a string for a word, and
            the value is a list of strings with each string being the
            pronunciations for that word given in IPA.

    Returns:
        A Set of the IPA symbols used in `word_to_ipa`
    """

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


def split_ipa_into_syllables(ipa, config):
    """Split the pronunciation of a word given by IPA into syllables.

    This function was designed for splitting English words into syllables, and
    may not work properly for other languages. The algorithm used to split
    syllables is:
        1. Find each nucleus.
        2. For each nucleus, build the syllable's onset by prefixing the
           consonant sounds before the nucleus, so long as prepending the
           phoneme is phonologically valid.
        3. Append any unused consonant phonemes to the nucleus that it follows.

    This algorithm idea is from:
    https://linguistics.stackexchange.com/a/30934/41351

    Args:
        ipa: A string representing the pronunciation for some word in IPA.

    Returns:
        A list of Syllables (see syllable.py) for the word.
    """
    log = logging.getLogger("dictionary_generator")

    # The vowels and consonants lists must be sorted so that entries with more
    # characters appear earlier. This is so that when we look for these
    # phonemes in an IPA definition, we match the longest phonemes if we can.
    vowels = config.get_vowels()
    consonants = config.get_consonants()
    vowels = sorted(vowels, key=len, reverse=True)
    consonants = sorted(consonants, key=len, reverse=True)

    phonemes = vowels + consonants
    phoneme_to_marker = {}
    for i, phoneme in enumerate(phonemes):
        phoneme_to_marker[phoneme] = "(" + str(i) + ")"
    marker_to_phoneme = {value: key for key, value in phoneme_to_marker.items()}

    # Step 1: Locate each nucleus.
    ipa_copy = ipa
    for vowel in vowels:
        ipa_copy = ipa_copy.replace(vowel, phoneme_to_marker[vowel])

    syllables = []
    syllable_start_index = 0
    matches = re.finditer(r"\([0-9]+\)", ipa_copy)

    for match in matches:
        onset = ipa_copy[syllable_start_index : match.start()]
        marker = ipa_copy[match.start() : match.end()]
        nucleus = marker_to_phoneme[marker]
        coda = []
        syllables.append(Syllable(onset, nucleus, coda))
        syllable_start_index = match.end()

    if len(syllables) == 0:
        log.warning("No syllables found for `%s`", ipa)
        return None

    # Step 2: Work backwards from each nucleus to form the onset.
    leftovers = ipa_copy[syllable_start_index:]
    for consonant in consonants:
        leftovers = leftovers.replace(consonant, phoneme_to_marker[consonant])

    matches = re.finditer(r"\([0-9]+\)", leftovers)
    leftovers_lst = []
    for match in matches:
        marker = leftovers[match.start() : match.end()]
        leftovers_lst.append(marker_to_phoneme[marker])

    syllables[-1].coda = leftovers_lst

    for i in range(len(syllables) - 1, -1, -1):
        onset = syllables[i].onset
        new_onset = []

        # Convert the onset to a list of consonant phonemes.
        for consonant in consonants:
            onset = onset.replace(consonant, phoneme_to_marker[consonant])

        matches = re.finditer(r"\([0-9]+\)", onset)
        onset_lst = []
        for match in matches:
            marker = onset[match.start() : match.end()]
            onset_lst.append(marker_to_phoneme[marker])

        # Try to prepend each element of `onset_lst` to `new_onset`, but
        # comply with English orthography rules.
        # We need to iterate backwards since we'll be prepending.
        for k in range(len(onset_lst) - 1, -1, -1):
            phoneme = onset_lst[k]
            following_phoneme = new_onset[0] if len(new_onset) > 0 else None
            if config.can_prepend_to_onset(phoneme, following_phoneme):
                new_onset = [phoneme] + new_onset
            else:
                if i == 0:
                    # This syllable must take the leading consonants.
                    log.warning("Unable to assign leading consonants for `%s`", ipa)
                    return None

                # We can't prepend this phoneme to the syllable, so give
                # all the unused phonems to the previous syllable's coda.
                assert i > 0
                syllables[i - 1].coda = onset_lst[: k + 1]
                break

        syllables[i].onset = new_onset

    return syllables
