# Notion to PDF Converter

Batch convert Notion HTML exports to PDF with optional watermark and Traditional-to-Simplified Chinese transcoding.

## Features

- Convert a single HTML file or an entire exported Notion workspace
- Add a watermark to every page
- Optionally transcode Traditional Chinese to Simplified Chinese

## Installation

```bash
pip install opencc-python-reimplemented beautifulsoup4 playwright
playwright install chromium
```

## Usage

```bash
# Convert a directory
python convert.py ./notion_export

# Convert a single file
python convert.py page.html

# Specify output directory
python convert.py ./notion_export -o ./output_pdf

# Enable Traditional → Simplified Chinese transcoding
python convert.py ./notion_export --transcode
```

## Notion Export Steps

1. Notion → Settings → **Export all workspace content**
2. Format: **HTML**
3. Download and unzip — pass the folder as the `input` argument
