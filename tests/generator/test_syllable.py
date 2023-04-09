from syllable import Syllable, SyllableRegion, SyllableAtom


#####################################################################
# Test __init__()
#####################################################################


def test_init():
    syllable = Syllable(["k", "l"], "æ", ["p", "s"])
    assert len(syllable._atoms) == 5
    assert syllable._atoms[0] == SyllableAtom("k", SyllableRegion.ONSET)
    assert syllable._atoms[1] == SyllableAtom("l", SyllableRegion.ONSET)
    assert syllable._atoms[2] == SyllableAtom("æ", SyllableRegion.NUCLEUS)
    assert syllable._atoms[3] == SyllableAtom("p", SyllableRegion.CODA)
    assert syllable._atoms[4] == SyllableAtom("s", SyllableRegion.CODA)


def test_init_empty():
    syllable = Syllable([], "", [])
    assert len(syllable._atoms) == 0


def test_init_no_onset():
    syllable = Syllable([], "a", ["d"])
    assert len(syllable._atoms) == 2
    assert syllable._atoms[0] == SyllableAtom("a", SyllableRegion.NUCLEUS)
    assert syllable._atoms[1] == SyllableAtom("d", SyllableRegion.CODA)


def test_init_no_nucleus():
    syllable = Syllable(["p"], "", ["s"])
    assert len(syllable._atoms) == 2
    assert syllable._atoms[0] == SyllableAtom("p", SyllableRegion.ONSET)
    assert syllable._atoms[1] == SyllableAtom("s", SyllableRegion.CODA)


def test_init_no_coda():
    syllable = Syllable(["b"], "o", [])
    assert len(syllable._atoms) == 2
    assert syllable._atoms[0] == SyllableAtom("b", SyllableRegion.ONSET)
    assert syllable._atoms[1] == SyllableAtom("o", SyllableRegion.NUCLEUS)


def test_init_one_one_phoneme_per_region():
    syllable = Syllable(["k"], "æ", ["p"])
    assert len(syllable._atoms) == 3
    assert syllable._atoms[0] == SyllableAtom("k", SyllableRegion.ONSET)
    assert syllable._atoms[1] == SyllableAtom("æ", SyllableRegion.NUCLEUS)
    assert syllable._atoms[2] == SyllableAtom("p", SyllableRegion.CODA)


def test_init_multiple_onsets():
    syllable = Syllable(["p", "r", "t"], "æ", ["s"])
    assert len(syllable._atoms) == 5
    assert syllable._atoms[0] == SyllableAtom("p", SyllableRegion.ONSET)
    assert syllable._atoms[1] == SyllableAtom("r", SyllableRegion.ONSET)
    assert syllable._atoms[2] == SyllableAtom("t", SyllableRegion.ONSET)
    assert syllable._atoms[3] == SyllableAtom("æ", SyllableRegion.NUCLEUS)
    assert syllable._atoms[4] == SyllableAtom("s", SyllableRegion.CODA)


def test_init_multiple_codas():
    syllable = Syllable(["k"], "æ", ["p", "s", "t"])
    assert len(syllable._atoms) == 5
    assert syllable._atoms[0] == SyllableAtom("k", SyllableRegion.ONSET)
    assert syllable._atoms[1] == SyllableAtom("æ", SyllableRegion.NUCLEUS)
    assert syllable._atoms[2] == SyllableAtom("p", SyllableRegion.CODA)
    assert syllable._atoms[3] == SyllableAtom("s", SyllableRegion.CODA)
    assert syllable._atoms[4] == SyllableAtom("t", SyllableRegion.CODA)


def test_init_long_nucleus():
    syllable = Syllable(["k"], "aeiou", ["p"])
    assert len(syllable._atoms) == 3
    assert syllable._atoms[0] == SyllableAtom("k", SyllableRegion.ONSET)
    assert syllable._atoms[1] == SyllableAtom("aeiou", SyllableRegion.NUCLEUS)
    assert syllable._atoms[2] == SyllableAtom("p", SyllableRegion.CODA)


#####################################################################
# Test __str__()
#####################################################################


def test_str_empty_syllable():
    syllable = Syllable([], "", [])
    assert str(syllable) == ""


def test_str_only_onset():
    syllable = Syllable(["b"], "", [])
    assert str(syllable) == "b"


def test_str_only_nucleus():
    syllable = Syllable([], "a", [])
    assert str(syllable) == "a"


def test_str_only_coda():
    syllable = Syllable([], "", ["t"])
    assert str(syllable) == "t"


def test_str_no_onset():
    syllable = Syllable([], "a", ["s"])
    assert str(syllable) == "as"


def test_str_no_nucleus():
    syllable = Syllable(["f"], "", ["t"])
    assert str(syllable) == "ft"


def test_str_no_coda():
    syllable = Syllable(["k"], "a", [])
    assert str(syllable) == "ka"


def test_str_onset_nucleus_coda():
    syllable = Syllable(["p", "l"], "a", ["n", "t"])
    assert str(syllable) == "plant"


#####################################################################
# Test is_last_phoneme_s()
#####################################################################


def test_is_last_phoneme_s_true():
    syllable = Syllable(onset=["t"], nucleus="ɪ", coda=["s"])
    assert syllable.is_last_phoneme_s() == True


def test_is_last_phoneme_s_false():
    syllable = Syllable(onset=["p"], nucleus="aʊ", coda=["t"])
    assert syllable.is_last_phoneme_s() == False


def test_is_last_phoneme_s_empty():
    syllable = Syllable(onset=[], nucleus="", coda=[])
    assert syllable.is_last_phoneme_s() == False


def test_is_last_phoneme_s_multiple_coda_sounds_true():
    syllable = Syllable(onset=["m"], nucleus="ɑ", coda=["t", "s"])
    assert syllable.is_last_phoneme_s() == True


def test_is_last_phoneme_s_multiple_coda_sounds_false():
    syllable = Syllable(onset=["b"], nucleus="ɔ", coda=["ɹ", "d"])
    assert syllable.is_last_phoneme_s() == False


#####################################################################
# Test map_atoms()
#####################################################################


def test_map_atoms_empty():
    syllable = Syllable([], "", [])
    atom_tuples_to_objs = {
        (
            SyllableAtom("t", SyllableRegion.ONSET),
            SyllableAtom("i", SyllableRegion.NUCLEUS),
            SyllableAtom("n", SyllableRegion.CODA),
        ): "Object 1"
    }
    objs = syllable.map_atoms(atom_tuples_to_objs)
    assert objs == []


def test_map_atoms_one_big_cluster():
    syllable = Syllable(["t"], "i", ["n"])
    atom_tuples_to_objs = {
        (
            SyllableAtom("t", SyllableRegion.ONSET),
            SyllableAtom("i", SyllableRegion.NUCLEUS),
            SyllableAtom("n", SyllableRegion.CODA),
        ): "Object"
    }
    objs = syllable.map_atoms(atom_tuples_to_objs)
    assert objs == ["Object"]


def test_map_atoms_with_single_phonemes():
    syllable = Syllable(["k"], "æ", ["s"])
    atom_tuples_to_obj = {
        (SyllableAtom("k", SyllableRegion.ONSET),): "k",
        (SyllableAtom("æ", SyllableRegion.NUCLEUS),): "a",
        (SyllableAtom("s", SyllableRegion.CODA),): "s",
    }
    objs = syllable.map_atoms(atom_tuples_to_obj)
    assert objs == ["k", "a", "s"]


def test_map_atoms_same_prefix():
    syllable = Syllable(["t", "s"], "i", ["n"])
    atom_tuples_to_objs = {
        (
            SyllableAtom("t", SyllableRegion.ONSET),
            SyllableAtom("i", SyllableRegion.NUCLEUS),
            SyllableAtom("n", SyllableRegion.CODA),
        ): "Object 1",
        (
            SyllableAtom("t", SyllableRegion.ONSET),
            SyllableAtom("s", SyllableRegion.ONSET),
            SyllableAtom("i", SyllableRegion.NUCLEUS),
            SyllableAtom("n", SyllableRegion.CODA),
        ): "Object 2",
    }
    objs = syllable.map_atoms(atom_tuples_to_objs)
    assert objs == ["Object 2"]


def test_map_atoms_with_missing_key():
    syllable = Syllable(["t", "s"], "i", ["n"])
    atom_tuples_to_objs = {
        (
            SyllableAtom("t", SyllableRegion.ONSET),
            SyllableAtom("i", SyllableRegion.NUCLEUS),
            SyllableAtom("n", SyllableRegion.CODA),
        ): "Object 1"
    }
    objs = syllable.map_atoms(atom_tuples_to_objs)
    assert objs == None


def test_map_atoms_with_clusters():
    syllable = Syllable(["k", "l"], "æ", ["p", "s"])
    atom_tuples_to_obj = {
        (SyllableAtom("k", SyllableRegion.ONSET), SyllableAtom("l", SyllableRegion.ONSET)): "kwel",
        (SyllableAtom("æ", SyllableRegion.NUCLEUS),): "a",
        (SyllableAtom("s", SyllableRegion.CODA),): "zzz",
        (SyllableAtom("p", SyllableRegion.CODA),): "y",
    }
    objs = syllable.map_atoms(atom_tuples_to_obj)
    assert objs == ["kwel", "a", "y", "zzz"]


def test_map_atoms_clusters_take_precedence():
    syllable = Syllable(["k", "l"], "æ", ["p", "s"])
    atom_tuples_to_obj = {
        (SyllableAtom("k", SyllableRegion.NUCLEUS),): "b",
        (
            SyllableAtom("k", SyllableRegion.ONSET),
            SyllableAtom("l", SyllableRegion.ONSET),
        ): "cluster1",
        (SyllableAtom("l", SyllableRegion.NUCLEUS),): "m",
        (SyllableAtom("æ", SyllableRegion.NUCLEUS),): "a",
        (SyllableAtom("s", SyllableRegion.CODA),): "zzz",
        (SyllableAtom("p", SyllableRegion.CODA),): "y",
        (
            SyllableAtom("p", SyllableRegion.CODA),
            SyllableAtom("s", SyllableRegion.CODA),
        ): "cluster2",
    }
    objs = syllable.map_atoms(atom_tuples_to_obj)
    assert objs == ["cluster1", "a", "cluster2"]


def test_map_atoms_with_overlap():
    syllable = Syllable(["t", "ʃ"], "ɛ", ["p"])
    atom_tuples_to_obj = {
        (SyllableAtom("t", SyllableRegion.ONSET), SyllableAtom("ʃ", SyllableRegion.ONSET)): "tʃ",
        (SyllableAtom("ʃ", SyllableRegion.ONSET), SyllableAtom("ɛ", SyllableRegion.NUCLEUS)): "ʃɛ",
        (SyllableAtom("ɛ", SyllableRegion.NUCLEUS), SyllableAtom("p", SyllableRegion.CODA)): "ɛp",
    }
    objs = syllable.map_atoms(atom_tuples_to_obj)
    assert objs == ["tʃ", "ɛp"]
