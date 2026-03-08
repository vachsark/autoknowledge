#!/usr/bin/env python3
"""Convert markdown files to PDF.

Usage:
    python md2pdf.py input.md [output.pdf]
    python md2pdf.py --dir Knowledge/ --output research-notes.pdf

Requires: pip install markdown weasyprint
"""

import argparse
import sys
from pathlib import Path

try:
    import markdown
    from weasyprint import HTML
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install markdown weasyprint")
    sys.exit(1)


CSS = """
body {
    font-family: 'Georgia', serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 40px;
    line-height: 1.6;
    color: #333;
}
h1 { font-size: 1.8em; border-bottom: 2px solid #333; padding-bottom: 8px; }
h2 { font-size: 1.4em; margin-top: 2em; color: #555; }
h3 { font-size: 1.1em; color: #666; }
code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
pre { background: #f4f4f4; padding: 16px; border-radius: 6px; overflow-x: auto; }
blockquote { border-left: 4px solid #ddd; margin-left: 0; padding-left: 16px; color: #666; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; }
th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
th { background: #f4f4f4; }
a { color: #2563eb; }
hr { border: none; border-top: 1px solid #ddd; margin: 2em 0; }
@page { margin: 1in; }
"""


def md_to_html(md_text: str) -> str:
    """Convert markdown text to HTML with styling."""
    extensions = ["tables", "fenced_code", "codehilite", "toc", "meta"]
    html_body = markdown.markdown(md_text, extensions=extensions)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}</body></html>"""


def convert_file(input_path: Path, output_path: Path) -> None:
    """Convert a single markdown file to PDF."""
    md_text = input_path.read_text(encoding="utf-8")
    html = md_to_html(md_text)
    HTML(string=html).write_pdf(str(output_path))
    print(f"  {input_path.name} -> {output_path.name}")


def convert_directory(dir_path: Path, output_path: Path) -> None:
    """Concatenate all markdown files in a directory into one PDF."""
    md_files = sorted(dir_path.glob("*.md"))
    md_files = [f for f in md_files if not f.name.startswith("_")]

    if not md_files:
        print(f"No markdown files found in {dir_path}")
        sys.exit(1)

    combined = []
    for f in md_files:
        combined.append(f.read_text(encoding="utf-8"))
        combined.append("\n\n---\n\n")

    html = md_to_html("\n".join(combined))
    HTML(string=html).write_pdf(str(output_path))
    print(f"  {len(md_files)} files -> {output_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Convert markdown to PDF")
    parser.add_argument("input", nargs="?", help="Input markdown file")
    parser.add_argument("output", nargs="?", help="Output PDF file")
    parser.add_argument("--dir", help="Convert all .md files in directory")
    args = parser.parse_args()

    if args.dir:
        dir_path = Path(args.dir)
        output = Path(args.output) if args.output else Path(f"{dir_path.name}.pdf")
        convert_directory(dir_path, output)
    elif args.input:
        input_path = Path(args.input)
        output = Path(args.output) if args.output else input_path.with_suffix(".pdf")
        convert_file(input_path, output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
