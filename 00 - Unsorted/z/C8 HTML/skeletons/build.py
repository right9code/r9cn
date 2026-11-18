#!/usr/bin/env python3
"""Build the self-contained Class 8 English revision app."""
import json, os, re, sys

BASE=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(BASE,'c8-data.json'),encoding='utf8'))
tpl=open(os.path.join(BASE,'c8-app-template.html'),encoding='utf8').read()
DATA={'secs':[],'notes':{}}

GRAMMAR_TIPS = {
    'g01': ('A sentence part has a job: the subject does or is something; an object receives the action; a complement describes or renames the subject/object; an adverbial tells when, where or how.', 'वाक्य के हर भाग का काम होता है: subject काम करता है या उसकी स्थिति बताता है; object पर काम होता है; complement subject/object का वर्णन या नाम बताता है; adverbial समय, जगह या ढंग बताता है।'),
    'g15': ('A modal shows advice, duty, permission, ability or possibility. The clue in the sentence helps choose one: should = advice, must = necessity, may/might = possibility. Use the base verb after a modal.', 'Modal सलाह, ज़िम्मेदारी, अनुमति, क्षमता या संभावना बताता है। वाक्य का संकेत सही modal चुनने में मदद करता है: should = सलाह, must = ज़रूरत, may/might = संभावना। Modal के बाद मूल क्रिया आती है।'),
    'g02': ('A noun names a person, place, thing or idea. A group is collective (a swarm); a feeling or idea is abstract (freedom); a particular name is proper (Subarnarekha River).', 'संज्ञा किसी व्यक्ति, जगह, वस्तु या विचार का नाम होती है। समूह collective (a swarm), भावना/विचार abstract (freedom), और खास नाम proper noun (Subarnarekha River) है।'),
    'g17': ('A to-infinitive is to + verb (to learn). After a modal, let, and had better, use the base verb without to. An -ing form is a gerund when it works like a noun, and a participle when it describes a noun or adds an action.', 'to-infinitive में to + क्रिया आती है (to learn)। Modal, let और had better के बाद to के बिना मूल क्रिया आती है। -ing रूप संज्ञा का काम करे तो gerund, और संज्ञा का वर्णन करे या अतिरिक्त काम बताए तो participle होता है।'),
    'g08': ('A determiner comes before a noun to point it out or tell which/how many/how much/whose. Use the for a particular thing or a whole class; use a/an for one nonspecific thing; use no article for plural things in general.', 'Determiner संज्ञा से पहले आकर बताता है कि कौन-सी, कितनी या किसकी चीज़ है। किसी खास चीज़ या पूरी जाति के लिए the, एक अनिश्चित चीज़ के लिए a/an, और सामान्य plural nouns से पहले कोई article नहीं लगाएँ।'),
    'g13': ('Perfect tense uses have/has/had + past participle. Use present perfect for a past action linked to now, past perfect for the earlier of two past actions, and future perfect for an action finished before a future time. Continuous adds been + verb-ing for duration.', 'Perfect tense में have/has/had + past participle आता है। वर्तमान से जुड़े काम के लिए present perfect, दो बीती घटनाओं में पहले वाले के लिए past perfect, और भविष्य के समय से पहले पूरे काम के लिए future perfect प्रयोग करें। अवधि बताने के लिए been + verb-ing जोड़ें।'),
    'g19': ('In active voice, the subject does the action. In passive voice, the subject receives it. Passive form = be + past participle; keep the tense by changing be (is done, was done, will be done).', 'Active voice में subject काम करता है। Passive voice में subject पर काम होता है। Passive रूप = be + past participle; tense के अनुसार be बदलता है (is done, was done, will be done)।'),
    'g18': ('Ask “what?” or “whom?” after the verb. If there is an answer, that is the object and the verb is transitive. If there is no object, it is intransitive. A complement describes or renames a subject/object.', 'क्रिया के बाद “क्या?” या “किसे?” पूछें। उत्तर मिले तो वह object है और क्रिया transitive है। Object न मिले तो intransitive है। Complement subject/object का वर्णन करता या दूसरा नाम बताता है।'),
    'g05': ('An adjective describes a noun or pronoun. Quality tells what kind, quantity tells how much/many, demonstrative points out, possessive shows whose, and interrogative asks which.', 'विशेषण संज्ञा या सर्वनाम का वर्णन करता है। Quality बताता है कैसा, quantity बताता है कितना/कितने, demonstrative इशारा करता है, possessive बताता है किसका, और interrogative पूछता है कौन-सा।'),
}

def reading_sec():
    sets=[]
    for fi, passages in enumerate(d['reading']):
        for pi,p in enumerate(passages):
            passage={'title':p['title'],'paras':p['paras']}
            if p.get('table'): passage['table']=p['table']
            units=[]
            for q in p['questions']:
                base={'passage':passage,'why':q.get('why')}
                if q['t']=='mcq': units.append({**base,'kind':'mcq','q':q['q'],'options':q['opts'],'answer':q['a'],'chip':'Reading · MCQ'})
                elif q['t']=='tf':
                    a=q['a']; ans=(0 if a else 1) if isinstance(a,bool) else int(a)
                    units.append({**base,'kind':'mcq','q':q['q'],'options':['True','False'],'answer':ans,'chip':'Reading · True/False'})
                elif q['t']=='text': units.append({**base,'kind':'text','q':q['q'],'parts':[{'label':x.get('label',''),'a':x['a']} for x in q['parts']]})
            sets.append({'id':f'reading-q{fi+1}-p{pi+1}','name':f'Q{fi+1} · {p["title"]}','group':f'Q{fi+1} · '+('Reading Passages'),'sub':f'{len(units)} questions on this passage','units':units})
    return {'id':'reading','name':'Reading Skill','icon':'📖','step':'Step 1','cvar':'sec1','sub':'Q1–Q2 · 10 passages','sets':sets}

def clean_grammar_why(why):
    why=why or ''
    why=re.sub(r'^Notes answer:\\s*','',why,flags=re.I)
    return why.strip()

def grammar_sec():
    sets=[]
    for t in d['grammar']:
        units=[]
        for q in t['questions']:
            why=clean_grammar_why(q.get('why'))
            if q['type']=='text':
                ans=q['answer'] if isinstance(q['answer'],list) else [q['answer']]
                units.append({'kind':'text','q':q['prompt'],'parts':[{'label':'','a':ans}],
                              'why':why,'grammar':True,'correct':str(ans[0]),'tip':{'en':GRAMMAR_TIPS[t['id']][0],'hi':GRAMMAR_TIPS[t['id']][1]},'chip':'Grammar · '+q.get('src','')})
                continue
            opts=q['options']; ans=q['answer']
            idx=ans if isinstance(ans,int) else (opts.index(ans) if ans in opts else 0)
            units.append({'kind':'mcq','q':q['prompt'],'options':opts,'answer':idx,'why':why,
                          'grammar':True,'correct':opts[idx],'tip':{'en':GRAMMAR_TIPS[t['id']][0],'hi':GRAMMAR_TIPS[t['id']][1]},'chip':'Grammar · '+q.get('src','')})
        sets.append({'id':'grammar-'+t['id'],'name':t['title'],'group':'Q3–Q4 · Grammar Topics','sub':f'{len(units)} practice questions','units':units})
    return {'id':'grammar','name':'Grammar','icon':'🧩','step':'Step 2','cvar':'sec3','sub':f'Q3–Q4 · {len(sets)} grammar topics','sets':sets}

def writing_sec():
    sets=[]
    qlabels=['Q5 · Notice & Story Completion','Q6 · Formal Email','Q7 · Essay & Article','Q8 · Informal Letter & Invitation']
    for qi,groups in enumerate(d['writing']):
        for si,g in enumerate(groups):
            units=[]
            if g.get('sequence'):
                units.append({'kind':'seq','q':g['sequence']['title'],'items':g['sequence']['items'],'why':'Follow the standard format order.'})
            for task in g['questions']:
                fmt={'noticeQs':'notice','storyQs':'story','principalQs':'email','teacherQs':'email',
                     'essayQs':'essay','articleQs':'article','letterQs':'letter','inviteQs':'letter'}.get(g['id'],'')
                units.append({'kind':'builder','title':task.get('title',''),'scenario':task.get('scenario',''),'cue':task.get('cue',''),'format':fmt,
                              'template':task['template'],'blanks':task['blanks'],
                              'bank':task['bank'],'grade':{k:v['answer'] for k,v in task['blanks'].items()}})
            sid=f'writing-q{qi+5}-{si+1}'
            sets.append({'id':sid,'name':g['label'],'group':qlabels[qi],
                         'sub':f'{len(g["questions"])} model tasks'+(' + format order' if g.get('sequence') else ''),'units':units})
    return {'id':'writing','name':'Writing Skills','icon':'✍️','step':'Step 3','cvar':'sec2','sub':'Q5–Q8 · 8 writing task sets','sets':sets}

def mcq_units(questions, passage=None, chip='Literature · MCQ'):
    out=[]
    for q in questions:
        if q.get('type')=='fill' or q.get('parts'):
            parts=[];grade={};bank=[]
            for pi,p in enumerate(q['parts']):
                if isinstance(p,dict):
                    key='b'+str(pi);parts.append({'key':key,'blank':True});grade[key]=p['answer'];bank.extend(p['tiles'])
            out.append({'kind':'cloze','q':q.get('q','Identify the poem and the poet.'),'parts':parts,'grade':grade,'bank':list(dict.fromkeys(bank)),'why':q.get('why'),'passage':passage,'src':q.get('src')})
        else:
            ans=q.get('answer',0)
            if isinstance(ans,bool): ans=0 if ans else 1
            out.append({'kind':'mcq','q':q['q'],'options':q['options'],'answer':ans,'why':q.get('why'),'passage':passage,'chip':chip})
    return out

def answer_builder(q):
    parts=[];grade={};bank=[];blank_i=0
    for p in q['parts']:
        if isinstance(p,list):
            key='b'+str(blank_i);blank_i+=1
            parts.append({'key':key,'blank':True}); grade[key]=p[p[-1]]
            bank.extend(p[:-1])
        else: parts.append({'text':p})
    return {'kind':'cloze','q':q['q'],'parts':parts,'grade':grade,'bank':list(dict.fromkeys(bank)),
            'why':q.get('why'),'src':q.get('src')}

def literature_sec():
    sets=[]
    def grouped(items,key):
        out={}
        for x in items: out.setdefault(key(x),[]).append(x)
        return out
    for i,(title,extracts) in enumerate(grouped(d['literature']['poemExtracts'],lambda e:e.get('poem','Poem')).items(),1):
        units=[]
        for e in extracts:
            p={'title':e.get('poem') or title,'paras':e.get('text',[])}
            units.extend(mcq_units(e['questions'],p))
        sets.append({'id':f'lit-q9-poem-{i}','name':title,'group':'Q9 · Poem Extracts','sub':f'{len(extracts)} extracts · {len(units)} questions','units':units})
    for i,(title,extracts) in enumerate(grouped(d['literature']['proseExtracts'],lambda e:e.get('source','Prose')).items(),1):
        units=[]
        for e in extracts:
            p={'title':e.get('source') or title,'paras':e.get('text',[])}
            units.extend(mcq_units(e['questions'],p))
        sets.append({'id':f'lit-q10-prose-{i}','name':title,'group':'Q10 · Prose Extracts','sub':f'{len(extracts)} extracts · {len(units)} questions','units':units})
    for tab,label in [('prose','Prose'),('poetry','Poetry')]:
        questions=[q for q in d['literature']['shortAnswers'] if q.get('tab')==tab]
        for i,(title,qs) in enumerate(grouped(questions,lambda q:q.get('src','Literature')).items(),1):
            units=[answer_builder(q) for q in qs]
            sets.append({'id':f'lit-q11-{tab}-{i}','name':title,'group':f'Q11 · Short Answers · {label}','sub':f'{len(units)} short-answer questions','units':units})
    for qi,questions in enumerate(d['literature']['longAnswers'],12):
        tab='Prose' if qi==12 else 'Poetry'
        for i,(title,qs) in enumerate(grouped(questions,lambda q:q.get('src','Literature')).items(),1):
            units=[answer_builder(q) for q in qs]
            sets.append({'id':f'lit-q{qi}-{i}','name':title,'group':f'Q{qi} · Long Answers · {tab}','sub':f'{len(units)} long-answer questions','units':units})
    return {'id':'literature','name':'Literature','icon':'📚','step':'Step 4','cvar':'sec4','sub':f'Q9–Q13 · {len(sets)} poem/chapter sets','sets':sets}

DATA['secs']=[reading_sec(),grammar_sec(),writing_sec(),literature_sec()]
# Lightweight section notes; rich Markdown notes are merged when available.
DATA['notes']={s['id']:[] for s in DATA['secs']}
for sec in DATA['secs']:
    DATA['notes'][sec['id']]=[{'title':x['name'],'text':x['sub']} for x in sec['sets']]
try:
    rich=json.load(open(os.path.join(BASE,'c8-notes.json'),encoding='utf8'))
    for k,v in rich.items(): DATA['notes'][k]=v
    print('rich notes merged:',{k:len(v) for k,v in rich.items()})
except FileNotFoundError: print('No rich notes JSON: using set overview notes.')

total=sum(len(x['units']) for sec in DATA['secs'] for x in sec['sets'])
for sec in DATA['secs']: print(sec['id'],sum(len(x['units']) for x in sec['sets']),'units in',len(sec['sets']),'sets')
print('total units:',total)
payload=json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')
why_hi=json.load(open(os.path.join(BASE,'c8-why-hi.json'),encoding='utf8'))
why_hi_payload=json.dumps(why_hi,ensure_ascii=False).replace('</','<\\/')
out=tpl.replace('/*__DATA__*/','var DATA = '+payload+';\nvar WHY_HI = '+why_hi_payload+';')
path=sys.argv[1] if len(sys.argv)>1 else os.path.join(BASE,'..','Class8-English-Revision.html')
with open(path,'w',encoding='utf8') as f:f.write(out)
print('written',path,os.path.getsize(path),'bytes')
