import copy
import pytest

from steno_tools.generator.steno import Key, Stroke, StrokeSequence
from steno_tools.generator.steno import MissingDashInStrokeError, OutOfStenoOrderError


#####################################################################
# Test Stroke class
#####################################################################


class TestStroke:
    #################################################################
    # Test __init__()
    #################################################################

    def test_init_empty(self):
        stroke = Stroke()

        assert stroke.get_keys() == []

    def test_init_empty_list(self):
        stroke = Stroke([])

        assert stroke.get_keys() == []

    def test_init_only_star(self):
        keys = [Key.STAR]
        stroke = Stroke(keys)

        assert stroke.get_keys() == keys

    def test_init_only_num(self):
        keys = [Key.NUM]
        stroke = Stroke(keys)

        assert stroke.get_keys() == keys

    def test_init_multiple_keys(self):
        keys = [Key.LS, Key.LW, Key.A, Key.STAR, Key.RL]
        stroke = Stroke(keys)

        assert stroke.get_keys() == keys

    def test_init_star_out_of_order(self):
        keys = [Key.LS, Key.STAR, Key.LW, Key.A, Key.RL]
        stroke = Stroke(keys)

        assert stroke.get_keys() == [Key.LS, Key.LW, Key.A, Key.STAR, Key.RL]

    def test_init_keys_out_of_order(self):
        with pytest.raises(OutOfStenoOrderError):
            Stroke([Key.A, Key.LW])

    #################################################################
    # Test __eq__()
    #################################################################

    def test_stroke_equality_when_equal(self):
        keys = [Key.A, Key.RT]
        stroke1 = Stroke(keys)
        stroke2 = Stroke(keys)
        assert stroke1 == stroke2

    def test_stroke_equality_when_not_equal(self):
        keys1 = [Key.A, Key.RT]
        keys2 = [Key.A, Key.RD]
        stroke1 = Stroke(keys1)
        stroke2 = Stroke(keys2)
        assert stroke1 != stroke2

    def test_stroke_equality_when_different_key_combination(self):
        keys1 = [Key.A, Key.RT]
        keys2 = [Key.A, Key.RT, Key.RD]
        stroke1 = Stroke(keys1)
        stroke2 = Stroke(keys2)
        assert stroke1 != stroke2

    def test_stroke_equality_when_one_is_starred(self):
        keys1 = [Key.A, Key.RT]
        keys2 = [Key.A, Key.STAR, Key.RT]
        stroke1 = Stroke(keys1)
        stroke2 = Stroke(keys2)
        assert stroke1 != stroke2

    def test_stroke_equality_when_one_is_none(self):
        stroke1 = Stroke([Key.A, Key.RT])
        stroke2 = None
        assert stroke1 != stroke2

    def test_stroke_equality_when_both_are_none(self):
        stroke1 = None
        stroke2 = None
        assert stroke1 == stroke2

    #################################################################
    # Test __lt__()
    #################################################################

    def test_lt_operator_false_when_equal(self):
        stroke1 = Stroke([Key.LK, Key.O, Key.RD])
        stroke2 = Stroke([Key.LK, Key.O, Key.RD])

        assert not (stroke1 < stroke2)
        assert not (stroke2 < stroke1)
        assert stroke1 == stroke2

    def test_lt_operator_unstarred_is_less(self):
        stroke1 = Stroke([Key.LK, Key.O, Key.RD])
        stroke2 = Stroke([Key.LK, Key.O, Key.STAR, Key.RD])

        assert stroke1 < stroke2
        assert not (stroke2 < stroke1)

    def test_lt_operator_star_is_tiebreaker(self):
        stroke1 = Stroke([Key.LK, Key.RP])
        stroke2 = Stroke([Key.LK, Key.STAR, Key.RP])
        stroke3 = Stroke([Key.LK, Key.RG])
        stroke4 = Stroke([Key.LK, Key.STAR, Key.RZ])

        assert stroke1 < stroke2
        assert not (stroke2 < stroke1)

        assert stroke2 < stroke3
        assert not (stroke3 < stroke2)

        assert stroke3 < stroke4
        assert not (stroke4 < stroke3)

    def test_lt_operator_shorter_is_less(self):
        stroke1 = Stroke([Key.LK, Key.O, Key.RD])
        stroke2 = Stroke([Key.LK, Key.O, Key.RD, Key.RZ])

        assert stroke1 < stroke2
        assert not (stroke2 < stroke1)

    def test_lt_operator_same_prefix(self):
        stroke1 = Stroke([Key.LK, Key.O, Key.RF, Key.RR, Key.RB])
        stroke2 = Stroke([Key.LK, Key.O, Key.RD])

        assert stroke1 < stroke2
        assert not (stroke2 < stroke1)

    def test_lt_operator_different_start(self):
        stroke1 = Stroke([Key.LK, Key.O, Key.RD])
        stroke2 = Stroke([Key.LP, Key.A, Key.RT])

        assert stroke1 < stroke2
        assert not (stroke2 < stroke1)

    #################################################################
    # Test __str__()
    #################################################################

    def test_str_empty(self):
        stroke = Stroke([])
        assert str(stroke) == "-"

    def test_str_only_left_consonants(self):
        stroke = Stroke([Key.LT, Key.LK])
        assert str(stroke) == "TK-"

    def test_str_only_left_consonants_and_star(self):
        stroke = Stroke([Key.LT, Key.LK, Key.STAR])
        assert str(stroke) == "TK*"

    def test_str_only_right_consonants(self):
        stroke = Stroke([Key.RP, Key.RL])
        assert str(stroke) == "-PL"

    def test_str_only_right_consonants_and_star(self):
        stroke = Stroke([Key.STAR, Key.RP, Key.RL])
        assert str(stroke) == "*PL"

    def test_str_both_consonants(self):
        stroke = Stroke([Key.LK, Key.RP, Key.RL])
        assert str(stroke) == "K-PL"

    def test_str_both_consonants_and_star(self):
        stroke = Stroke([Key.LK, Key.STAR, Key.RP, Key.RL])
        assert str(stroke) == "K*PL"

    def test_str_has_vowel(self):
        stroke = Stroke([Key.A, Key.O])
        assert str(stroke) == "AO"

    def test_str_only_star(self):
        stroke = Stroke([Key.STAR])
        assert str(stroke) == "*"

    def test_str_has_vowels_and_star(self):
        stroke = Stroke([Key.A, Key.O, Key.STAR, Key.U])
        assert str(stroke) == "AO*U"

    def test_str_complex_no_star(self):
        stroke = Stroke([Key.LS, Key.LT, Key.O, Key.RP])
        assert str(stroke) == "STOP"

    def test_str_complex_with_star(self):
        stroke = Stroke([Key.LS, Key.LT, Key.O, Key.STAR, Key.RP])
        assert str(stroke) == "STO*P"

    #################################################################
    # Test from_string()
    #################################################################

    def test_from_string_empty(self):
        with pytest.raises(MissingDashInStrokeError):
            Stroke.from_string("")

    def test_from_string_just_dash(self):
        stroke = Stroke.from_string("-")
        expected = Stroke([])

        assert stroke == expected

    def test_from_string_only_left_consonants(self):
        stroke = Stroke.from_string("SR-")
        expected = Stroke([Key.LS, Key.LR])

        assert stroke == expected

    def test_from_string_left_consonants_with_star(self):
        stroke = Stroke.from_string("SR*")
        expected = Stroke([Key.LS, Key.LR, Key.STAR])

        assert stroke == expected

    def test_from_string_only_right_consonants(self):
        stroke = Stroke.from_string("-FB")
        expected = Stroke([Key.RF, Key.RB])

        assert stroke == expected

    def test_from_string_right_consonants_with_star(self):
        stroke = Stroke.from_string("*FB")
        expected = Stroke([Key.RF, Key.RB, Key.STAR])

        assert stroke == expected

    def test_from_string_both_consonants(self):
        stroke = Stroke.from_string("SR-FB")
        expected = Stroke([Key.LS, Key.LR, Key.RF, Key.RB])

        assert stroke == expected

    def test_from_string_both_consonants_with_star(self):
        stroke = Stroke.from_string("SR*FB")
        expected = Stroke([Key.LS, Key.LR, Key.STAR, Key.RF, Key.RB])

        assert stroke == expected

    def test_from_string_only_vowels(self):
        stroke = Stroke.from_string("AU")
        expected = Stroke([Key.A, Key.U])

        assert stroke == expected

    def test_from_string_vowels_with_star(self):
        stroke = Stroke.from_string("A*U")
        expected = Stroke([Key.A, Key.STAR, Key.U])

        assert stroke == expected

    def test_from_string_all_regions(self):
        stroke = Stroke.from_string("TPUPB")
        expected = Stroke([Key.LT, Key.LP, Key.U, Key.RP, Key.RB])

        assert stroke == expected

    def test_from_string_all_regions_with_star(self):
        stroke = Stroke.from_string("TP*UPB")
        expected = Stroke([Key.LT, Key.LP, Key.STAR, Key.U, Key.RP, Key.RB])

        assert stroke == expected

    def test_from_string_out_of_steno_order(self):
        with pytest.raises(OutOfStenoOrderError):
            Stroke.from_string("HS-")

    def test_from_string_star_out_of_steno_order(self):
        with pytest.raises(OutOfStenoOrderError):
            stroke = Stroke.from_string("K*W")
            print(f"s: {str(s)}")

    def test_from_string_missing_only_left_consonants_missing_dash(self):
        with pytest.raises(MissingDashInStrokeError):
            Stroke.from_string("WH")

    def test_from_string_missing_only_right_consonants_missing_dash(self):
        with pytest.raises(MissingDashInStrokeError):
            Stroke.from_string("FG")

    def test_from_string_missing_both_consonants_missing_dash(self):
        with pytest.raises(MissingDashInStrokeError):
            Stroke.from_string("WHFG")

    #################################################################
    # Test add_keys_maintain_steno_order()
    #################################################################

    def test_add_keys_maintain_order_empty_stroke(self):
        stroke = Stroke()
        keys = [Key.LS, Key.LT, Key.A]

        stroke.add_keys_maintain_steno_order(keys)

        assert stroke.get_keys() == keys

    def test_add_keys_maintain_order_non_empty_stroke(self):
        stroke = Stroke([Key.LS, Key.LT])
        keys = [Key.A, Key.E]

        stroke.add_keys_maintain_steno_order(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.A, Key.E]

    def test_add_keys_maintain_order_added_keys_out_of_order(self):
        stroke = Stroke([Key.LS, Key.LT])
        keys = [Key.RG, Key.RR]

        with pytest.raises(OutOfStenoOrderError):
            stroke.add_keys_maintain_steno_order(keys)

    def test_add_keys_maintain_order_appending_is_out_of_order(self):
        stroke = Stroke([Key.LS, Key.A])
        keys = [Key.LH, Key.RR]

        with pytest.raises(OutOfStenoOrderError):
            stroke.add_keys_maintain_steno_order(keys)

    def test_add_keys_maintain_order_duplicate_key(self):
        stroke = Stroke([Key.LS, Key.LT])
        keys = [Key.LT, Key.A]

        stroke.add_keys_maintain_steno_order(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.A]

    def test_add_keys_maintain_order_star_anywhere(self):
        stroke = Stroke([Key.LS, Key.LT, Key.RG])
        keys = [Key.STAR]

        stroke.add_keys_maintain_steno_order(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.STAR, Key.RG]

    #################################################################
    # Test add_keys_ignore_steno_order()
    #################################################################

    def test_add_keys_ignore_order_empty_stroke(self):
        stroke = Stroke()
        keys = [Key.LS, Key.LT, Key.A]

        stroke.add_keys_ignore_steno_order(keys)

        assert stroke.get_keys() == keys

    def test_add_keys_ignore_order_non_empty_stroke(self):
        stroke = Stroke([Key.LS, Key.LT])
        keys = [Key.A, Key.E]

        stroke.add_keys_ignore_steno_order(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.A, Key.E]

    def test_add_keys_ignore_order_added_keys_out_of_order(self):
        stroke = Stroke([Key.LS, Key.LT])
        keys = [Key.RG, Key.RR]

        stroke.add_keys_ignore_steno_order(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.RR, Key.RG]

    def test_add_keys_ignore_order_appending_is_out_of_order(self):
        stroke = Stroke([Key.LS, Key.A])
        keys = [Key.LH, Key.RR]

        stroke.add_keys_ignore_steno_order(keys)

        assert stroke.get_keys() == [Key.LS, Key.LH, Key.A, Key.RR]

    def test_add_keys_ignore_order_duplicate_key(self):
        stroke = Stroke([Key.LS, Key.LT])
        keys = [Key.LT, Key.A]

        stroke.add_keys_ignore_steno_order(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.A]

    def test_add_keys_ignore_order_star_anywhere(self):
        stroke = Stroke([Key.LS, Key.LT, Key.RG])
        keys = [Key.STAR]

        stroke.add_keys_ignore_steno_order(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.STAR, Key.RG]

    #################################################################
    # Test clear_keys()
    #################################################################

    def test_clear_keys_empty_stroke(self):
        stroke = Stroke()
        keys = [Key.LS, Key.LT, Key.A]

        stroke.clear_keys(keys)

        assert stroke.get_keys() == []

    def test_clear_keys_non_empty_stroke(self):
        stroke = Stroke([Key.LS, Key.LT, Key.A])
        keys = [Key.LT, Key.A]

        stroke.clear_keys(keys)

        assert stroke.get_keys() == [Key.LS]

    def test_clear_keys_no_matching_keys(self):
        stroke = Stroke([Key.LS, Key.LT, Key.A])
        keys = [Key.RF, Key.RR]

        stroke.clear_keys(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.A]

    def test_clear_keys_star_key(self):
        stroke = Stroke([Key.LS, Key.LT, Key.STAR])
        keys = [Key.STAR]

        stroke.clear_keys(keys)

        assert stroke.get_keys() == [Key.LS, Key.LT]

    #################################################################
    # Test clear_vowels()
    #################################################################

    def test_clear_all_vowels_empty_stroke(self):
        stroke = Stroke()
        stroke.clear_all_vowels()

        assert stroke.get_keys() == []

    def test_clear_all_vowels_non_empty_stroke(self):
        stroke = Stroke([Key.LS, Key.LT, Key.A, Key.E, Key.RP])
        stroke.clear_all_vowels()

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.RP]

    def test_clear_all_vowels_no_vowels(self):
        stroke = Stroke([Key.LS, Key.LT, Key.STAR, Key.RP])
        stroke.clear_all_vowels()

        assert stroke.get_keys() == [Key.LS, Key.LT, Key.STAR, Key.RP]

    #################################################################
    # Test get_vowels()
    #################################################################

    def test_get_vowels_empty_stroke(self):
        stroke = Stroke()

        assert stroke.get_vowels() == []

    def test_get_vowels_non_empty_stroke(self):
        stroke = Stroke([Key.LS, Key.LT, Key.A, Key.E, Key.RP])

        assert stroke.get_vowels() == [Key.A, Key.E]

    def test_get_vowels_no_vowels(self):
        stroke = Stroke([Key.LS, Key.LT, Key.STAR, Key.RP])

        assert stroke.get_vowels() == []

    #################################################################
    # Test get_last_key()
    #################################################################

    def test_get_last_key_empty_stroke(self):
        stroke = Stroke()

        assert stroke.get_last_key() is None

    def test_get_last_key_only_star(self):
        stroke = Stroke([Key.STAR])

        assert stroke.get_last_key() is None

    def test_get_last_key_only_num(self):
        stroke = Stroke([Key.NUM])

        assert stroke.get_last_key() is None

    def test_get_last_key_with_valid_last_key(self):
        stroke = Stroke([Key.LH, Key.A, Key.RT])

        assert stroke.get_last_key() == Key.RT

    def test_get_last_key_star_does_not_count(self):
        stroke = Stroke([Key.LH, Key.A, Key.STAR])

        assert stroke.get_last_key() == Key.A

    #################################################################
    # Test get_keys()
    #################################################################

    def test_get_keys_empty_stroke(self):
        stroke = Stroke()

        assert stroke.get_keys() == []

    def test_get_keys_no_star(self):
        keys = [Key.LS, Key.LH, Key.E, Key.RL, Key.RD]
        stroke = Stroke(keys)

        assert stroke.get_keys() == keys

    def test_get_keys_with_star(self):
        keys = [Key.LS, Key.LH, Key.STAR, Key.E, Key.RL, Key.RD]
        stroke = Stroke(keys)

        assert stroke.get_keys() == keys

    #################################################################
    # Test is_empty()
    #################################################################

    def test_is_empty_true_when_empty(self):
        stroke = Stroke()

        assert stroke.is_empty()

    def test_is_empty_false_when_not_empty(self):
        stroke = Stroke([Key.LS, Key.LH, Key.E, Key.RL, Key.RD])

        assert not stroke.is_empty()

    def test_is_empty_false_when_only_star(self):
        stroke = Stroke([Key.STAR])

        assert not stroke.is_empty()

    def test_is_empty_false_when_only_num(self):
        stroke = Stroke([Key.NUM])

        assert not stroke.is_empty()

    #################################################################
    # Test has_left_consonant()
    #################################################################

    def test_is_empty_false_when_empty(self):
        stroke = Stroke()

        assert not stroke.has_left_consonant()

    def test_is_empty_false_when_no_left_consonants(self):
        stroke = Stroke([Key.A, Key.RR, Key.RL, Key.RD])

        assert not stroke.has_left_consonant()

    def test_is_empty_true_when_one_left_consonant(self):
        stroke = Stroke([Key.LR, Key.A, Key.RR, Key.RL, Key.RD])

        assert stroke.has_left_consonant()

    def test_is_empty_true_when_multiple_left_consonants(self):
        stroke = Stroke([Key.LK, Key.LW, Key.LH, Key.A, Key.RR, Key.RL, Key.RD])

        assert stroke.has_left_consonant()

    #################################################################
    # Test has_right_consonant()
    #################################################################

    def test_is_empty_false_when_empty(self):
        stroke = Stroke()

        assert not stroke.has_right_consonant()

    def test_is_empty_false_when_no_right_consonants(self):
        stroke = Stroke([Key.LW, Key.LH, Key.A])

        assert not stroke.has_right_consonant()

    def test_is_empty_true_when_one_right_consonant(self):
        stroke = Stroke([Key.LW, Key.LH, Key.A, Key.RF])

        assert stroke.has_right_consonant()

    def test_is_empty_true_when_multiple_right_consonants(self):
        stroke = Stroke([Key.LW, Key.A, Key.RR, Key.RL, Key.RD])

        assert stroke.has_right_consonant()

    #################################################################
    # Test left_consonants_match()
    #################################################################

    def test_left_consonants_match_true_when_both_empty(self):
        stroke1 = Stroke()
        stroke2 = Stroke()

        assert stroke1.left_consonants_match(stroke2)

    def test_left_consonants_match_true_when_both_no_left_consonants(self):
        stroke1 = Stroke([Key.A, Key.RF])
        stroke2 = Stroke([Key.O, Key.STAR, Key.RL])

        assert stroke1.left_consonants_match(stroke2)

    def test_left_consonants_match_false_when_only_partial_match(self):
        stroke1 = Stroke([Key.LW, Key.LH, Key.A, Key.RF])
        stroke2 = Stroke([Key.LP, Key.LH, Key.A, Key.RF])

        assert not stroke1.left_consonants_match(stroke2)

    def test_left_consonants_match_false_when_subset_match(self):
        stroke1 = Stroke([Key.LW, Key.LH, Key.A, Key.RF])
        stroke2 = Stroke([Key.LW, Key.LH, Key.LR, Key.A, Key.RF])

        assert not stroke1.left_consonants_match(stroke2)

    def test_left_consonants_match_true_when_full_match(self):
        stroke1 = Stroke([Key.LW, Key.LH, Key.A, Key.RR, Key.RD])
        stroke2 = Stroke([Key.LW, Key.LH, Key.O, Key.RG])

        assert stroke1.left_consonants_match(stroke2)

    #################################################################
    # Test vowels_match()
    #################################################################

    def test_vowels_match_true_when_both_empty(self):
        stroke1 = Stroke()
        stroke2 = Stroke()

        assert stroke1.vowels_match(stroke2)

    def test_vowels_match_true_when_both_no_vowels(self):
        stroke1 = Stroke([Key.LW, Key.LH])
        stroke2 = Stroke([Key.LS, Key.STAR, Key.RL])

        assert stroke1.vowels_match(stroke2)

    def test_vowels_match_false_when_only_partial_match(self):
        stroke1 = Stroke([Key.LH, Key.A, Key.O, Key.RF, Key.RG])
        stroke2 = Stroke([Key.LH, Key.A, Key.U, Key.RF, Key.RG])

        assert not stroke1.vowels_match(stroke2)

    def test_vowels_match_false_when_subset_match(self):
        stroke1 = Stroke([Key.A, Key.O, Key.RF, Key.RP])
        stroke2 = Stroke([Key.A, Key.O, Key.U, Key.RF, Key.RP])

        assert not stroke1.vowels_match(stroke2)

    def test_vowels_match_true_when_full_match(self):
        stroke1 = Stroke([Key.LW, Key.LH, Key.A, Key.E, Key.RL, Key.RD])
        stroke2 = Stroke([Key.LK, Key.A, Key.STAR, Key.E, Key.RD])

        assert stroke1.vowels_match(stroke2)

    #################################################################
    # Test right_consonants_match()
    #################################################################

    def test_right_consonants_match_true_when_both_empty(self):
        stroke1 = Stroke()
        stroke2 = Stroke()

        assert stroke1.right_consonants_match(stroke2)

    def test_right_consonants_match_true_when_both_no_right_consonants(self):
        stroke1 = Stroke([Key.LW, Key.A])
        stroke2 = Stroke([Key.LS, Key.O, Key.STAR, Key.U])

        assert stroke1.right_consonants_match(stroke2)

    def test_right_consonants_match_false_when_only_partial_match(self):
        stroke1 = Stroke([Key.LH, Key.A, Key.RF, Key.RG])
        stroke2 = Stroke([Key.LH, Key.A, Key.RF, Key.RL])

        assert not stroke1.right_consonants_match(stroke2)

    def test_right_consonants_match_false_when_subset_match(self):
        stroke1 = Stroke([Key.LW, Key.LH, Key.A, Key.RF, Key.RP])
        stroke2 = Stroke([Key.LW, Key.LH, Key.A, Key.RF, Key.RP, Key.RL])

        assert not stroke1.right_consonants_match(stroke2)

    def test_right_consonants_match_true_when_full_match(self):
        stroke1 = Stroke([Key.LW, Key.LH, Key.A, Key.RR, Key.RD])
        stroke2 = Stroke([Key.LK, Key.LR, Key.O, Key.STAR, Key.RR, Key.RD])

        assert stroke1.right_consonants_match(stroke2)


#####################################################################
# Test StrokeSequence class
#####################################################################


class TestStrokeSequence:
    #################################################################
    # Test __init__()
    #################################################################

    def test_init_empty(self):
        sequence = StrokeSequence()

        assert sequence.get_strokes() == []

    def test_init_empty_list(self):
        sequence = StrokeSequence([])

        assert sequence.get_strokes() == []

    def test_init_one_stroke(self):
        strokes = [Stroke([Key.A, Key.RT])]
        sequence = StrokeSequence(strokes)

        assert sequence.get_strokes() == strokes

    def test_init_multiple_strokes(self):
        strokes = [Stroke([Key.A, Key.RT]), Stroke([Key.LW, Key.STAR])]
        sequence = StrokeSequence(strokes)

        assert sequence.get_strokes() == strokes

    #################################################################
    # Test __eq__()
    #################################################################

    def test_equality_true_when_empty(self):
        sequence = StrokeSequence()

        assert sequence.get_strokes() == []

    def test_equality_true_when_same_strokes(self):
        strokes = [Stroke([Key.A, Key.RT]), Stroke([Key.LW, Key.STAR])]
        sequence1 = StrokeSequence(strokes)
        sequence2 = StrokeSequence(strokes)

        assert sequence1 == sequence2

    def test_equality_true_when_stroke_copies(self):
        strokes = [Stroke([Key.A, Key.RT]), Stroke([Key.LW, Key.STAR])]
        sequence1 = StrokeSequence(strokes)
        sequence2 = StrokeSequence(copy.deepcopy(strokes))

        assert sequence1 == sequence2

    def test_equality_false_when_different_strokes(self):
        strokes1 = [Stroke([Key.A, Key.RT]), Stroke([Key.LW, Key.STAR])]
        strokes2 = [Stroke([Key.A, Key.RT]), Stroke([Key.O, Key.RG, Key.RZ])]
        sequence1 = StrokeSequence(strokes1)
        sequence2 = StrokeSequence(strokes2)

        assert sequence1 != sequence2

    def test_equality_false_when_differs_by_star(self):
        strokes1 = [Stroke([Key.A, Key.RT])]
        strokes2 = [Stroke([Key.A, Key.STAR, Key.RT])]
        sequence1 = StrokeSequence(strokes1)
        sequence2 = StrokeSequence(strokes2)

        assert sequence1 != sequence2

    #################################################################
    # Test __str__()
    #################################################################

    def test_str_empty(self):
        sequence = StrokeSequence([Stroke()])

        assert str(sequence) == ""

    def test_init_one_stroke(self):
        sequence = StrokeSequence([Stroke([Key.A, Key.RG, Key.RZ])])

        assert str(sequence) == "AGZ"

    def test_init_multiple_strokes(self):
        sequence = StrokeSequence([Stroke([Key.A, Key.RT]), Stroke([Key.LW, Key.STAR])])

        assert str(sequence) == "AT/W*"

    def test_init_multiple_strokes_with_some_empty(self):
        strokes = [
            Stroke(),
            Stroke([Key.LW, Key.U, Key.RG]),
            Stroke([Key.STAR, Key.RB]),
            Stroke(),
            Stroke(),
            Stroke([Key.LH, Key.RP, Key.RZ]),
            Stroke(),
        ]
        sequence = StrokeSequence(strokes)

        assert str(sequence) == "WUG/*B/H-PZ"
