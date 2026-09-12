# Document Comparator

A browser-based comparator for general documents and CNC programs.

## Comparison modes

### General Document

Use this for ordinary text-based documents and PDFs. It provides:

- Line-by-line comparison
- Changed-character highlighting
- Similarity percentage per differing line
- Ignore-position comparison
- Side-by-side source display
- Simple line-based merge and download

### CNC Program

Select **CNC Program** before comparing machine programs. This enables the CNC-aware engine with:

- Alignment of inserted and deleted CNC blocks
- Optional ignoring of N sequence numbers, comments and whitespace
- CNC address parsing and classification
- G-code and M-code changes
- X/Y/Z/A/B/C/U/V/W position changes
- I/J/K/R arc and geometry changes
- Feed `F`, spindle `S`, tool `T`, H/D offset and cycle parameter changes
- Macro change detection
- CNC change summary
- Downloadable CSV comparison report

## Supported files

- `.txt`
- `.pdf`
- `.nc`
- `.cnc`
- `.tap`
- `.iso`
- `.mpf`
- `.spf`

PDF comparison depends on extractable PDF text. Scanned/image-only PDFs require OCR, which is not included in this version.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Live deployment

The `main` branch is deployed through Streamlit Community Cloud with `app.py` as the main application file.

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

## Safety note

The current merge function remains line-based. CNC programs should always be reviewed and validated before any merged output is used on a machine control.
