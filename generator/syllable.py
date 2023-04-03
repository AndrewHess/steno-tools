"""A syllable written with IPA symbols."""

import enum
from typing import NamedTuple


class SyllableRegion(enum.Enum):
    """A region of a syllable."""

    ONSET = enum.auto()
    NUCLEUS = enum.auto()
    CODA = enum.auto()


class SyllableAtom(NamedTuple):
    """The smallest block of a syllable."""

    phoneme: str
    region: SyllableRegion


class Syllable:
    """A collection of SyllableAtoms constituting a single syllable.

    Attributes:
        atoms: A list of SyllableAtoms. Concatenating the atoms and reading the
            phonemes from each atom gives the pronunciation of the syllable.
    """

    def __init__(self, onset, nucleus, coda):
        """Creates a Syllable.

        Args:
            onset: A list of strings. Each string is a phoneme in the onset.
            nucleus: A string specifying the IPA symbols for the nucleus.
            coda: A list of strings. Each string is a phoneme in the coda.
        """

        self._atoms = []

        for phoneme in onset:
            self._atoms.append(SyllableAtom(phoneme, SyllableRegion.ONSET))

        self._atoms.append(SyllableAtom(nucleus, SyllableRegion.NUCLEUS))

        for phoneme in coda:
            self._atoms.append(SyllableAtom(phoneme, SyllableRegion.CODA))

    def __str__(self):
        return "".join([phoneme for phoneme, _ in self._atoms])

    def map_atoms(self, atom_tuples_to_obj):
        """Map the phonemes of this syllable to objects.

        Args:
            atom_tuples_to_obj: A dictionary where the keys are tuples of
                SyllableAtoms. There's no guarantee on what the values are.

        Returns:
            A list containing only elements which are values from the input
            dictionary. The list is formed by iterating this syllable's
            SyllableAtoms and at each step checking for the longest key in
            `atom_tuples_to_obj` that matches the next `n` elements (where `n`
            is the length of that specific key); those SyllableAtoms are then
            mapped to the corresponding value in `atom_tuples_to_obj`.
        """
        objs = []
        max_tuple_length = len(max(atom_tuples_to_obj, key=len))

        start = 0
        while start < len(self._atoms):
            found_match = False

            for length in range(max_tuple_length + 1, 0, -1):
                end = start + length
                if end > len(self._atoms):
                    continue

                obj = atom_tuples_to_obj.get(tuple(self._atoms[start:end]), None)

                if obj is not None:
                    objs.append(obj)
                    start += length
                    found_match = True
                    break  # Break out of the inner loop

            if not found_match:
                print(f"No match for {self._atoms[start]}")
                return None

        return objs

    def is_last_phoneme_s(self):
        """Return True if the last phoneme of this syllable is 's'."""
        if len(self._atoms) == 0:
            return False

        return self._atoms[-1].phoneme == "s"
