import streamlit as st

from comparator import (
    ignore_position_compare,
    inline_difference,
    line_compare,
    merge_files,
    read_uploaded_file,
    summary_stats,
)

st.set_page_config(
    page_title="Program & Document Comparator",
    page_icon="🔍",
    layout="wide",
)

st.markdown("""
<style>
.block-container {max-width: 1500px; padding-top: 1.5rem;}
[data-testid="stMetricValue"] {font-size: 1.8rem;}
.small-note {opacity: 0.75; font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

st.title("Program & Document Comparator")
st.caption(
    "Compare CNC programs, text files and PDFs in your browser. "
    "Nothing is intentionally stored by this app."
)

left_col, right_col = st.columns(2)

with left_col:
    file1 = st.file_uploader(
        "File 1",
        type=["txt", "pdf", "nc", "cnc", "tap", "iso", "mpf", "spf"],
        key="file1",
    )

with right_col:
    file2 = st.file_uploader(
        "File 2",
        type=["txt", "pdf", "nc", "cnc", "tap", "iso", "mpf", "spf"],
        key="file2",
    )

if not file1 or not file2:
    st.info("Upload two files to begin.")
    st.stop()

try:
    content1 = read_uploaded_file(file1)
    content2 = read_uploaded_file(file2)
except Exception as exc:
    st.error(f"Could not read one of the files: {exc}")
    st.stop()

stats = summary_stats(content1, content2)

m1, m2, m3, m4 = st.columns(4)
m1.metric("File 1 lines", stats["file1_lines"])
m2.metric("File 2 lines", stats["file2_lines"])
m3.metric("Differences", stats["differences"])
m4.metric("Matching lines", stats["matching_lines"])

tab_compare, tab_ignore, tab_files, tab_merge = st.tabs(
    ["Line Compare", "Ignore Position", "File Contents", "Merge"]
)

with tab_compare:
    st.subheader("Line-by-line comparison")
    diffs = line_compare(content1, content2)

    if not diffs:
        st.success("No differences found.")
    else:
        st.warning(f"{len(diffs)} differing line(s) found.")
        show_all = st.checkbox("Show all differences", value=True)
        limit = len(diffs) if show_all else min(50, len(diffs))

        for diff in diffs[:limit]:
            with st.expander(
                f"Line {diff['line']} — similarity {diff['similarity']}%",
                expanded=diff["line"] <= 5,
            ):
                marked1, marked2 = inline_difference(diff["file1"], diff["file2"])
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**File 1**")
                    st.markdown(marked1 or "*(blank)*")
                with c2:
                    st.markdown("**File 2**")
                    st.markdown(marked2 or "*(blank)*")

with tab_ignore:
    st.subheader("Ignore line position")
    result = ignore_position_compare(content1, content2)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"**Only in File 1 ({len(result['only_file1'])})**")
        st.code("\n".join(result["only_file1"]) or "No unique lines", language=None)

    with c2:
        st.markdown(f"**Only in File 2 ({len(result['only_file2'])})**")
        st.code("\n".join(result["only_file2"]) or "No unique lines", language=None)

with tab_files:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{file1.name}**")
        st.code(content1, language=None, line_numbers=True)
    with c2:
        st.markdown(f"**{file2.name}**")
        st.code(content2, language=None, line_numbers=True)

with tab_merge:
    st.subheader("Create merged file")
    prefer = st.radio(
        "When corresponding lines differ, which file should win?",
        ["File 2", "File 1"],
        horizontal=True,
    )
    merged = merge_files(content1, content2, prefer="file2" if prefer == "File 2" else "file1")

    st.code(merged, language=None, line_numbers=True)
    base = file1.name.rsplit(".", 1)[0]
    st.download_button(
        "Download merged file",
        data=merged,
        file_name=f"{base}_merged.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.divider()
st.markdown(
    '<div class="small-note">Web conversion of the original Tkinter Program Checking App.</div>',
    unsafe_allow_html=True,
)
