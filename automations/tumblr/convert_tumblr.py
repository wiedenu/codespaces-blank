#!/usr/bin/env python3
"""Convert Tumblr HTML export to Obsidian Markdown files."""

import re
import sys
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import html2text


def parse_date(timestamp_str):
    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', timestamp_str.strip())
    for fmt in ('%B %d, %Y %I:%M%p', '%B %d, %Y %I:%M %p'):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text[:60]


def convert_post(html_file, output_dir):
    raw = html_file.read_text(encoding='utf-8', errors='replace')
    # Fix common double-encoded non-breaking spaces from Tumblr export
    raw = raw.replace('Â ', ' ').replace('Â', '')

    soup = BeautifulSoup(raw, 'html.parser')
    body = soup.find('body')
    if not body:
        return None

    # Title
    title_tag = body.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else ''
    if title_tag:
        title_tag.decompose()

    # Timestamp
    footer = body.find('div', id='footer')
    date_obj = None
    if footer:
        ts = footer.find('span', id='timestamp')
        if ts:
            date_obj = parse_date(ts.get_text(strip=True))
        footer.decompose()

    # Tags (Tumblr export puts them in <a class="tag"> or similar)
    tags = [t.get_text(strip=True) for t in body.find_all('a', class_='tag')]

    # Body → Markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0
    md_body = h.handle(body.decode_contents()).strip()

    # Frontmatter
    post_id = html_file.stem
    date_str = date_obj.strftime('%Y-%m-%d') if date_obj else 'unknown'
    safe_title = title.replace('"', '\\"')

    fm = ['---']
    if title:
        fm.append(f'title: "{safe_title}"')
    fm.append(f'date: {date_str}')
    fm.append('source: tumblr')
    fm.append(f'tumblr_id: "{post_id}"')
    if tags:
        fm.append('tags: [' + ', '.join(f'"{t}"' for t in tags) + ']')
    fm.append('---')
    fm.append('')
    if title:
        fm.append(f'# {title}')
        fm.append('')

    content = '\n'.join(fm) + md_body + '\n'

    # Filename: YYYY-MM-DD-slug.md or YYYY-MM-DD-id.md
    if date_obj and title:
        filename = f"{date_obj.strftime('%Y-%m-%d')}-{slugify(title)}.md"
    elif date_obj:
        filename = f"{date_obj.strftime('%Y-%m-%d')}-{post_id}.md"
    else:
        filename = f"{post_id}.md"

    (output_dir / filename).write_text(content, encoding='utf-8')
    return filename


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_tumblr.py <export_dir> [output_dir]")
        print("  export_dir  path to extracted Tumblr export folder")
        print("  output_dir  where to write .md files (default: ./tumblr-obsidian)")
        sys.exit(1)

    export_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('./tumblr-obsidian')
    html_dir = export_dir / 'html'

    if not html_dir.exists():
        print(f"Error: {html_dir} not found. Is this the right export folder?")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    html_files = sorted(html_dir.glob('*.html'))
    print(f"Found {len(html_files)} posts → converting to {output_dir}/\n")

    ok, fail = 0, []
    for f in html_files:
        try:
            name = convert_post(f, output_dir)
            print(f"  OK  {name}")
            ok += 1
        except Exception as e:
            print(f"  ERR {f.name}: {e}")
            fail.append(f.name)

    print(f"\n{ok}/{len(html_files)} converted.", end='')
    if fail:
        print(f" {len(fail)} failed: {', '.join(fail)}")
    else:
        print(" All good.")


if __name__ == '__main__':
    main()
