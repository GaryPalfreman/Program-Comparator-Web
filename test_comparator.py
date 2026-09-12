from comparator import (
    cnc_compare,
    cnc_normalize_line,
    ignore_position_compare,
    line_compare,
    merge_files,
    preprocess_content,
)


def test_preprocess():
    assert preprocess_content("1: G00 X0\n\n2: G01 X1") == ["G00 X0", "G01 X1"]


def test_line_compare():
    diffs = line_compare("A\nB", "A\nC")
    assert len(diffs) == 1
    assert diffs[0]["line"] == 2


def test_ignore_position_preserves_duplicates():
    result = ignore_position_compare("A\nA\nB", "A\nB")
    assert result["only_file1"] == ["A"]


def test_merge():
    assert merge_files("A\nB", "A\nC", prefer="file2") == "A\nC"


def test_cnc_normalization_ignores_sequence_comments_and_spaces():
    assert cnc_normalize_line("N100 G01 X10.0 Y5.0 (CUT)") == "G01X10.0Y5.0"


def test_cnc_alignment_handles_inserted_block_without_cascade():
    old = "N10 G00 X0\nN20 G01 X10 F100\nN30 M30"
    new = "N100 G00 X0\nN110 S2500 M03\nN120 G01 X10 F100\nN130 M30"
    result = cnc_compare(old, new)
    assert len(result["changes"]) == 1
    assert result["changes"][0]["status"] == "inserted"


def test_cnc_classifies_feed_and_position_change():
    old = "N10 G01 X10.0 Y5.0 F100"
    new = "N20 G01 X10.5 Y5.0 F120"
    result = cnc_compare(old, new)
    change = result["changes"][0]
    assert "POSITION CHANGE" in change["categories"]
    assert "FEED CHANGE" in change["categories"]
    assert "SEQUENCE CHANGE" not in change["categories"]
