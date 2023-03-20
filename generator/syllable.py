"""A syllable written with IPA symbols."""


class Syllable:
    """A syllable written with IPA symbols.

    Attributes:
        onset:
            A list of strings. Each string is a consonant phoneme in IPA.
            Together, the elements of the list make the syllable's onset (the
            consonant sounds before the vowel).
        nucleus:
            A string that is the syllable's vowel sound written in IPA.
        coda:
            A list of strings. Each string is a consonant phoneme in IPA.
            Together, the elements of the list make the syllable's coda (the
            consonant sounds after the vowel).
    """

    def __init__(self, onset, nucleus, coda):
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda

    def str_debug(self):
        """Return a string of the syllable for debugging purposes."""
        return str(self.onset) + str(self.nucleus) + str(self.coda)

    def __str__(self):
        onset = "".join(self.onset)
        coda = "".join(self.coda)
        return f"{onset + self.nucleus + coda}"
