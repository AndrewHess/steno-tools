"""Manage steno keys, strokes, and sequences of strokes."""

from enum import Enum
import logging


class MissingDashInStrokeError(Exception):
    """Error for when a steno stroke string is missing a middle.

    This should be thrown when a string representing a stroke doesn't have any
    vowels and also doesn't have an asterisk.
    """


class OutOfStenoOrderError(Exception):
    """Error for when the keys of a steno stroke are out of order."""


class Key(Enum):
    """Enum for the keys on a steno keyboard."""

    NUM = (0, "#")
    LS = (1, "S")
    LT = (2, "T")
    LK = (3, "K")
    LP = (4, "P")
    LW = (5, "W")
    LH = (6, "H")
    LR = (7, "R")
    A = (8, "A")
    O = (9, "O")
    STAR = (10, "*")
    E = (11, "E")
    U = (12, "U")
    RF = (13, "F")
    RR = (14, "R")
    RP = (15, "P")
    RB = (16, "B")
    RL = (17, "L")
    RG = (18, "G")
    RT = (19, "T")
    RS = (20, "S")
    RD = (21, "D")
    RZ = (22, "Z")

    def __init__(self, index, letter):
        self.index = index
        self.letter = letter


class Stroke:
    """A single steno stroke."""

    def __init__(self, keys=None):
        self._active_keys_bitmap = [False] * len(Key)
        self._last_active_pos = -1

        if keys is not None:
            self.add_keys_maintain_steno_order(keys)

    def __eq__(self, other):
        if self._last_active_pos != other._last_active_pos:
            return False

        return self._active_keys_bitmap == other._active_keys_bitmap

    def __lt__(self, other):
        for i, (active_self, active_other) in enumerate(
            zip(self._active_keys_bitmap, other._active_keys_bitmap)
        ):
            if active_self and not active_other:
                return other._last_active_pos > i

            if active_other and not active_self:
                return self._last_active_pos < i

        return False

    def __hash__(self):
        return hash(tuple(self._active_keys_bitmap))

    def __str__(self):
        result = ""
        has_vowel_or_star = False

        for key in Key:
            if self._active_keys_bitmap[key.index]:
                result += key.letter

                if key.letter in ["A", "O", "*", "E", "U"]:
                    has_vowel_or_star = True

            if key is Key.U and not has_vowel_or_star:
                result += "-"

        return result

    @staticmethod
    def from_string(stroke_str):
        """Create a stroke from its string representation.

        If the input string doesn't contain any vowels or an asterisk, it must
        include a "-" to indicate separation between the left and right
        consonants, even if only consonants on one side are present in the
        stroke.

        Args:
            stroke_str: A string representing a single steno stroke. For
                example, "TP*EURS", "S-P".

        Raises:
            MissingDashInStrokeError: If the input string doesn't have any
                vowels and it doesn't have an asterisk and it doens't have a
                dash to denote the split between left and right consonants.
            OutOfStenoOrderError: If the keys in the input string are out of
                steno order.

        Returns:
            The stroke corresponding to the input string.
        """

        keys = []
        past_middle = False

        for key_str in stroke_str:
            if key_str == "-":
                past_middle = True
                continue

            if key_str == "#":
                keys.append(Key.NUM)
                continue

            for key in [Key.A, Key.O, Key.STAR, Key.E, Key.U]:
                if key_str == key.letter:
                    past_middle = True
                    keys.append(key)
                    break

            consonants = [Key.LS, Key.LT, Key.LK, Key.LP, Key.LW, Key.LH, Key.LR]
            if past_middle:
                consonants = [
                    Key.RF,
                    Key.RR,
                    Key.RP,
                    Key.RB,
                    Key.RL,
                    Key.RG,
                    Key.RT,
                    Key.RS,
                    Key.RD,
                    Key.RZ,
                ]

            for key in consonants:
                if key_str == key.letter:
                    keys.append(key)
                    break

        if not past_middle:
            raise MissingDashInStrokeError()

        log = logging.getLogger("dictionary_generator")
        log.debug("Converted `%s` to keys: `%s`", stroke_str, keys)

        try:
            stroke = Stroke(keys=keys)
        except OutOfStenoOrderError as err:
            raise OutOfStenoOrderError(f"`{stroke_str}` is out of steno order") from err

        return stroke

    def add_keys_maintain_steno_order(self, keys):
        """Add keys to this stroke while ensuring steno order is maintained.

        Args:
            keys: list(Key)

        Raises:
            OutOfStenoOrderError: If appending the keys to the stroke would put
            the stroke out of steno order.
        """

        for key in keys:
            if key not in [Key.NUM, Key.STAR]:
                if key.index < self._last_active_pos:
                    raise OutOfStenoOrderError()

                self._last_active_pos = key.index

            self._active_keys_bitmap[key.index] = True

    def add_keys_ignore_steno_order(self, keys):
        """Add keys to this stroke regardless of steno order.

        Note: Use add_keys_maintain_steno_order() instead if you want to ensure
        that appending the keys does not mess up the stroke's steno order.

        Args:
            keys: list(Key)
        """

        for key in keys:
            if key not in [Key.NUM, Key.STAR]:
                self._last_active_pos = key.index

            self._active_keys_bitmap[key.index] = True

    def clear_keys(self, keys):
        """Removes the specified keys from this stroke.

        This works even if some of the keys are not already in the stroke.

        Args:
            keys: list(Key)
        """

        for key in keys:
            self._active_keys_bitmap[key.index] = False

        # Update `self._last_active_pos`.
        self._last_active_pos = -1
        for key in reversed(Key):
            if self._active_keys_bitmap[key.index] and key not in [Key.NUM, Key.STAR]:
                self._last_active_pos = key.index
                break

    def clear_all_vowels(self):
        """Remove all vowels from this stroke."""

        self.clear_keys([Key.A, Key.O, Key.E, Key.U])

    def get_vowels(self):
        """Return the list of vowel keys in this stroke."""

        active_vowels = []

        for key in [Key.A, Key.O, Key.E, Key.U]:
            if self._active_keys_bitmap[key.index]:
                active_vowels.append(key)

        return active_vowels

    def get_last_key(self):
        """Return the last key in this stroke, or None if there are no keys."""

        if self._last_active_pos == -1:
            return None

        return list(Key)[self._last_active_pos]

    def get_keys(self):
        """Return the list of keys present in this stroke."""

        keys = []

        for key in Key:
            if self._active_keys_bitmap[key.index]:
                keys.append(key)

        return keys

    def is_empty(self):
        """Return True if no keys are active."""

        return not self.get_keys()

    def has_left_consonant(self):
        """Return True if the stroke has a left consonant key active."""

        return self._has_active_key_between(Key.LS, Key.LR)

    def has_right_consonant(self):
        """Return True if the stroke has a right consonant key active."""

        return self._has_active_key_between(Key.RF, Key.RZ)

    def _has_active_key_between(self, min_key, max_key):
        """True if a key between min_key and max_key (both inclusive) is on."""
        for i in range(min_key.index, max_key.index + 1):
            if self._active_keys_bitmap[i]:
                return True

        return False

    def left_consonants_match(self, other):
        """Return True both strokes have the same left consonants."""

        return self._regions_match(other, Key.LS, Key.LR, True)

    def vowels_match(self, other):
        """Return True both strokes have the same vowels."""

        return self._regions_match(other, Key.A, Key.U, True)

    def right_consonants_match(self, other):
        """Return True both strokes have the same right consonants."""

        return self._regions_match(other, Key.RF, Key.RZ, True)

    def _regions_match(self, other, min_key, max_key, ignore_star):
        self_region = self._get_active_keys_between(min_key, max_key, ignore_star)
        other_region = other._get_active_keys_between(min_key, max_key, ignore_star)

        return self_region == other_region

    def _get_active_keys_between(self, min_key, max_key, ignore_star):
        keys = []
        key_enum_list = list(Key)

        for i in range(min_key.index, max_key.index + 1):
            if self._active_keys_bitmap[i]:
                if ignore_star and key_enum_list[i] is Key.STAR:
                    continue

                keys.append(key_enum_list[i])

        return keys


class StrokeSequence:
    """A series of Strokes, meant to represent one translation."""

    def __init__(self, strokes=None):
        self._strokes = strokes if strokes is not None else []

    def __eq__(self, other):
        return self._strokes == other._strokes

    def __hash__(self):
        return hash(tuple(self._strokes))

    def __lt__(self, other):
        if len(self._strokes) < len(other._strokes):
            return True

        if len(self._strokes) > len(other._strokes):
            return False

        for stroke1, stroke2 in zip(self._strokes, other._strokes):
            if stroke1 < stroke2:
                return True

            if stroke1 > stroke2:
                return False

        return False

    def __str__(self):
        stroke_strings = [str(stroke) for stroke in self._strokes if not stroke.is_empty()]
        return "/".join(stroke_strings)

    def get_strokes(self):
        """Return the list of strokes comprising this sequence."""

        return self._strokes

    def append_stroke(self, stroke):
        """Append a stroke to this sequence."""

        self._strokes.append(stroke)

    def set_strokes(self, strokes):
        """Overwrite this sequence with the provided list of strokes."""

        self._strokes = strokes
