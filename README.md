# Program & Document Comparator

A browser-based conversion of the original Tkinter **Program Checking App**.

## Features

- Upload and compare two files
- TXT and PDF support
- CNC/program file extensions supported: `.nc`, `.cnc`, `.tap`, `.iso`, `.mpf`, `.spf`
- Line-by-line differences
- Changed characters highlighted
- Similarity percentage per differing line
- Ignore-position comparison
- Duplicate lines are preserved in ignore-position mode
- Side-by-side source display
- Merge results using File 1 or File 2 as the preferred source
- Download the merged file directly from the browser

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud.
2. Choose **Create app**.
3. Select `GaryPalfreman/Program-Comparator-Web` and the `main` branch.
4. Set the main file path to `app.py`.
5. Deploy.

## Project structure

```text
.
├── app.py
├── comparator.py
├── requirements.txt
├── README.md
├── .gitignore
├── test_comparator.py
└── .streamlit/
    └── config.toml
```

## Notes

PDF comparison depends on extractable PDF text. Scanned/image-only PDFs require OCR, which is not included in this version.

The merge logic follows the original application's line-based behaviour, with the addition that the user can choose which file wins when a line differs.
