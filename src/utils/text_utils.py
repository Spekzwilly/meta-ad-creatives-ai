import re
from typing import Optional


def clean_product_text(text: str) -> str:
    if not text:
        return text
    text = re.sub(r'<[^>]+>', '', text)
    text = (text
            .replace('&nbsp;', ' ')
            .replace('&amp;', '&')
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&quot;', '"')
            .replace('&#39;', "'"))
    return re.sub(r'\s+', ' ', text).strip()


def parse_markdown_table(text: str) -> Optional[dict]:
    if not text:
        return None

    table_lines = []
    in_table = False
    for line in text.strip().split('\n'):
        if '|' in line:
            clean = line.strip()
            if (clean.startswith('|') and clean.endswith('|')) or clean.count('|') >= 2:
                table_lines.append(clean)
                in_table = True
        elif in_table and not line.strip():
            break
        elif in_table and not line.strip().startswith('-'):
            break

    if len(table_lines) < 2:
        return None

    try:
        headers = None
        data = []
        for line in table_lines:
            if re.match(r'^[\s\|\-\:]+$', line):
                continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if headers is None:
                headers = cells
            elif len(cells) == len(headers):
                data.append(cells)
        if headers and data:
            return {"headers": headers, "data": data}
    except Exception:
        pass

    return None
