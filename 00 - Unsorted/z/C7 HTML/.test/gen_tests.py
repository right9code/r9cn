#!/usr/bin/env python3
"""Regenerate the headless smoke-test copies from the freshly built app."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'Class7-English-Revision.html'), encoding='utf8').read()

# ---- T2: seeded student name + progress, drives the new features ----
seed = """try {
  localStorage.setItem('c7-student', 'Rahul');
  var p = {};
  ['grammar|grammar-nouns|0','grammar|grammar-nouns|1','grammar|grammar-nouns|2'].forEach(function(k){p[k]=1;});
  p['grammar|grammar-nouns|3']=0;
  p['reading|reading-q1-p1|0']=1;
  localStorage.setItem('c7-progress-v1', JSON.stringify(p));
} catch(e) { document.title = 'SEED-FAIL ' + e; }
/* ================= THEME ENGINE ================= */"""
assert src.count('/* ================= THEME ENGINE ================= */') == 1
t2 = src.replace('/* ================= THEME ENGINE ================= */', seed, 1)

driver = """
<script>
window.confirm = function(){ return true; };
var R = [];
function ok(n, c) { R.push((c ? 'PASS ' : 'FAIL ') + n); }
window.addEventListener('load', function () {
  try {
    ok('name modal closed after saved name', $('name-modal').style.display === 'none');
    ok('hero greets student with attempted total',
       /^Hi Rahul — \\d+ of 473 attempted/.test($('hero-hi').textContent.trim()));
    ok('hero shows correct count', /4 correct so far/.test($('hero-sub').textContent));

    openPick('literature');
    var groups = [].map.call(document.querySelectorAll('#pick-list .pick-group'), function (e) { return e.textContent; });
    ok('literature has 4 group headers', groups.length === 4 &&
       groups[0].indexOf('Q8') === 0 && groups[1].indexOf('Q9') === 0 &&
       groups[2].indexOf('Q10') === 0 && groups[3].indexOf('Q11') === 0);
    var cards = document.querySelectorAll('#pick-list .set-card');
    ok('literature has 31 cards', cards.length === 31);
    ok('number chip present on card 1', cards[0].querySelector('.set-num').textContent === '1');
    ok('number chip restarts per group', cards[4].querySelector('.set-num').textContent === '1');
    ok('mini progress bar present', !!cards[0].querySelector('.set-bar-fill'));
    var names = [].map.call(document.querySelectorAll('#pick-list .set-name'), function (e) { return e.textContent; });
    ok('Q8 poem cards (4)', names.indexOf('Paper Boats — Rabindranath Tagore') >= 0 &&
       names.indexOf('My Dear Soldiers — A.P.J. Abdul Kalam') >= 0);
    ok('Q9 prose titles recovered', names.indexOf('The Tunnel — Ruskin Bond') >= 0 &&
       names.indexOf('Say the Right Thing') >= 0 && names.indexOf('My Brother’s Great Invention — Anita Rau Badami') >= 0);
    ok('Q10 chapter cards (11)', names.indexOf('Rani Abbakka') >= 0 && names.indexOf('The Day the River Spoke') >= 0);
    ok('Q11-12 own picker card', names.indexOf('Your literature reader') >= 0);
    ok('extract count pluralised', /1 extract \\u00b7 5 questions/.test(cards[0].textContent));
    ok('pick title updated', $('pick-title').textContent.indexOf('Literature') === 0);

    openPick('reading');
    var rcards = document.querySelectorAll('#pick-list .set-card');
    ok('reading still one set per passage (10)', rcards.length === 10 &&
       document.querySelectorAll('#pick-list .pick-group').length === 0);
    ok('reading sub preserved', rcards[0].textContent.indexOf('questions on this passage') >= 0);
    ok('reading chips 1..10', rcards[9].querySelector('.set-num').textContent === '10');

    startSet('reading', 'reading-q2-p1');
    var ptab = document.querySelector('#q-card .passage table');
    ok('Q2 passage renders its table', !!ptab);
    ok('table has 4 data rows', ptab && ptab.querySelectorAll('tbody tr').length === 4);
    ok('table caption shown', ptab && /Water saved in one month during the campaign/.test(ptab.querySelector('caption').textContent));
    ok('table header cells', ptab && ptab.querySelectorAll('th').length === 2 &&
       /litres/.test(ptab.textContent) && /Water-saving action/.test(ptab.textContent));
    startSet('reading', 'reading-q1-p1');
    ok('Q1 passage (no table) still renders', !!document.querySelector('#q-card .passage') &&
       !document.querySelector('#q-card .passage table'));

    openPick('grammar');
    var gcards = document.querySelectorAll('#pick-list .set-card');
    ok('grammar 10 sets', gcards.length === 10);
    ok('grammar att/total stat', gcards[0].querySelector('.set-stat').textContent === '4/20 · 3 ✓');
    ok('grammar reset button', !!gcards[0].querySelector('.reset-btn'));

    openPick('writing');
    ok('writing 7 sets (its picker)', document.querySelectorAll('#pick-list .set-card').length === 7);

    startSet('grammar', DATA.secs[1].sets[0].id);
    ok('practice header shows set name', $('head-title').textContent.length > 0);
    answered = true; renderDone();
    var h2 = document.querySelector('.done-card h2');
    ok('finish card names student: "Rahul scored x/20"', h2 && /^Rahul scored \\d+\\/20$/.test(h2.textContent));

    openNameModal(false);
    ok('rename modal opens', $('name-modal').style.display === 'flex' && $('name-reset').style.display !== 'none');
    ok('rename prefilled', $('name-input').value === 'Rahul');
    closeNameModal();
    ok('rename modal closes on backdrop', $('name-modal').style.display === 'none');
    $('name-input').value = 'Rahul S';
    saveName();
    ok('rename saves', localStorage.getItem('c7-student') === 'Rahul S' &&
       $('hero-hi').textContent.indexOf('Hi Rahul S') === 0);

    resetMyScore();
    ok('reset my score clears progress', Object.keys(JSON.parse(localStorage.getItem('c7-progress-v1'))).length === 0);
    ok('reset my score keeps name', localStorage.getItem('c7-student') === 'Rahul S');

    ok('home has a reset-everything button', !!document.querySelector('.reset-all') &&
       document.querySelector('.reset-all').textContent.indexOf('Reset everything') > 0);
    document.querySelector('.reset-all').click();
    ok('reset everything reopens the name gate', $('name-modal').style.display === 'flex' &&
       $('name-title').textContent === "What's your name?" && $('name-reset').style.display === 'none');
    ok('reset everything erases the name', !localStorage.getItem('c7-student'));
    ok('reset everything clears all scores', Object.keys(JSON.parse(localStorage.getItem('c7-progress-v1') || '{}')).length === 0);
    ok('hero reset to placeholder while gated', $('hero-hi').textContent.indexOf('Annual exam revision') === 0);
    ok('gate blocks the home screen again', closeNameModal() === undefined && $('name-modal').style.display === 'flex');
  } catch (e) { R.push('FAIL exception: ' + e.message); }
  var box = document.createElement('div');
  box.id = 'test-results';
  box.style.cssText = 'position:fixed;left:0;top:0;background:#fff;color:#000;font:12px monospace;z-index:999;padding:4px';
  box.innerHTML = R.join(' ||| ');
  document.body.appendChild(box);
});
</script>
</body>"""
assert t2.count('</body>') == 1
t2 = t2.replace('</body>', driver, 1)

# ---- T3: first-launch hard gate (own origin => fresh localStorage) ----
gate = """
<script>
var R = [];
function ok(n, c) { R.push((c ? 'PASS ' : 'FAIL ') + n); }
window.addEventListener('load', function () {
  try {
    ok('gate visible on first launch', $('name-modal').style.display === 'flex');
    ok('gate title asks for a name', $('name-title').textContent === "What's your name?");
    ok('no reset button during first launch', $('name-reset').style.display === 'none');
    ok('no name stored yet', !localStorage.getItem('c7-student'));
    closeNameModal();
    ok('backdrop click cannot dismiss the gate', $('name-modal').style.display === 'flex');
    document.getElementById('name-modal').click();
    ok('modal click cannot dismiss the gate', $('name-modal').style.display === 'flex');
    $('name-input').value = '   ';
    saveName();
    ok('blank name is rejected', $('name-modal').style.display === 'flex' && !localStorage.getItem('c7-student'));
    $('name-input').value = 'Aarav';
    saveName();
    ok('saving a name closes the gate', $('name-modal').style.display === 'none');
    ok('name stored', localStorage.getItem('c7-student') === 'Aarav');
    ok('hero updates after gating', $('hero-hi').textContent.indexOf('Hi Aarav — 0 of 473 attempted') === 0);
  } catch (e) { R.push('FAIL exception: ' + e.message); }
  var box = document.createElement('div'); box.id = 'test-results';
  box.style.cssText = 'position:fixed;left:0;top:0;background:#fff;color:#000;font:12px monospace;z-index:999;padding:4px';
  box.innerHTML = R.join(' ||| '); document.body.appendChild(box);
});
</script>
</body>"""
assert src.count('</body>') == 1
t3 = src.replace('</body>', gate, 1)

# ---- T4: screenshot of the literature picker ----
shot = """<script>window.addEventListener('load',function(){openPick('literature');});</script></body>"""
t4 = src.replace('/* ================= THEME ENGINE ================= */',
                 "try{localStorage.setItem('c7-student','Rahul');}catch(e){}\n/* ================= THEME ENGINE ================= */", 1)
t4 = t4.replace('</body>', shot, 1)

base = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(base, 't2-named.html'), 'w', encoding='utf8').write(t2)
os.makedirs(os.path.join(base, 'gate'), exist_ok=True)
open(os.path.join(base, 'gate', 't3-gate.html'), 'w', encoding='utf8').write(t3)
open(os.path.join(base, 'gate', 't4-shot.html'), 'w', encoding='utf8').write(t4)
print('generated t2-named.html, gate/t3-gate.html, gate/t4-shot.html')
