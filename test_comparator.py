from comparator import ignore_position_compare, line_compare, merge_files, preprocess_content


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
