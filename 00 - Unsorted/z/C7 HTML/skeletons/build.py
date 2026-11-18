#!/usr/bin/env python3
"""Build the final single-file app from c7-app-template.html + c7-data.json."""
import json, re, sys

d = json.load(open('c7-data.json', encoding='utf8'))
tpl = open('c7-app-template.html', encoding='utf8').read()

def uni_options(ans_idx, options):
    return {'answer': ans_idx, 'options': options}

DATA = {'secs': [], 'notes': {}}

GRAMMAR_TIPS = {
    'nouns': ('A noun names a person, place, thing or idea. Ask “who?” or “what?”; a group such as a choir is a collective noun.', 'संज्ञा किसी व्यक्ति, जगह, वस्तु या विचार का नाम होती है। “कौन?” या “क्या?” पूछें। choir जैसे समूह का नाम समूहवाचक संज्ञा है।'),
    'pronouns': ('A pronoun stands in for a noun. Use who for people, which for things, and me after a preposition such as between.', 'सर्वनाम संज्ञा की जगह आता है। लोगों के लिए who, वस्तुओं के लिए which और between जैसे शब्द के बाद me का प्रयोग करें।'),
    'adjectives': ('An adjective describes a noun. Use a comparative to compare two things (older) and a superlative for the top one in a group (oldest).', 'विशेषण संज्ञा के बारे में बताता है। दो चीज़ों की तुलना में comparative (older) और समूह में सबसे अधिक बताने के लिए superlative (oldest) प्रयोग करें।'),
    'adverbs': ('An adverb adds information to an action or description: how (carefully), when (tomorrow), how often (often), or how much (very).', 'क्रिया-विशेषण काम या वर्णन के बारे में बताता है: कैसे (carefully), कब (tomorrow), कितनी बार (often) या कितना (very)।'),
    'articles': ('Choose a or an by the first sound, not the first letter: a university starts with a “y” sound; an hour starts with a vowel sound. Use the for something specific.', 'a या an चुनते समय पहला अक्षर नहीं, पहली ध्वनि देखें: university की शुरुआत “य” ध्वनि से और hour की स्वर-ध्वनि से होती है। किसी खास चीज़ के लिए the लगाएँ।'),
    'perfect': ('Perfect tenses use have/has/had + a past participle. Use had for the earlier of two past actions; will have for something finished before a future time.', 'Perfect tense में have/has/had के साथ क्रिया का past participle आता है। दो बीती घटनाओं में पहले हुई घटना के लिए had और भविष्य के तय समय से पहले पूरा होने वाले काम के लिए will have प्रयोग करें।'),
    'modals': ('A modal shows meaning such as advice, need, ability or possibility. Put the base verb after it: should go, must help, can swim.', 'Modal सलाह, ज़रूरत, क्षमता या संभावना बताता है। इसके बाद क्रिया का मूल रूप आता है: should go, must help, can swim।'),
    'nonfinite': ('A to-infinitive is to + verb (to learn). After let, can, must and similar words, use the verb without to. An -ing verb can act like a noun (Swimming is fun).', 'to-infinitive में to + क्रिया आती है (to learn)। let, can, must के बाद to के बिना मूल क्रिया आती है। -ing वाली क्रिया संज्ञा का काम भी कर सकती है (Swimming is fun)।'),
    'transitive': ('After the verb, ask “what?” or “whom?” If there is an answer (sang a song), the verb is transitive. If not (birds sang), it is intransitive.', 'क्रिया के बाद “क्या?” या “किसे?” पूछें। उत्तर मिले (sang a song), तो क्रिया transitive है। उत्तर न मिले (birds sang), तो intransitive है।'),
    'voice': ('In active voice, the subject does the action. In passive voice, the subject receives it; passive verbs usually use be + a past participle (was built).', 'Active voice में subject काम करता है। Passive voice में subject पर काम होता है; passive क्रिया में आम तौर पर be + past participle आता है (was built)।'),
}

# ---------- READING ----------
def _js_string(s, i):
    """Decode the single-quoted JS string starting at s[i]; returns (value, next_i)."""
    assert s[i] == "'", s[i:i+20]
    i += 1; out = []
    esc_map = {'n': '\n', 't': '\t', 'r': '\r', "'": "'", '"': '"', '\\': '\\'}
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            out.append(esc_map.get(s[i + 1], '\\' + s[i + 1])); i += 2; continue
        if c == "'":
            return ''.join(out), i + 1
        out.append(c); i += 1
    return ''.join(out), i

def _match_bracket(s, i):
    """i points at '[' or '{' -> index of its matching closer (string-aware)."""
    open_ch = s[i]; close_ch = ']' if open_ch == '[' else '}'
    depth = 0
    while i < len(s):
        c = s[i]
        if c in "'\"":
            _, i = _js_string(s, i); continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError('unbalanced brackets')

def _str_list(blob, key):
    """head: ['a', 'b'] -> ['a', 'b']"""
    m = re.search(r'\b' + key + r": \[", blob)
    if not m:
        return []
    start = blob.index('[', m.start()); end = _match_bracket(blob, start)
    inner = blob[start + 1:end]
    out, i = [], 0
    while i < len(inner):
        if inner[i] == "'":
            val, i = _js_string(inner, i); out.append(val)
        else:
            i += 1
    return out

def extract_tables(path):
    """Recover the p.table objects ({caption, head, rows}) the data extractor dropped,
    keyed by passage title."""
    try:
        src = open(path, encoding='utf8').read()
    except OSError:
        return {}
    titles = []
    for m in re.finditer(r"\btitle: '", src):
        val, _ = _js_string(src, m.end() - 1)
        titles.append((m.start(), val))
    tables = {}
    for m in re.finditer(r'\btable: \{', src):
        start = src.index('{', m.start())
        blob = src[start:_match_bracket(src, start) + 1]
        prev = [t for t in titles if t[0] < m.start()]
        if not prev:
            continue
        cap = re.search(r"\bcaption: '", blob)
        caption = _js_string(blob, cap.end() - 1)[0] if cap else ''
        rows = []
        rm = re.search(r'\brows: \[', blob)
        if rm:
            rstart = blob.index('[', rm.start())
            for seg in re.finditer(r'\[[^\[\]]*\]', blob[rstart + 1:_match_bracket(blob, rstart)]):
                row, i = [], 0
                while i < len(seg.group(0)):
                    if seg.group(0)[i] == "'":
                        val, i = _js_string(seg.group(0), i); row.append(val)
                    else:
                        i += 1
                rows.append(row)
        tables[prev[-1][1]] = {'caption': caption, 'head': _str_list(blob, 'head'), 'rows': rows}
    return tables

def reading_sec():
    tables = extract_tables('../class7-reading-q1.html')
    tables.update(extract_tables('../class7-reading-q2.html'))
    sets = []
    for fi, file_sets in enumerate(d['reading']):
        for pi, passage in enumerate(file_sets):
            pass_obj = {'title': passage['title'], 'paras': passage['paras']}
            if passage['title'] in tables:
                pass_obj['table'] = tables[passage['title']]
            units = []
            for q in passage['questions']:
                base = {'passage': pass_obj, 'why': q.get('why')}
                if q['t'] == 'mcq':
                    units.append({**base, 'kind': 'mcq', 'q': q['q'], 'options': q['opts'], 'answer': q['a'], 'chip': 'Reading · MCQ'})
                elif q['t'] == 'tf':
                    a = q['a']
                    ans = (0 if a else 1) if isinstance(a, bool) else int(a)  # options [True, False]
                    units.append({**base, 'kind': 'mcq', 'q': q['q'], 'options': ['True', 'False'], 'answer': ans, 'chip': 'Reading · True/False'})
                elif q['t'] == 'text':
                    parts = [{'label': (p.get('label') or ''), 'a': p['a']} for p in q['parts']]
                    units.append({**base, 'kind': 'text', 'q': q['q'], 'parts': parts})
            sets.append({'id': f'reading-q{fi+1}-p{pi+1}',
                         'name': f"Q{fi+1} · {passage['title']}",
                         'sub': f'{len(units)} questions on this passage', 'units': units})
    return {'id': 'reading', 'name': 'Reading Skill', 'icon': '📖', 'step': 'Step 1', 'cvar': 'sec1',
            'sub': 'Q1–Q2 · choose a passage', 'sets': sets}

# ---------- GRAMMAR ----------
def clean_grammar_why(why):
    why = why or ''
    why = re.sub(r'^From notes[^:]*:\s*', '', why, flags=re.I)
    why = re.sub(r'^Notes answer:\s*', '', why, flags=re.I)
    why = re.sub(r'\s*\(Exam-pattern\)', '', why, flags=re.I)
    return why.strip()

def grammar_sec():
    sets = []
    for topic in d['grammar']:
        units = []
        for q in topic['questions']:
            why = clean_grammar_why(q.get('why'))
            if q['type'] == 'mcq':
                ans_idx = q['options'].index(q['answer']) if q['answer'] in q['options'] else 0
                units.append({'kind': 'mcq', 'q': q['prompt'], 'options': q['options'], 'answer': ans_idx,
                              'why': why, 'grammar': True, 'correct': q['options'][ans_idx], 'tip': {'en': GRAMMAR_TIPS[topic['id']][0], 'hi': GRAMMAR_TIPS[topic['id']][1]}, 'chip': 'Grammar · MCQ'})
            elif q['type'] == 'text':
                accepted = str(q['answer']).split('|')
                units.append({'kind': 'text', 'q': q['prompt'], 'parts': [{'label': '', 'a': accepted}],
                              'why': why, 'grammar': True, 'correct': accepted[0], 'tip': {'en': GRAMMAR_TIPS[topic['id']][0], 'hi': GRAMMAR_TIPS[topic['id']][1]}})
            elif q['type'] == 'text-multi':
                parts = [{'label': p.get('label', ''), 'a': str(p['answer']).split('|')} for p in q['parts']]
                correct = '; '.join(p['a'][0] for p in parts)
                units.append({'kind': 'text', 'q': q['prompt'], 'parts': parts,
                              'why': why, 'grammar': True, 'correct': correct, 'tip': {'en': GRAMMAR_TIPS[topic['id']][0], 'hi': GRAMMAR_TIPS[topic['id']][1]}})
        sets.append({'id': 'grammar-' + topic['id'], 'name': topic['name'], 'sub': '20 questions', 'units': units})
    return {'id': 'grammar', 'name': 'Grammar', 'icon': '🧩', 'step': 'Step 2', 'cvar': 'sec3',
            'sub': 'Q3 · 10 topics × 20 questions', 'sets': sets}

# ---------- WRITING ----------
def conv_builder(c, kind_name, format_name=None):
    grade = {k: v['answer'] for k, v in c['blanks'].items()}
    return {'kind': 'builder', 'title': c.get('title', ''), 'scenario': c['scenario'],
            'format': format_name or kind_name, 'template': c['template'],
            'blanks': c['blanks'], 'bank': c['bank'], 'grade': grade}

def writing_sec():
    w = d['writing']
    sets = []
    # Q4: one sequence exercise + builders
    q4_units = [{'kind': 'seq', 'q': 'Arrange the parts of a notice in the correct format order (use ▲/▼ to move):',
                 'items': w['q4']['order'],
                 'why': 'A notice always follows this fixed format — institutional name on top, NOTICE heading, date, title, body, contact line, signature block at the end.'}]
    for c in w['q4']['questions']:
        q4_units.append(conv_builder(c, 'q4', 'notice'))
    sets.append({'id': 'writing-q4', 'name': 'Q4 · Notice', 'sub': 'format + 5 notices · 6 questions', 'units': q4_units})
    writing_sequences = {
        'q5-diary': ('Arrange the parts of a diary entry in the correct order', ['Date and day (and time, if needed)', 'Salutation (e.g. "Dear Diary,")', 'Opening: introduce the event and your feelings', 'Body: describe what happened (events/details)', 'Closing: reflect on feelings or hope for tomorrow', 'Name / sign-off']),
        'q5-story': ('Arrange the parts of a story completion in the correct order', ['Title', 'Given opening / beginning (the cue)', 'Middle: develop the situation and build interest', 'Climax / turning point (problem or key moment)', 'Ending: resolution with a clear closing or message']),
        'q6-email': ('Arrange the parts of a formal email in the correct order', ['Date', 'From (sender’s email address)', 'To (receiver’s email address)', 'Cc (Carbon Copy)', 'Bcc (Blind Carbon Copy)', 'Subject (short and clear)', 'Salutation (e.g. Respected Sir/Madam,)', 'Body: purpose, details, and request/action', 'Closing (e.g. Regards,)', 'Name and designation/class']),
        'q6-letter': ('Arrange the parts of an informal letter in the correct order', ['Sender’s address', 'Date', 'Salutation (e.g. Dear Rahul,)', 'Introduction: greeting and reason for writing', 'Main body: details, feelings, or news', 'Conclusion: closing remarks / hope to meet or hear back', 'Subscription (e.g. Yours lovingly,)', 'Sender’s name']),
        'q7-essay': ('Arrange the parts of an essay in the correct order', ['Title', 'Introduction: hook and main idea (thesis)', 'Body paragraph 1: first point with example', 'Body paragraph 2: second point with example', 'Body paragraph 3: third point / personal view', 'Conclusion: round off and leave a strong final thought']),
        'q7-article': ('Arrange the parts of an article in the correct order', ['Title (catchy and centred)', 'Byline (By Name, Class)', 'Introduction: a striking hook, then the topic', 'Body: causes and effects / analysis', 'Conclusion: practical solutions and a call to action']),
    }
    for gid, gkey, label, sub in [('q5', 'diary', 'Q5 · Diary Entry', '4 diary tasks'),
                                  ('q5', 'story', 'Q5 · Story Completion', '4 story tasks'),
                                  ('q6', 'email', 'Q6 · Formal Email', '4 email tasks'),
                                  ('q6', 'letter', 'Q6 · Informal Letter', '4 letter tasks'),
                                  ('q7', 'essay', 'Q7 · Essay', '4 essay tasks'),
                                  ('q7', 'article', 'Q7 · Article', '4 article tasks')]:
        units = []
        seq = writing_sequences[gid + '-' + gkey]
        units.append({'kind': 'seq', 'q': seq[0], 'items': seq[1], 'why': 'Follow the standard format order.'})
        units.extend(conv_builder(c, gid, gkey) for c in w[gid][gkey])
        sets.append({'id': f'writing-{gid}-{gkey}', 'name': label, 'sub': sub + ' + format order', 'units': units})
    return {'id': 'writing', 'name': 'Writing Skills', 'icon': '✍️', 'step': 'Step 3', 'cvar': 'sec2',
            'sub': 'Q4–Q7 · 7 task sets', 'sets': sets}

# ---------- LITERATURE ----------
def group_by(items, key):
    """dict-of-lists preserving first-seen order"""
    out = {}
    for it in items:
        out.setdefault(key(it), []).append(it)
    return out

def extract_units(extracts, chip='Extract'):
    units = []
    for e in extracts:
        pass_obj = {'title': e['title'], 'paras': e['text']}
        for q in e['questions']:
            if q['type'] == 'mcq':
                units.append({'passage': pass_obj, 'kind': 'mcq', 'q': q['q'], 'options': q['options'],
                              'answer': q['answer'], 'why': q.get('why'), 'chip': chip + ' · MCQ'})
            else:  # fill
                parts = [{'label': p['label'], 'answer': p['answer'], 'tiles': p['tiles']} for p in q['parts']]
                units.append({'passage': pass_obj, 'kind': 'fill', 'q': q['q'], 'parts': parts, 'why': q.get('why')})
    return units

def prose_labels(extracts):
    """Recover the empty prose titles from the source: labels in class7-literature-q9.html."""
    try:
        html = open('../class7-literature-q9.html', encoding='utf8').read()
    except OSError:
        return None
    labels = re.findall(r"source:\s*'([^']*)'", html)
    return labels if len(labels) == len(extracts) else None

def cloze_units(questions):
    units = []
    for q in questions:
        bank, grade = [], {}
        parts = []
        for p in q['parts']:
            if p.get('blank'):
                key = 'b' + str(len(parts))
                correct = p['options'][p['answer']]
                parts.append({'key': key, 'blank': True})
                grade[key] = correct
                bank.extend(p['options'])
            else:
                parts.append({'text': p['text']})
        bank = list(dict.fromkeys(bank))  # dedupe preserving order
        units.append({'kind': 'cloze', 'q': q['q'], 'parts': parts, 'bank': bank, 'grade': grade,
                      'src': q.get('src'), 'why': q.get('why')})
    return units

def lit_sub_extracts(n, units):
    return f"{n} extract{'s' if n > 1 else ''} · {len(units)} questions"

def literature_sec():
    sets = []
    # Q8 — one card per poem
    for i, (title, extracts) in enumerate(group_by(d['litExtracts'][0], lambda e: e['title']).items(), 1):
        units = extract_units(extracts)
        sets.append({'id': f'lit-q8-p{i}', 'name': title, 'group': 'Q8 · Poem Extracts',
                     'sub': lit_sub_extracts(len(extracts), units), 'units': units})
    # Q9 — one card per chapter (titles recovered from the source: labels)
    extracts9 = d['litExtracts'][1]
    labels = prose_labels(extracts9)
    if not labels:
        labels = [f'Extract {i+1}' for i in range(len(extracts9))]
    for i, (label, extracts) in enumerate(group_by(list(zip(labels, extracts9)), lambda t: t[0]).items(), 1):
        units = extract_units([e for _, e in extracts])
        sets.append({'id': f'lit-q9-c{i}', 'name': label, 'group': 'Q9 · Prose Extracts',
                     'sub': lit_sub_extracts(len(extracts), units), 'units': units})
    # Q10 — one card per chapter, 3 short answers each
    for i, (src, qs) in enumerate(group_by(d['litCloze'][0]['questions'], lambda q: q['src']).items(), 1):
        units = cloze_units(qs)
        sets.append({'id': f'lit-q10-c{i}', 'name': src, 'group': 'Q10 · Short Answers',
                     'sub': f'{len(units)} short-answer questions', 'units': units})
    # Q11–Q12 — its own picker: one card per chapter, one long answer each
    for i, (src, qs) in enumerate(group_by(d['litCloze'][1]['questions'], lambda q: q['src']).items(), 1):
        units = cloze_units(qs)
        sets.append({'id': f'lit-q11-c{i}', 'name': src, 'group': 'Q11–Q12 · Long Answers',
                     'sub': f"{len(units)} long-answer question{'s' if len(units) > 1 else ''}", 'units': units})
    return {'id': 'literature', 'name': 'Literature', 'icon': '📚', 'step': 'Step 4', 'cvar': 'sec4',
            'sub': f'Q8–Q12 · {len(sets)} sets · poems, chapters & answers', 'sets': sets}

DATA['secs'] = [reading_sec(), grammar_sec(), writing_sec(), literature_sec()]

# ---------- NOTES (verbatim reuse of existing content) ----------
# grammar: collect rule statements from why-lines that start with "From notes"
gnotes = []
for topic in d['grammar']:
    rules, seen = [], set()
    for q in topic['questions']:
        why = q.get('why') or ''
        if why.lower().startswith('from notes'):
            rule = re.sub(r'^From notes[^:]*:\s*', '', why, flags=re.I)
            rule = re.sub(r'\s*\(Exam-pattern[^)]*\)', '', rule)
            rule = rule.split(' | ')[0].strip().rstrip('.')
            if rule and rule not in seen:
                seen.add(rule); rules.append(rule)
    gnotes.append({'title': topic['name'], 'lines': [r + '.' for r in rules[:12]]})

# writing: formats derived from the actual templates
wnotes = [
    {'title': 'Notice format (Q4)', 'lines': d['writing']['q4']['order']},
    {'title': 'Formal email format (Q6)', 'lines': ['Date: (date)', 'From: (your email)', 'To: (recipient email)', 'Cc / Bcc: (if needed)', 'Subject: (short & clear)', 'Salutation: Sir/Ma\'am', 'Body: who you are + what you request + why', 'Closing: Thank you, Yours faithfully/sincerely, Name & class']},
    {'title': 'Informal letter format (Q6)', 'lines': ['Your address & date (top)', 'Salutation: Dear …,', 'Body: greeting → news/purpose → closing line', 'Yours lovingly / With love,', 'Name']},
    {'title': 'Diary entry format (Q5)', 'lines': ['Date & time (top)', 'Dear Diary,', 'What happened + how you felt', 'Name (at the end)']},
    {'title': 'Story completion (Q5)', 'lines': ['Give the story a title', 'Use the given cue as the opening', 'Middle: what happens next (keep it connected)', 'End: a clear, satisfying close']},
    {'title': 'Essay & Article (Q7)', 'lines': ['Title', 'Introduction: what & why it matters', 'Body: 2–3 paragraphs, one idea each', 'Conclusion: takeaway / hope / appeal', 'Word limit as asked (~120–150)']},
]

# literature: poem & prose reference lists (from the extracts themselves)
poems, sources = [], []
for e in d['litExtracts'][0]:
    if e['title'] and e['title'] not in poems: poems.append(e['title'])
for e in d['litExtracts'][1]:
    if e['title'] and e['title'] not in sources: sources.append(e['title'])

lnotes = [
    {'title': 'Poems to know (Q8)', 'lines': poems},
    {'title': 'Prose chapters to know (Q9)', 'lines': sources},
    {'title': 'How extract questions work', 'text': 'Each extract card shows the poem/prose lines first, then its questions. True/False, MCQ, and identify-the-poet items are all taken from your Q8–Q9 files.'},
    {'title': 'Short & long answers (Q10–Q12)', 'text': 'These build the full model answer blank by blank — after you check, the correct wording is highlighted. The finished sentence is exactly what an examiner wants to read.'},
]

rnotes = [
    {'title': 'Passages in Q1', 'lines': [p['title'] for p in d['reading'][0]]},
    {'title': 'Passages in Q2', 'lines': [p['title'] for p in d['reading'][1]]},
    {'title': 'How reading questions work', 'text': 'Every card shows its passage first (scroll inside the box). MCQs, True/False and one-word answers all come with the line from the passage that justifies the answer — read it after every check.'},
]

DATA['notes'] = {'reading': rnotes, 'grammar': gnotes, 'writing': wnotes, 'literature': lnotes}

# ---------- RICH NOTES (distilled from the C07 markdown book, build_notes.py) ----------
try:
    rich = json.load(open('c7-notes.json', encoding='utf8'))
    DATA['notes']['grammar'] = rich.get('grammar', gnotes)
    DATA['notes']['writing'] = rich.get('writing', wnotes)
    # keep the 4 short intro cards, then the full chapter cards
    DATA['notes']['literature'] = lnotes + rich.get('literature', [])
    print('rich notes merged:', {k: len(v) for k, v in rich.items()})
except FileNotFoundError:
    print('c7-notes.json not found - using generated notes only')

# counts sanity
tot = sum(len(s['units']) for sec in DATA['secs'] for s in sec['sets'])
print('total units:', tot)
for sec in DATA['secs']:
    print(sec['id'], sum(len(s['units']) for s in sec['sets']), 'units in', len(sec['sets']), 'sets')

payload = json.dumps(DATA, ensure_ascii=False)
why_hi = json.load(open('c7-why-hi.json', encoding='utf8'))
why_hi_payload = json.dumps(why_hi, ensure_ascii=False)
# avoid closing the <script> tag
payload = payload.replace('</', '<\\/')
why_hi_payload = why_hi_payload.replace('</', '<\\/')
out = tpl.replace('/*__DATA__*/', 'var DATA = ' + payload + ';\nvar WHY_HI = ' + why_hi_payload + ';')
out_path = sys.argv[1] if len(sys.argv) > 1 else 'Class7-English-Revision.html'
open(out_path, 'w', encoding='utf8').write(out)
import os
print('written', out_path, os.path.getsize(out_path), 'bytes')
