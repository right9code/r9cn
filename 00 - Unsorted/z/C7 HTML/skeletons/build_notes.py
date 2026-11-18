#!/usr/bin/env python3
"""Convert the C07 markdown notes into c7-notes.json for the app's Notes pane.

Source: /home/right9zzz/Z/r9AE/C07 (user-authorized study notes)
Output: c7-notes.json  -> {grammar:[{title,html}], writing:[...], literature:[...]}
"""
import json, os, re
import markdown

SRC = '/home/right9zzz/Z/r9AE/C07'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c7-notes.json')

# file path (relative to SRC) -> card order/key
GRAMMAR = [
    ('grammar', 'LANGUAGE/C07 - G - 02 - NOUNS.md'),
    ('grammar', 'LANGUAGE/C07 - G - 04 - PRONOUNS.md'),
    ('grammar', 'LANGUAGE/C07 - G - 05 - ADJECTIVES.md'),
    ('grammar', 'LANGUAGE/C07 - G - 07 - ADVERBS.md'),
    ('grammar', 'LANGUAGE/C07 - G - 08 - ARTICLES.md'),
    ('grammar', 'LANGUAGE/C07 - G - 12 - PERFECT TENSES.md'),
    ('grammar', 'LANGUAGE/C07 - G - 14 - MODALS AND AUXILIARIES.md'),
    ('grammar', 'LANGUAGE/C07 - G - 15 - NON-FINITE VERBS.md'),
    ('grammar', 'LANGUAGE/C07 - G - 16 - TRANSITIVE AND INTRANSITIVE VERBS.md'),
    ('grammar', 'LANGUAGE/C07 - G - 17 - ACTIVE AND PASSIVE VOICE.md'),
]

WRITING = [
    ('writing', 'LANGUAGE/Writing/C07 - W - 18 - NOTICE WRITING.md'),
    ('writing', 'LANGUAGE/Writing/C07 - W - 09 - DIARY WRITING.md'),
    ('writing', 'LANGUAGE/Writing/C07 - W - 33 - STORY WRITING.md'),
    ('writing', 'LANGUAGE/Writing/C07 - W - 17 - EMAIL WRITING.md'),
    ('writing', 'LANGUAGE/Writing/C07 - W - 13 - INFORMAL LETTER.md'),
    ('writing', 'LANGUAGE/Writing/C07 - W - 14 - INFORMAL INVITATION LETTER.md'),
    ('writing', 'LANGUAGE/Writing/C07 - W - 06 - ESSAY WRITING.md'),
    ('writing', 'LANGUAGE/Writing/C07 - W - 26 - ARTICLE WRITING.md'),
]

LITERATURE = [
    ('literature', 'LITERATURE/C07 - 01 - THE DAY THE RIVER SPOKE.md'),
    ('literature', 'LITERATURE/C07 - 04 - ANIMALS BIRDS AND DR DOLITTLE.md'),
    ('literature', 'LITERATURE/C07 - 05 - A FUNNY MAN - POETRY.md'),
    ('literature', 'LITERATURE/C07 - 06 - SAY THE RIGHT THING.md'),
    ('literature', 'LITERATURE/C07 - 07 - MY BROTHERS GREAT INVENTION.md'),
    ('literature', 'LITERATURE/C07 - 08 - PAPER BOATS - POETRY.md'),
    ('literature', 'LITERATURE/C07 - 09 - NORTH SOUTH EAST WEST.md'),
    ('literature', 'LITERATURE/C07 - 10 - THE TUNNEL.md'),
    ('literature', 'LITERATURE/C07 - 11 - TRAVEL - POETRY.md'),
    ('literature', 'LITERATURE/C07 - 14 - MY DEAR SOLDIERS - POETRY.md'),
    ('literature', 'LITERATURE/C07 - 15 - RANI ABBAKKA.md'),
]

EXTS = ['tables', 'fenced_code', 'nl2br', 'sane_lists']

LIST_RE = re.compile(r'^\s*(- |\d+\. )')


def fix_lists(text):
    """Python-Markdown needs a blank line before a list; the source often has
    the list starting right after a paragraph line (lazy continuation)."""
    out, in_code = [], False
    for ln in text.split('\n'):
        if ln.strip().startswith('```'):
            in_code = not in_code
        if (not in_code and out and out[-1].strip() != ''
                and LIST_RE.match(ln) and not LIST_RE.match(out[-1])):
            out.append('')
        out.append(ln)
    return '\n'.join(out)


def strip_first_h1(html, title):
    """The card <summary> already shows the title - drop the duplicate h1."""
    m = re.match(r'\s*<h1>.*?</h1>', html, flags=re.S)
    if m and re.sub(r'<[^>]+>', '', m.group(0)).strip().lower() == title.strip().lower():
        return html[m.end():].lstrip()
    return html


SMALL = {'and', 'the', 'of', 'in', 'to', 'a', 'an'}


def pretty_title(t):
    t = t.strip()
    if t == t.upper() and any(c.isalpha() for c in t):
        words = t.title().split()
        t = ' '.join(w if (i == 0 or w.lower() not in SMALL) else w.lower()
                     for i, w in enumerate(words))
    return t


def convert(path):
    text = open(path, encoding='utf8').read()
    html = markdown.markdown(fix_lists(text), extensions=EXTS)
    m = re.search(r'^#\s+(.+?)\s*$', text, re.M)
    title = pretty_title(m.group(1) if m else os.path.basename(path))
    return {'title': title, 'html': strip_first_h1(html, title)}


def main():
    notes = {'grammar': [], 'writing': [], 'literature': []}
    for group, rel in GRAMMAR + WRITING + LITERATURE:
        p = os.path.join(SRC, rel)
        if not os.path.exists(p):
            print('MISSING:', rel)
            continue
        notes[group].append(convert(p))
    json.dump(notes, open(OUT, 'w', encoding='utf8'), ensure_ascii=False)
    sizes = {k: sum(len(c['html']) for c in v) for k, v in notes.items()}
    print('cards:', {k: len(v) for k, v in notes.items()})
    print('html bytes:', sizes, '| total', sum(sizes.values()))
    print('written', OUT, os.path.getsize(OUT), 'bytes')


if __name__ == '__main__':
    main()
