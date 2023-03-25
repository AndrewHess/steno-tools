"""Configuration for the steno dictionary generator."""

import copy
import logging
import schema
import yaml

import steno


NO_STENO_MAPPING = "NO_STENO_MAPPING"

_STR_ANY_SET_OF_KEYS = "ANY_SET_OF_KEYS"
_STR_ANY_NON_EMPTY_SET_OF_KEYS = "ANY_NON_EMPTY_SET_OF_KEYS"
_STR_NEXT_STROKE = "NEXT_STROKE"
_STR_PREVIOUS_STROKE = "PREVIOUS_STROKE"

_STR_VOWELS = "vowels"
_STR_PHONEME = "phoneme"
_STR_KEYS = "keys"

_STR_CONSONANTS = "consonants"
_STR_KEYS_LEFT = "keys_left"
_STR_KEYS_RIGHT = "keys_right"

_STR_PHONOLOGY = "phonology"
_STR_ALLOWED = "allowed"
_STR_IMMEDIATELY_BEFORE_VOWEL = "immediately_before_vowel"
_STR_PREV_AND_NEXT = "previous_and_next_sounds"
_STR_PREV = "prev"
_STR_NEXT = "next"

_STR_POSTPROCESSING = "postprocessing"
_STR_ENABLED = "enabled"
_STR_RULES = "rules"
_STR_KEEP_ORIGINAL = "keep_original_sequence"
_STR_DISALLOW_F_FOR_FINAL_S = "disallow_f_for_final_s_sound"
_STR_FOLD_STROKES = "fold_strokes"
_STR_STROKES_TO_FOLD = "strokes_to_fold"
_STR_KEYS_TO_FOLD_IN = "keys_to_fold_in"
_STR_FOLD_INTO = "fold_into"
_STR_VOWEL_DROPPING = "drop_vowels"
_STR_LEFT_CONSONANTS = "left_consonants"
_STR_RIGHT_CONSONANTS = "right_consonants"
_STR_VOWEL_CLUSTERS_TO_DROP = "vowel_clusters_to_drop"
_STR_ENABLED_FOR = "enabled_for"
_STR_SINGLE_STROKES = "single_strokes"
_STR_FIRST_STROKE = "first_stroke_of_sequence"
_STR_MIDDLE_STROKES = "middle_strokes_of_sequence"
_STR_LAST_STROKE = "last_stroke_of_sequence"
_STR_APPEND_DISAMBIGUATOR_STROKE = "append_disambiguator_stroke"
_STR_DISAMBIGUATOR_STROKE = "disambiguator_stroke"


class InvalidConfigError(Exception):
    """Error for when the config file is not as expected.

    This should be raised when an expected entry is missing or some value in
    it is not formatted how it should be.
    """


class Config:
    """Maintain the config settings for how to make strokes from words."""

    CONFIG_SCHEMA = schema.Schema(
        {
            _STR_VOWELS: [
                {
                    _STR_PHONEME: str,
                    _STR_KEYS: schema.Or([str], NO_STENO_MAPPING),
                }
            ],
            _STR_CONSONANTS: [
                {
                    _STR_PHONEME: str,
                    _STR_KEYS_LEFT: schema.Or([str], NO_STENO_MAPPING),
                    _STR_KEYS_RIGHT: schema.Or([str], NO_STENO_MAPPING),
                }
            ],
            _STR_PHONOLOGY: [
                {
                    _STR_ALLOWED: {
                        _STR_IMMEDIATELY_BEFORE_VOWEL: [str],
                        _STR_PREV_AND_NEXT: [
                            {
                                _STR_PREV: [str],
                                _STR_NEXT: [str],
                            }
                        ],
                    },
                }
            ],
            _STR_POSTPROCESSING: {
                _STR_DISALLOW_F_FOR_FINAL_S: {_STR_ENABLED: bool},
                _STR_FOLD_STROKES: {
                    _STR_ENABLED: bool,
                    _STR_RULES: [
                        {
                            _STR_ENABLED: bool,
                            _STR_KEEP_ORIGINAL: bool,
                            _STR_STROKES_TO_FOLD: [str],
                            _STR_KEYS_TO_FOLD_IN: str,
                            _STR_FOLD_INTO: schema.Or(_STR_NEXT_STROKE, _STR_PREVIOUS_STROKE),
                        }
                    ],
                },
                _STR_VOWEL_DROPPING: {
                    _STR_ENABLED: bool,
                    _STR_RULES: [
                        {
                            _STR_ENABLED: bool,
                            _STR_KEEP_ORIGINAL: bool,
                            _STR_LEFT_CONSONANTS: schema.Or(
                                str,
                                schema.Or(_STR_ANY_SET_OF_KEYS, _STR_ANY_NON_EMPTY_SET_OF_KEYS),
                            ),
                            _STR_RIGHT_CONSONANTS: schema.Or(
                                str,
                                schema.Or(_STR_ANY_SET_OF_KEYS, _STR_ANY_NON_EMPTY_SET_OF_KEYS),
                            ),
                            _STR_VOWEL_CLUSTERS_TO_DROP: [str],
                            _STR_ENABLED_FOR: {
                                _STR_SINGLE_STROKES: bool,
                                _STR_FIRST_STROKE: bool,
                                _STR_MIDDLE_STROKES: bool,
                                _STR_LAST_STROKE: bool,
                            },
                        }
                    ],
                },
                _STR_APPEND_DISAMBIGUATOR_STROKE: {
                    _STR_ENABLED: bool,
                    _STR_DISAMBIGUATOR_STROKE: str,
                },
            },
        }
    )

    def __init__(self, config_file):
        self._log = logging.getLogger("dictionary_generator")
        self._vowel_to_possible_strokes = {}
        self._left_consonant_to_possible_strokes = {}
        self._right_consonant_to_possible_strokes = {}
        self._allowed_first_consonants = []
        self._consonants_allowed_after = {}
        self._postprocessing_settings = {}

        try:
            with open(config_file, "r", encoding="UTF-8") as file:
                self._config = yaml.safe_load(file)
                Config.CONFIG_SCHEMA.validate(self._config)
        except yaml.YAMLError as err:
            raise InvalidConfigError(f"Invalid YAML in {config_file}: {err}") from err
        except schema.SchemaError as err:
            raise InvalidConfigError(
                f"{config_file} does not conform to the schema: {err}"
            ) from err

        self._process_config()

    def _process_config(self):
        self._process_vowels_mapping()
        self._process_consonants_mapping()
        self._process_phonology_rules()
        self._process_postprocessing_settings()

    def _process_vowels_mapping(self):
        self._vowel_to_possible_strokes = self._process_phoneme_mapping(_STR_VOWELS, _STR_KEYS)

    def _process_consonants_mapping(self):
        self._left_consonant_to_possible_strokes = self._process_phoneme_mapping(
            _STR_CONSONANTS, _STR_KEYS_LEFT
        )
        self._right_consonant_to_possible_strokes = self._process_phoneme_mapping(
            _STR_CONSONANTS, _STR_KEYS_RIGHT
        )

    def _process_phonology_rules(self):
        """Extract the phonology rules from the config.

        This should only be called after _process_consonants_mapping() has
        already finished.

        This sets self._allowed_first_consonants to a list of all phonemes that
        are allowed immediately before a vowel. Each phoneme should be
        represented as a string giving the pronunciation in IPA.

        It also sets self._consonants_allowed_after to a dictionary specifying
        which consonant phonemes can follow a given consonant phoneme. The key
        is a phoneme, and the value is a list of phonemes that can follow it.
        Each phoneme should be a string giving the pronunciation in IPA.

        Raises:
            InvalidConfigError: If any phoneme specified in the rules is not
            specified in the `consonants` section of the config.
        """

        self._allowed_first_consonants = []
        self._consonants_allowed_after = {}

        phonology_section = self._config[_STR_PHONOLOGY]

        for item in phonology_section:
            rules = item[_STR_ALLOWED]

            allowed_first = rules[_STR_IMMEDIATELY_BEFORE_VOWEL]
            for consonant in allowed_first:
                if consonant not in self._left_consonant_to_possible_strokes:
                    raise InvalidConfigError(
                        f"Element {consonant} is in `phonology` but not in `consonants`"
                    )

            self._allowed_first_consonants += allowed_first

            for prev_and_next in rules[_STR_PREV_AND_NEXT]:
                prev_consonant_list = prev_and_next[_STR_PREV]
                next_consonant_list = prev_and_next[_STR_NEXT]

                for consonant in prev_consonant_list + next_consonant_list:
                    if consonant not in self._left_consonant_to_possible_strokes:
                        raise InvalidConfigError(
                            f"Element {consonant} is in `phonology` but not in `consonants`"
                        )

                for prev_consonant in prev_consonant_list:
                    old_or_empty = self._consonants_allowed_after.get(prev_consonant, [])
                    new_value = old_or_empty + next_consonant_list
                    self._consonants_allowed_after[prev_consonant] = new_value

    def _process_postprocessing_settings(self):
        self._postprocessing_settings = self._config[_STR_POSTPROCESSING]

    def _process_phoneme_mapping(self, phonemes_category, keys_list_name):
        """Extract phonemes and possible strokes to steno them from a section.

        Args:
            phonemes_category: A string specifying which section of the config
                file to process.
            keys_list_name: A string specifying the key in the config file
                where the value is a list of strings specifying all the
                possible strokes to make the corresponding phoneme.
        """

        phoneme_to_possible_strokes = {}
        phonemes_section = self._config[phonemes_category]

        for entry in phonemes_section:
            phoneme = entry[_STR_PHONEME]
            strokes_as_strings = entry[keys_list_name]

            if strokes_as_strings == NO_STENO_MAPPING:
                self._log.debug(
                    "No mapping for phoneme `%s` in %s in %s",
                    phoneme,
                    phonemes_category,
                    keys_list_name,
                )
                phoneme_to_possible_strokes[phoneme] = []
                continue

            strokes = []
            for stroke_string in strokes_as_strings:
                self._log.debug(
                    "got stroke `%s` for `%s` in `%s`", stroke_string, phoneme, phonemes_category
                )
                strokes.append(steno.Stroke.from_string(stroke_string))

            phoneme_to_possible_strokes[phoneme] = strokes

        return phoneme_to_possible_strokes

    def get_vowels(self):
        """Return the vowels specified in the config.

        Returns:
            List of strings. Each is a IPA representation of a vowel sound.
        """

        return self._vowel_to_possible_strokes.keys()

    def get_consonants(self):
        """Return the consonants specified in the config.

        Returns:
            List of strings. Each is a IPA representation of a consonant sound.
        """

        return self._left_consonant_to_possible_strokes.keys()

    def possible_strokes_for_left_consonant(self, phoneme):
        """Return how to stroke a certain consonant with left consonants.

        Returns:
            List of Strokes. Each stroke is a way to acheive the given phoneme.
        """

        return self._left_consonant_to_possible_strokes.get(phoneme, [])

    def possible_strokes_for_vowel(self, phoneme):
        """Return how to stroke a certain vowel.

        Returns:
            List of Strokes. Each stroke is a way to acheive the given phoneme.
        """

        return self._vowel_to_possible_strokes.get(phoneme, [])

    def possible_strokes_for_right_consonant(self, phoneme):
        """Return how to stroke a certain consonant with right consonant.

        Returns:
            List of Strokes. Each stroke is a way to acheive the given phoneme.
        """

        return self._right_consonant_to_possible_strokes.get(phoneme, [])

    def can_prepend_to_onset(self, phoneme, following_phoneme):
        """Determine if combining the phonemes conforms to the phonology rules.

        Returns:
            True if `phoneme + following_phoneme` conforms to the specified
            phonology rules.
        """

        if phoneme not in self._left_consonant_to_possible_strokes:
            self._log.error("Unknown consonant phoneme `%s`", phoneme)
            return False

        if following_phoneme is None:
            # This phoneme would be the one right before the vowel.
            return phoneme in self._allowed_first_consonants

        return following_phoneme in self._consonants_allowed_after.get(phoneme, [])

    def should_disallow_f_for_final_s_sound(self):
        """Return True if this postprocessing setting is enabled."""

        return self._postprocessing_settings[_STR_DISALLOW_F_FOR_FINAL_S][_STR_ENABLED]

    def postprocess_stroke_sequence(self, stroke_sequence):
        """Update a StrokeSequence using rules from the config.

        Args:
            stroke_sequence: The StrokeSequence to run postprocessing on.

        Returns:
            A list of StrokeSequences.
        """

        new_stroke_sequences = [stroke_sequence]

        new_lst = []
        for sequence in new_stroke_sequences:
            new_lst += self._run_stroke_folding_rules(sequence)
        new_stroke_sequences = new_lst

        new_lst = []
        for sequence in new_stroke_sequences:
            new_lst += self._run_vowel_dropping_rules(sequence)
        new_stroke_sequences = new_lst

        return new_stroke_sequences

    def _run_stroke_folding_rules(self, stroke_sequence):
        """Perform stroke folding postprocessing.

        Args:
            stroke_sequence: The StrokeSequence to apply the folding rules to.

        Raises:
            InvalidConfigError: If the the specified stroke to fold into is not
                _STR_NEXT_STROKE or _STR_PREVIOUS_STROKE
            OutOfStenoOrderError: If the keys specified to fold into an adjacent
                stroke are out of steno order.
            MissingDashInStrokeError: If the keys specified to fold into an
                adjacent stroke have no middle keys (vowels, a star, or dash).

        Returns:
            A list of StrokeSequences.
        """
        new_stroke_sequences = [stroke_sequence]
        fold_strokes = self._config.get(_STR_POSTPROCESSING, {}).get(_STR_FOLD_STROKES, {})

        if not fold_strokes.get(_STR_ENABLED, False):
            return new_stroke_sequences

        list_of_stroke_lists = [copy.deepcopy(stroke_sequence.get_strokes())]

        for rule in fold_strokes.get(_STR_RULES, []):
            if not rule[_STR_ENABLED]:
                continue

            length = len(list_of_stroke_lists)  # We may append to the list.
            for i in range(length):
                strokes = copy.deepcopy(list_of_stroke_lists[i])
                made_changes = False

                new_strokes = copy.deepcopy(strokes)
                for k, stroke in enumerate(strokes):
                    if not Config._stroke_folding_enabled_for_stroke(
                        strokes, k, rule[_STR_FOLD_INTO]
                    ):
                        continue

                    if Config._stroke_folding_rule_applies(rule, stroke):
                        fold_into = rule[_STR_FOLD_INTO]
                        if fold_into == _STR_NEXT_STROKE:
                            new_strokes[k + 1].add_keys_ignore_steno_order(
                                steno.Stroke.from_string(rule[_STR_KEYS_TO_FOLD_IN]).get_keys()
                            )
                        elif fold_into == _STR_PREVIOUS_STROKE:
                            new_strokes[k - 1].add_keys_ignore_steno_order(
                                steno.Stroke.from_string(rule[_STR_KEYS_TO_FOLD_IN]).get_keys()
                            )
                        else:
                            raise InvalidConfigError("Unknown fold_into value `{fold_into}`")

                        new_strokes = new_strokes[:k] + new_strokes[k + 1 :]
                        made_changes = True

                if made_changes:
                    if rule[_STR_KEEP_ORIGINAL]:
                        list_of_stroke_lists.append(new_strokes)
                    else:
                        list_of_stroke_lists[i] = new_strokes

        new_stroke_sequences = []
        for strokes in list_of_stroke_lists:
            new_stroke_sequences.append(steno.StrokeSequence(strokes))

        return new_stroke_sequences

    def _run_vowel_dropping_rules(self, stroke_sequence):
        """Perform vowel-dropping postprocessing.

        Args:
            stroke_sequence: The StrokeSequence to apply the vowel-dropping
            rules to.

        Raises:
            OutOfStenoOrderError: If the keys specified in the rule as vowel
                clusters to drop are out of steno order.
            MissingDashInStrokeError: If the keys specified in the rule as vowel
                clusters to drop have no middle keys (vowels, a star, or dash).
                This should never occur because the keys in the vowel cluster
                should be vowels.

        Returns:
            A list of StrokeSequences.
        """

        new_stroke_sequences = [stroke_sequence]
        vowel_dropping = self._config.get(_STR_POSTPROCESSING, {}).get(_STR_VOWEL_DROPPING, {})

        if not vowel_dropping.get(_STR_ENABLED, False):
            return new_stroke_sequences

        list_of_stroke_lists = [copy.deepcopy(stroke_sequence.get_strokes())]

        for rule in vowel_dropping.get(_STR_RULES, []):
            if not rule[_STR_ENABLED]:
                continue

            length = len(list_of_stroke_lists)  # We may append to the list.
            for i in range(length):
                strokes = copy.deepcopy(list_of_stroke_lists[i])
                made_changes = False

                for k, stroke in enumerate(strokes):
                    if not Config._vowel_dropping_enabled_for_stroke(
                        strokes, k, rule[_STR_ENABLED_FOR]
                    ):
                        continue

                    if Config._vowel_dropping_rule_applies(rule, stroke):
                        stroke.clear_all_vowels()
                        made_changes = True

                if made_changes:
                    if rule[_STR_KEEP_ORIGINAL]:
                        list_of_stroke_lists.append(strokes)
                    else:
                        list_of_stroke_lists[i] = strokes

        new_stroke_sequences = []
        for strokes in list_of_stroke_lists:
            new_stroke_sequences.append(steno.StrokeSequence(strokes))

        return new_stroke_sequences

    @staticmethod
    def _stroke_folding_enabled_for_stroke(strokes, index, fold_into):
        if fold_into == _STR_NEXT_STROKE:
            return index < len(strokes) - 1

        if fold_into == _STR_PREVIOUS_STROKE:
            return index > 0

        raise InvalidConfigError("Unknown fold_into value `{fold_into}`")

    @staticmethod
    def _vowel_dropping_enabled_for_stroke(strokes, index, enabled_for):
        if index < 0 or index >= len(strokes):
            return False

        if len(strokes) == 1:
            return enabled_for[_STR_SINGLE_STROKES] and index == 0

        if index == 0:
            return enabled_for[_STR_FIRST_STROKE]

        if index == len(strokes) - 1:
            return enabled_for[_STR_LAST_STROKE]

        return enabled_for[_STR_MIDDLE_STROKES]

    @staticmethod
    def _stroke_folding_rule_applies(rule, stroke):
        """Check if the stroke-folding rule applies to this stroke.

        This function does not check if the rule is enabled.

        Args:
            rule: A dictionary specifying the stroke-folding rule.
            stroke: The stroke that this rule would be applied to.

        Raises:
            OutOfStenoOrderError: If the keys specified in the rule as strokes
                to fold are out of steno order.
            MissingDashInStrokeError: If the keys specified in the rule as
                strokes to fold have not middle keys (vowels, a star, or dash).

        Return:
            True if the stroke matches one of the strokes specified in the rule
            as a stroke to fold into an adjacent stroke.
        """

        for stroke_string in rule[_STR_STROKES_TO_FOLD]:
            if stroke == steno.Stroke.from_string(stroke_string):
                return True

        return False

    @staticmethod
    def _vowel_dropping_rule_applies(rule, stroke):
        """Check if the vowel dropping rule applies to this stroke.

        This function does not check if the rule is enabled.

        Args:
            rule: A dictionary specifying the vowel dropping rule.
            stroke: The stroke that this rule would be applied to.

        Raises:
            OutOfStenoOrderError: If the keys specified in the rule as vowel
                clusters to drop are out of steno order.
            MissingDashInStrokeError: If the keys specified in the rule as vowel
                clusters to drop have no middle keys (vowels, a star, or dash).
                This should never occur because the keys in the vowel cluster
                should be vowels.

        Return:
            True if the stroke contains one of the vowel clusters specified in
            the rule.
        """

        # Check the left consonants condition.
        left_consonants_rule = rule[_STR_LEFT_CONSONANTS]
        if left_consonants_rule == _STR_ANY_SET_OF_KEYS:
            # Do nothing.
            pass
        elif left_consonants_rule == _STR_ANY_NON_EMPTY_SET_OF_KEYS:
            if not stroke.has_left_consonant():
                return False
        elif not stroke.left_consonants_match(steno.Stroke.from_string(left_consonants_rule)):
            return False

        # Check the right consonants condition.
        right_consonants_rule = rule[_STR_RIGHT_CONSONANTS]
        if right_consonants_rule == _STR_ANY_SET_OF_KEYS:
            # Do nothing.
            pass
        elif right_consonants_rule == _STR_ANY_NON_EMPTY_SET_OF_KEYS:
            if not stroke.has_right_consonant():
                return False
        elif not stroke.right_consonants_match(steno.Stroke.from_string(right_consonants_rule)):
            return False

        # Check if the vowels are in one of the specified clusters.
        for vowel_cluster in rule[_STR_VOWEL_CLUSTERS_TO_DROP]:
            if stroke.vowels_match(steno.Stroke.from_string(vowel_cluster)):
                return True

        return False

    def should_append_disambiguator_stroke(self):
        """Return True if this postprocessing setting is enabled."""

        return self._postprocessing_settings[_STR_APPEND_DISAMBIGUATOR_STROKE][_STR_ENABLED]

    def get_disambiguator_stroke(self):
        """Return the disambiguator stroke specified in postprocessing settings.

        This should only be needed when should_append_disambiguator_stroke()
        returns True.

        Returns:
            None if should_append_disambiguator_stroke() returns False,
            otherwise it returns a Stroke that should be appended to a
            StrokeSequence if that StrokeSequence collided with another for a
            different word.
        """

        if not self.should_append_disambiguator_stroke():
            return None

        return steno.Stroke.from_string(
            self._postprocessing_settings[_STR_APPEND_DISAMBIGUATOR_STROKE][
                _STR_DISAMBIGUATOR_STROKE
            ]
        )
