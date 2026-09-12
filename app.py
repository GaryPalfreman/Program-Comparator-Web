import csv
import io

import streamlit as st

from comparator import (
    cnc_compare,
    ignore_position_compare,
    inline_difference,
    line_compare,
    merge_files,
    read_uploaded_file,
    summary_stats,
)

st.set_page_config(
    page_title="Document Comparator",
    page_icon="🔍",
    layout="wide",
)

st.markdown("""
<style>
.block-container {max-width: 1550px; padding-top: 1.25rem;}
[data-testid="stMetricValue"] {font-size: 1.8rem;}
.small-note {opacity: 0.72; font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

st.title("Document Comparator")
st.caption(
    "One comparator for general documents and CNC programs. "
    "Choose the comparison engine that matches the files you are reviewing."
)

comparison_mode = st.radio(
    "Comparison type",
    ["General Document", "CNC Program"],
    horizontal=True,
    help=(
        "General Document uses normal line-by-line comparison. "
        "CNC Program enables CNC-aware block alignment and parameter classification."
    ),
)

is_cnc = comparison_mode == "CNC Program"

ignore_sequence = True
ignore_comments = True
ignore_whitespace = True

if is_cnc:
    with st.sidebar:
        st.header("CNC comparison settings")
        ignore_sequence = st.checkbox("Ignore N sequence numbers", value=True)
        ignore_comments = st.checkbox("Ignore comments", value=True)
        ignore_whitespace = st.checkbox("Ignore whitespace", value=True)
        st.caption(
            "These settings apply only when CNC Program mode is selected. "
            "The recommended defaults focus the comparison on machining instructions."
        )
else:
    with st.sidebar:
        st.header("General document mode")
        st.caption(
            "Standard text comparison is active. Switch to CNC Program above whenever "
            "you want CNC-aware alignment and machine-code change classification."
        )

left_col, right_col = st.columns(2)
with left_col:
    file1 = st.file_uploader(
        "File 1 — reference / original",
        type=["txt", "pdf", "nc", "cnc", "tap", "iso", "mpf", "spf"],
        key="file1",
    )
with right_col:
    file2 = st.file_uploader(
        "File 2 — revised / comparison",
        type=["txt", "pdf", "nc", "cnc", "tap", "iso", "mpf", "spf"],
        key="file2",
    )

if not file1 or not file2:
    if is_cnc:
        st.info("CNC Program mode selected. Upload two CNC programs to begin.")
    else:
        st.info("General Document mode selected. Upload two documents to begin.")
    st.stop()

try:
    content1 = read_uploaded_file(file1)
    content2 = read_uploaded_file(file2)
except Exception as exc:
    st.error(f"Could not read one of the files: {exc}")
    st.stop()

if is_cnc:
    result = cnc_compare(
        content1,
        content2,
        ignore_sequence=ignore_sequence,
        ignore_comments=ignore_comments,
        ignore_whitespace=ignore_whitespace,
    )
    changes = result["changes"]
    modified = sum(c["status"] == "modified" for c in changes)
    inserted = sum(c["status"] == "inserted" for c in changes)
    deleted = sum(c["status"] == "deleted" for c in changes)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Matched blocks", result["matched_blocks"])
    m2.metric("Modified", modified)
    m3.metric("Inserted", inserted)
    m4.metric("Deleted", deleted)
    m5.metric("Total changes", len(changes))

    tab_compare, tab_summary, tab_files, tab_general, tab_merge = st.tabs(
        ["CNC Compare", "Change Summary", "File Contents", "Ignore Position", "Merge"]
    )

    with tab_compare:
        st.subheader("CNC-aware aligned comparison")
        st.caption(
            "Inserted and deleted blocks are aligned so one extra block does not shift "
            "the remainder of the program. CNC addresses are classified automatically."
        )

        if not changes:
            st.success("No CNC differences found with the current settings.")
        else:
            filters = st.multiselect(
                "Show change types",
                ["modified", "inserted", "deleted"],
                default=["modified", "inserted", "deleted"],
            )
            visible = [c for c in changes if c["status"] in filters]

            for index, change in enumerate(visible, start=1):
                labels = " · ".join(change["categories"])
                line1 = change["file1_line"] if change["file1_line"] is not None else "—"
                line2 = change["file2_line"] if change["file2_line"] is not None else "—"
                heading = (
                    f"{index}. {change['status'].upper()} — "
                    f"File 1 line {line1} ↔ File 2 line {line2} — {labels}"
                )
                with st.expander(heading, expanded=index <= 5):
                    c1, c2 = st.columns(2)
                    if change["status"] == "modified":
                        marked1, marked2 = inline_difference(change["file1"], change["file2"])
                    else:
                        marked1, marked2 = change["file1"], change["file2"]

                    with c1:
                        st.markdown(f"**{file1.name} · line {line1}**")
                        st.markdown(marked1 or "*(no corresponding block)*")
                    with c2:
                        st.markdown(f"**{file2.name} · line {line2}**")
                        st.markdown(marked2 or "*(no corresponding block)*")

                    if change["status"] == "modified":
                        st.caption(f"Block similarity: {change['similarity']}%")
                        if change["details"]:
                            st.markdown("**Changed CNC addresses**")
                            st.dataframe(
                                change["details"],
                                use_container_width=True,
                                hide_index=True,
                                column_order=["category", "address", "file1", "file2"],
                            )

    with tab_summary:
        st.subheader("CNC change summary")
        counts = result["category_counts"]
        if counts:
            summary_rows = [
                {"Change category": category, "Occurrences": count}
                for category, count in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
            ]
            st.dataframe(summary_rows, use_container_width=True, hide_index=True)
        else:
            st.success("No changes to summarize.")

        report_buffer = io.StringIO()
        writer = csv.writer(report_buffer)
        writer.writerow([
            "status", "file1_line", "file2_line", "categories",
            "address", "file1_value", "file2_value", "file1_block", "file2_block"
        ])
        for change in changes:
            if change["details"]:
                for detail in change["details"]:
                    writer.writerow([
                        change["status"], change["file1_line"] or "", change["file2_line"] or "",
                        " | ".join(change["categories"]), detail["address"], detail["file1"],
                        detail["file2"], change["file1"], change["file2"],
                    ])
            else:
                writer.writerow([
                    change["status"], change["file1_line"] or "", change["file2_line"] or "",
                    " | ".join(change["categories"]), "", "", "", change["file1"], change["file2"],
                ])

        st.download_button(
            "Download CNC comparison report (CSV)",
            data=report_buffer.getvalue(),
            file_name=f"{file1.name.rsplit('.', 1)[0]}_vs_{file2.name.rsplit('.', 1)[0]}_comparison.csv",
            mime="text/csv",
            use_container_width=True,
        )

else:
    stats = summary_stats(content1, content2)
    diffs = line_compare(content1, content2)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("File 1 lines", stats["file1_lines"])
    m2.metric("File 2 lines", stats["file2_lines"])
    m3.metric("Differences", stats["differences"])
    m4.metric("Matching lines", stats["matching_lines"])

    tab_compare, tab_files, tab_general, tab_merge = st.tabs(
        ["Document Compare", "File Contents", "Ignore Position", "Merge"]
    )

    with tab_compare:
        st.subheader("General document comparison")
        st.caption("Standard line-by-line comparison for text-based documents and PDFs.")

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
                        st.markdown(f"**{file1.name}**")
                        st.markdown(marked1 or "*(blank)*")
                    with c2:
                        st.markdown(f"**{file2.name}**")
                        st.markdown(marked2 or "*(blank)*")

with tab_files:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{file1.name}**")
        st.code(content1, language=None, line_numbers=True)
    with c2:
        st.markdown(f"**{file2.name}**")
        st.code(content2, language=None, line_numbers=True)

with tab_general:
    st.subheader("Ignore line position")
    general = ignore_position_compare(content1, content2)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Only in File 1 ({len(general['only_file1'])})**")
        st.code("\n".join(general["only_file1"]) or "No unique lines", language=None)
    with c2:
        st.markdown(f"**Only in File 2 ({len(general['only_file2'])})**")
        st.code("\n".join(general["only_file2"]) or "No unique lines", language=None)

with tab_merge:
    st.subheader("Line-based merge")
    if is_cnc:
        st.warning(
            "CNC merge is still line-based. Review machine programs carefully before "
            "using merged output on a CNC control."
        )
    prefer = st.radio(
        "When corresponding lines differ, which file should win?",
        ["File 2", "File 1"],
        horizontal=True,
    )
    merged = merge_files(
        content1,
        content2,
        prefer="file2" if prefer == "File 2" else "file1",
    )
    st.code(merged, language=None, line_numbers=True)
    st.download_button(
        "Download merged file",
        data=merged,
        file_name=f"{file1.name.rsplit('.', 1)[0]}_merged.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.divider()
st.markdown(
    '<div class="small-note">Document Comparator — general document comparison with an '
    'optional CNC-aware engine for machine-program revisions.</div>',
    unsafe_allow_html=True,
)
