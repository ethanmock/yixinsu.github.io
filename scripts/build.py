#!/usr/bin/env python3
"""Inject content from data/*.json into index.html.

Content lives in data/news.json and data/publications.json (the source of
truth). index.html is a self-contained bundle; this script rewrites the
`news = [...]` and `pubs = [...]` arrays embedded in its template with the
JSON data, re-encoding the bundle exactly the way the runtime expects.

Usage:
    python3 scripts/build.py          # edit data/*.json first, then run this
    python3 scripts/build.py --check  # verify index.html is already in sync

Workflow: edit data/*.json  ->  python3 scripts/build.py  ->  git commit
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")

def safe_json(obj):
    # json.dumps, but keep "</script>" (and any "</...") from closing the
    # host <script> tag. "\/" is a valid JSON escape that parses back to "/".
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

def find_array(s, name):
    """Return (start, end) covering the [...] of `name = [ ... ]` in s."""
    m = re.search(re.escape(name) + r"\s*=\s*\[", s)
    if not m:
        raise SystemExit(f"[build] could not find `{name} = [` in template")
    j = s.index("[", m.start())
    depth = 0
    for k in range(j, len(s)):
        if s[k] == "[":
            depth += 1
        elif s[k] == "]":
            depth -= 1
            if depth == 0:
                return j, k + 1
    raise SystemExit(f"[build] unbalanced brackets for `{name}`")

def rebuild():
    html = open(INDEX, encoding="utf-8").read()
    tpl_m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)',
                      html, re.S)
    if not tpl_m:
        raise SystemExit("[build] template script block not found in index.html")
    template = json.loads(tpl_m.group(2).strip())

    news = json.load(open(os.path.join(ROOT, "data", "news.json"), encoding="utf-8"))
    pubs = json.load(open(os.path.join(ROOT, "data", "publications.json"), encoding="utf-8"))

    # Replace pubs first so news' offsets stay valid, then news; recompute each.
    for name, data in (("pubs", pubs), ("news", news)):
        a, b = find_array(template, name)
        template = template[:a] + json.dumps(data, ensure_ascii=False) + template[b:]

    new_body = safe_json(template)
    new_html = html[:tpl_m.start(2)] + new_body + html[tpl_m.end(2):]
    return html, new_html

def main():
    old, new = rebuild()
    if "--check" in sys.argv:
        if old == new:
            print("[build] index.html is in sync with data/*.json")
            return 0
        print("[build] OUT OF SYNC — run `python3 scripts/build.py`")
        return 1
    if old == new:
        print("[build] no changes (index.html already up to date)")
        return 0
    open(INDEX, "w", encoding="utf-8").write(new)
    print(f"[build] index.html updated ({len(new)//1024} KB)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
