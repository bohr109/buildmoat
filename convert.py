import os
import argparse
import tempfile
import opencc
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pathlib import Path

WATERMARK_TEXT = "buildmoat.org"


def convert_chinese(soup: BeautifulSoup) -> BeautifulSoup:
    converter = opencc.OpenCC('t2s')
    for text_node in soup.find_all(string=True):
        if text_node.parent.name not in ['style', 'script']:
            text_node.replace_with(converter.convert(str(text_node)))
    return soup


def add_watermark_css(watermark_text: str) -> str:
    return f"""
    body::before {{
        content: "{watermark_text}";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 80px;
        color: rgba(200, 200, 200, 0.4);
        z-index: 9999;
        pointer-events: none;
        white-space: nowrap;
    }}
    """


def process_file(html_path: Path, output_dir: Path, transcode: bool):
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    if transcode:
        soup = convert_chinese(soup)

    # Inject watermark CSS into <head>
    style_tag = soup.new_tag('style')
    style_tag.string = add_watermark_css(WATERMARK_TEXT)
    if soup.head:
        soup.head.append(style_tag)
    else:
        soup.insert(0, style_tag)

    output_path = output_dir / html_path.with_suffix('.pdf').name

    # Write temp file next to the original so relative image paths resolve correctly
    tmp_path = html_path.parent / f"_tmp_{html_path.name}"
    try:
        tmp_path.write_text(str(soup), encoding='utf-8')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp_path.absolute().as_uri(), wait_until='networkidle')
            page.pdf(path=str(output_path), format='A4', print_background=True)
            browser.close()
    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"  -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Convert Notion HTML exports to PDF')
    parser.add_argument('input', help='Path to a single HTML file or a directory of HTML files')
    parser.add_argument('-o', '--output', default='./output_pdf', help='Output directory (default: ./output_pdf)')
    parser.add_argument('--transcode', action='store_true', help='Convert Traditional Chinese to Simplified Chinese')
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file():
        if input_path.suffix.lower() != '.html':
            print(f"Error: {input_path} is not an HTML file")
            return
        html_files = [input_path]
    elif input_path.is_dir():
        html_files = list(input_path.rglob('*.html'))
        if not html_files:
            print(f"No HTML files found in {input_path}")
            return
    else:
        print(f"Error: {input_path} does not exist")
        return

    print(f"Found {len(html_files)} file(s). Transcode: {args.transcode}")
    for i, html_file in enumerate(html_files, 1):
        print(f"[{i}/{len(html_files)}] {html_file.name}")
        try:
            process_file(html_file, output_dir, transcode=args.transcode)
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == '__main__':
    main()
