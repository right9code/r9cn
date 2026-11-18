#!/usr/bin/env python3
"""Convert C08 study-note Markdown files into collapsible HTML note cards."""
import json,os,re
import markdown
BASE=os.path.dirname(os.path.abspath(__file__))
SRC='/home/right9zzz/Z/r9AE/C08'
FILES={
 'grammar':[
  'LANGUAGE/Grammar/C08 - G - 01 - THE SENTENCE.md','LANGUAGE/Grammar/C08 - G - 15 - MODALS.md','LANGUAGE/Grammar/C08 - G - 02 - NOUNS.md','LANGUAGE/Grammar/C08 - G - 17 - NON-FINITE VERBS.md','LANGUAGE/Grammar/C08 - G - 08 - DETERMINERS.md','LANGUAGE/Grammar/C08 - G - 13 - PERFECT AND PERFECT CONTINUOUS TENSES.md','LANGUAGE/Grammar/C08 - G - 19 - ACTIVE AND PASSIVE VOICE.md','LANGUAGE/Grammar/C08 - G - 18 - TRANSITIVE AND INTRANSITIVE VERBS.md','LANGUAGE/Grammar/C08 - G - 05 - ADJECTIVES.md'],
 'writing':[
  'LANGUAGE/Writing/C08 - W - 16 - NOTICE WRITING.md','LANGUAGE/Writing/C08 - W - 34 - NARRATIVE WRITING.md','LANGUAGE/Writing/C08 - W - 23 - EMAIL WRITING.md','LANGUAGE/Writing/C08 - W - 06 - ESSAY WRITING.md','LANGUAGE/Writing/C08 - W - 27 - ARTICLE WRITING.md','LANGUAGE/Writing/C08 - W - 25 - INFORMAL LETTER.md','LANGUAGE/Writing/C08 - W - 24 - INFORMAL INVITATION LETTER.md'],
 'literature':[
  'LITERATURE/Prose/C08 - 01 - THE WIT THAT WON HEARTS.md','LITERATURE/Poetry/C08 - 02 - A CONCRETE EXAMPLE - POETRY.md','LITERATURE/Prose/C08 - 07 - THE CASE OF THE FIFTH WORD.md','LITERATURE/Poetry/C08 - 05 - SOMEBODYS MOTHER - POETRY.md','LITERATURE/Prose/C08 - 09 - SPECTACULAR WONDERS.md','LITERATURE/Poetry/C08 - 08 - THE MAGIC BRUSH OF DREAMS - POETRY.md','LITERATURE/Prose/C08 - 10 - THE CHERRY TREE.md','LITERATURE/Prose/C08 - 12 - WAITING FOR THE RAIN.md','LITERATURE/Poetry/C08 - 11 - HARVEST HYMN - POETRY.md','LITERATURE/Prose/C08 - 13 - FEATHERED FRIEND.md','LITERATURE/Prose/C08 - 15 - BIBHA CHOWDHURI THE BEAM OF LIGHT THAT LIT THE PATH FOR WOMEN IN INDIAN SCIENCE.md']}
EXTS=['tables','fenced_code','nl2br','sane_lists']
SMALL={'and','the','of','in','to','a','an'}
def title_of(text, fallback):
 m=re.search(r'^#\s+(.+?)\s*$',text,re.M)
 t=(m.group(1) if m else fallback).strip()
 if t==t.upper() and any(c.isalpha() for c in t):
  words=t.title().split();t=' '.join(w if i==0 or w.lower() not in SMALL else w.lower() for i,w in enumerate(words))
 return t
def main():
 notes={k:[] for k in FILES}
 for group,files in FILES.items():
  for rel in files:
   p=os.path.join(SRC,rel)
   if not os.path.exists(p): print('MISSING',rel);continue
   text=open(p,encoding='utf8').read(); title=title_of(text,os.path.basename(p))
   html=markdown.markdown(text,extensions=EXTS)
   html=re.sub(r'^\s*<h1>.*?</h1>','',html,count=1,flags=re.S)
   notes[group].append({'title':title,'html':html.strip()})
 out=os.path.join(BASE,'c8-notes.json')
 json.dump(notes,open(out,'w',encoding='utf8'),ensure_ascii=False)
 print('cards:',{k:len(v) for k,v in notes.items()},'| written',out,os.path.getsize(out),'bytes')
if __name__=='__main__':main()
