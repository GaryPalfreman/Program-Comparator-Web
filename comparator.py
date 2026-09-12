import io
import re
from collections import Counter
from difflib import SequenceMatcher
from typing import Dict, List, Tuple


def read_uploaded_file(uploaded_file) -> str:
    """Read text from a Streamlit uploaded TXT, CNC/program, or PDF file."""
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if name.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "PDF support requires PyPDF2. Install dependencies from requirements.txt."
            ) from exc
        reader = PdfReader(io.BytesIO(data))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)

    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def preprocess_content(content: str) -> List[str]:
    """Strip leading line numbers in the original app format, whitespace and blanks."""
    stripped_lines = []
    for line in content.splitlines():
        stripped_line = re.sub(r"^\d+:\s*", "", line).strip()
        if stripped_line:
            stripped_lines.append(stripped_line)
    return stripped_lines


def normalize_content(content: str) -> List[str]:
    processed = preprocess_content(content)
    return sorted(line.strip() for line in processed if line.strip())


def line_compare(content1: str, content2: str) -> List[Dict]:
    a = preprocess_content(content1)
    b = preprocess_content(content2)
    max_lines = max(len(a), len(b))
    diffs = []

    for i in range(max_lines):
        left = a[i] if i < len(a) else ""
        right = b[i] if i < len(b) else ""
        if left != right:
            diffs.append(
                {
                    "line": i + 1,
                    "file1": left,
                    "file2": right,
                    "similarity": round(SequenceMatcher(None, left, right).ratio() * 100, 1),
                }
            )
    return diffs


def ignore_position_compare(content1: str, content2: str) -> Dict[str, List[str]]:
    """Compare without line position while preserving duplicate lines."""
    left = Counter(preprocess_content(content1))
    right = Counter(preprocess_content(content2))
    only_left = list((left - right).elements())
    only_right = list((right - left).elements())
    return {"only_file1": only_left, "only_file2": only_right}


def merge_files(content1: str, content2: str, prefer: str = "file2") -> str:
    a = preprocess_content(content1)
    b = preprocess_content(content2)
    max_lines = max(len(a), len(b))
    merged = []

    for i in range(max_lines):
        left = a[i] if i < len(a) else ""
        right = b[i] if i < len(b) else ""
        if left == right:
            merged.append(left)
        else:
            merged.append(right if prefer == "file2" else left)
    return "\n".join(merged)


def inline_difference(left: str, right: str) -> Tuple[str, str]:
    """Return simple marked-up text for changed characters."""
    matcher = SequenceMatcher(None, left, right)
    lparts, rparts = [], []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        ltxt = left[i1:i2]
        rtxt = right[j1:j2]
        if tag == "equal":
            lparts.append(ltxt)
            rparts.append(rtxt)
        else:
            if ltxt:
                lparts.append(f"**{ltxt}**")
            if rtxt:
                rparts.append(f"**{rtxt}**")
    return "".join(lparts), "".join(rparts)


def summary_stats(content1: str, content2: str) -> Dict[str, int]:
    a = preprocess_content(content1)
    b = preprocess_content(content2)
    diffs = line_compare(content1, content2)
    return {
        "file1_lines": len(a),
        "file2_lines": len(b),
        "differences": len(diffs),
        "matching_lines": max(min(len(a), len(b)) - len(diffs), 0),
    }
