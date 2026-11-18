#!/usr/bin/env node
// Extract authored question data arrays from the standalone C8 source pages.
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const root = path.join(__dirname, '..', 'sources');
function source(file) { return fs.readFileSync(path.join(root, file), 'utf8'); }
function expression(src, marker, open) {
  const m = src.indexOf(marker);
  if (m < 0) throw new Error('Missing ' + marker);
  const start = src.indexOf(open, m + marker.length);
  let depth=0, quote='', escape=false;
  for (let i=start; i<src.length; i++) {
    const c=src[i];
    if (quote) { if (escape) escape=false; else if (c==='\\') escape=true; else if (c===quote) quote=''; continue; }
    if (c==='\'' || c==='"' || c==='`') { quote=c; continue; }
    if (c===open) depth++;
    if (c===(open==='['?']':'}')) { depth--; if (!depth) return src.slice(start,i+1); }
  }
  throw new Error('Unclosed expression for '+marker);
}
function evaluate(expr, ctx={}) { return vm.runInNewContext('('+expr+')',ctx,{timeout:5000}); }
function array(src, name, ctx={}) { return evaluate(expression(src, 'var '+name, '['),ctx); }
function sequence(src, panel) {
  const marker=`makeSequenceCard(${panel},`;
  const at=src.indexOf(marker);
  if(at<0) throw new Error('Missing sequence '+panel);
  const args=src.slice(at+marker.length);
  const title=args.match(/^\s*'((?:\\.|[^'])*)'/);
  const pos=args.indexOf('[',title ? title[0].length : 0);
  const arr=evaluate(expression(args.slice(pos), '', '['));
  return {title:title ? title[1] : '', items:arr};
}
function extractWriting(file, vars, labels, panels) {
  const src=source(file);
  return vars.map((v,i)=>({id:v,label:labels[i],sequence:panels[i] ? sequence(src,panels[i]) : null,questions:array(src,v)}));
}

const reading=[array(source('class8-reading-q1.html'),'PASSAGES'),array(source('class8-reading-q2.html'),'PASSAGES')];
const grammar=array(source('class8-grammar-q3-4.html'),'TOPICS');
const q9src=source('class8-literature-q9.html');
const poems=evaluate(expression(q9src,'var POEMS','{'));
const identify=function(poemName,poetName,poemTiles,poetTiles,why){return {type:'fill',q:'Identify the poem and the poet.',why,parts:[{label:'Poem',answer:poemName,tiles:poemTiles},{label:'Poet',answer:poetName,tiles:poetTiles}]};};
const litPoems=array(q9src,'extracts',{POEMS:poems,identify});
for(const e of litPoems) e.poem=e.poem || e.source || e.label || '';
const tf=function(q,answer,why){return {q:'State whether the following statement is true or false: '+q,options:['True','False'],answer:answer,why:why};};
const litProse=array(source('class8-literature-q10.html'),'extracts',{tf});
for(const e of litProse) e.source=e.source || e.label || '';
const literature={poemExtracts:litPoems,proseExtracts:litProse,
  shortAnswers:array(source('class8-literature-q11.html'),'QUESTIONS'),
  longAnswers:[array(source('class8-literature-q12.html'),'QUESTIONS'),array(source('class8-literature-q13.html'),'QUESTIONS')]};
const writing=[
  extractWriting('class8-writing-q5.html',['noticeQs','storyQs'],['Notice','Story Completion'],['panelNotice','panelStory']),
  extractWriting('class8-writing-q6.html',['principalQs','teacherQs'],['Formal Email · Principal','Formal Email · Teacher'],['panelPrincipal',null]),
  extractWriting('class8-writing-q7.html',['essayQs','articleQs'],['Essay','Article'],['panelEssay','panelArticle']),
  extractWriting('class8-writing-q8.html',['letterQs','inviteQs'],['Informal Letter','Invitation Letter'],['panelLetter','panelInvite'])
];
const data={reading,grammar,literature,writing};
fs.writeFileSync(path.join(__dirname,'c8-data.json'),JSON.stringify(data,null,2));
console.log('reading passages:',reading.map(a=>a.length));
console.log('grammar topics:',grammar.length,grammar.map(t=>[t.title,t.questions.length]));
console.log('poem/prose extracts:',litPoems.length,litProse.length);
console.log('literature answer sets:',literature.shortAnswers.length,literature.longAnswers.map(a=>a.length));
console.log('writing task groups:',writing.map(g=>g.map(s=>[s.label,s.questions.length])));
