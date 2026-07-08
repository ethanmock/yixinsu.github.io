#!/usr/bin/env python3
"""Inject content + config from data/ into index.html.

Sources of truth (edit these, never hand-edit index.html):
    data/news.json          news / updates list
    data/publications.json  publications list
    data/config.json        site settings: accent, defaultLang,
                            showResearchDemo, demoUrl

index.html is a self-contained bundle. This script rewrites:
  * the `news = [...]` and `pubs = [...]` arrays in its template, and
  * the prop defaults inside the template's data-props attribute,
then re-encodes the bundle the way the runtime expects.

Usage:
    python3 scripts/build.py          # edit data/*.json first, then run this
    python3 scripts/build.py --check  # verify index.html is already in sync

Workflow: edit data/*.json  ->  python3 scripts/build.py  ->  git commit
"""
import json, re, sys, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")

# Which config keys map onto template props (data-props schema defaults).
CONFIG_KEYS = ("accent", "defaultLang", "showResearchDemo", "demoUrl")


def safe_json(obj):
    # json.dumps, but keep "</script>" (and any "</...") from closing the
    # host <script> tag. "\/" is a valid JSON escape that parses back to "/".
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def attr_escape(s):
    # Escape a string for use inside a double-quoted HTML attribute.
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


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


def apply_config(template, config):
    """Set prop defaults inside the data-props attribute from config."""
    m = re.search(r'data-props="([^"]*)"', template)
    if not m:
        raise SystemExit("[build] data-props attribute not found in template")
    schema = json.loads(html.unescape(m.group(1)))
    for key in CONFIG_KEYS:
        if key in config and key in schema and isinstance(schema[key], dict):
            schema[key]["default"] = config[key]
    new_attr = 'data-props="' + attr_escape(json.dumps(schema, ensure_ascii=False)) + '"'
    return template[:m.start()] + new_attr + template[m.end():]


def rebuild():
    html_text = open(INDEX, encoding="utf-8").read()
    tpl_m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)',
                      html_text, re.S)
    if not tpl_m:
        raise SystemExit("[build] template script block not found in index.html")
    template = json.loads(tpl_m.group(2).strip())

    def load(name):
        return json.load(open(os.path.join(ROOT, "data", name), encoding="utf-8"))

    news = load("news.json")
    pubs = load("publications.json")
    config_path = os.path.join(ROOT, "data", "config.json")
    config = json.load(open(config_path, encoding="utf-8")) if os.path.exists(config_path) else {}

    # Replace arrays (pubs first so offsets stay valid; each is recomputed).
    for name, data in (("pubs", pubs), ("news", news)):
        a, b = find_array(template, name)
        template = template[:a] + json.dumps(data, ensure_ascii=False) + template[b:]

    if config:
        template = apply_config(template, config)

    new_body = safe_json(template)
    new_html = html_text[:tpl_m.start(2)] + new_body + html_text[tpl_m.end(2):]
    return html_text, new_html


def main():
    old, new = rebuild()
    if "--check" in sys.argv:
        if old == new:
            print("[build] index.html is in sync with data/*")
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
