
/* ================= THEME ENGINE ================= */
var SCHEMES = ['sage','lavender','sand'];
var NAMES = { sage:'Sage', lavender:'Lavender', sand:'Sandstone' };
var scheme = 'sage', mode = 'auto';
var mq = window.matchMedia('(prefers-color-scheme: light)');
function applyTheme() {
  document.body.dataset.scheme = scheme;
  document.body.dataset.mode = mode === 'auto' ? (mq.matches ? 'light' : 'dark') : mode;
  document.getElementById('scheme-btn').textContent = '🎨 ' + NAMES[scheme];
  document.getElementById('mode-btn').textContent =
    mode === 'auto' ? '🌗 Auto' : mode === 'light' ? '☀️ Light' : '🌙 Dark';
  try { localStorage.setItem('c7-theme', JSON.stringify({ scheme: scheme, mode: mode })); } catch (e) {}
}
function cycleScheme() { scheme = SCHEMES[(SCHEMES.indexOf(scheme) + 1) % SCHEMES.length]; applyTheme(); }
function cycleMode() { mode = mode === 'auto' ? 'light' : mode === 'light' ? 'dark' : 'auto'; applyTheme(); }
mq.addEventListener('change', function () { if (mode === 'auto') applyTheme(); });
try { var th = JSON.parse(localStorage.getItem('c7-theme') || 'null'); if (th && SCHEMES.indexOf(th.scheme) >= 0) { scheme = th.scheme; mode = th.mode || 'auto'; } } catch (e) {}
applyTheme();

/* ================= HELPERS ================= */
function $(id) { return document.getElementById(id); }
function esc(s) { return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function norm(s) { return String(s || '').trim().toLowerCase().replace(/\s+/g,' '); }
function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; }
function shuffle(a) { var x = a.slice(); for (var i = x.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = x[i]; x[i] = x[j]; x[j] = t; } return x; }

/* ================= PROGRESS STORE ================= */
var STORE_KEY = 'c7-progress-v1';
var progress = {};
try { progress = JSON.parse(localStorage.getItem(STORE_KEY) || '{}') || {}; } catch (e) { progress = {}; }
function saveProgress() { try { localStorage.setItem(STORE_KEY, JSON.stringify(progress)); } catch (e) {} }
function markUnit(key, correct) { progress[key] = correct ? 1 : 0; saveProgress(); }
function unitKey(sec, setId, i) { return sec + '|' + setId + '|' + i; }
function setStats(sec, setId, total) {
  var att = 0, ok = 0;
  for (var i = 0; i < total; i++) { var v = progress[unitKey(sec, setId, i)]; if (v !== undefined) { att++; if (v === 1) ok++; } }
  return { att: att, ok: ok, total: total };
}

/* ================= STUDENT NAME ================= */
var STUDENT_KEY = 'c7-student';
var student = '';
try { student = String(localStorage.getItem(STUDENT_KEY) || '').trim(); } catch (e) {}
var nameGate = false;   /* true only while the first-launch hard gate is up */

function openNameModal(first) {
  nameGate = !!first;
  $('name-title').textContent = first ? "What's your name?" : 'Your name';
  $('name-hint').textContent = first
    ? 'Your name shows on your progress line and your score cards. It is saved only on this device.'
    : 'Tap your name on the home screen any time to change it. Your scores are never touched.';
  $('name-input').value = student;
  $('name-reset').style.display = first ? 'none' : '';
  $('name-modal').style.display = 'flex';
  setTimeout(function () { $('name-input').focus(); }, 60);
}
function closeNameModal() { if (nameGate) return; $('name-modal').style.display = 'none'; }
function saveName() {
  var v = $('name-input').value.trim().replace(/\s+/g, ' ').slice(0, 24);
  if (!v) { $('name-input').focus(); return; }
  student = v;
  try { localStorage.setItem(STUDENT_KEY, v); } catch (e) {}
  nameGate = false;
  $('name-modal').style.display = 'none';
  renderHome();
}
function resetMyScore() {
  if (!confirm('Reset ALL of your scores? Your name will be kept.')) return;
  progress = {}; saveProgress();
  nameGate = false;
  $('name-modal').style.display = 'none';
  renderHome();
}
function resetEverything() {
  if (!confirm('Reset everything? All of your scores AND your name will be erased, then you will type your name again.')) return;
  progress = {}; saveProgress();
  try { localStorage.removeItem(STUDENT_KEY); } catch (e) {}
  student = '';
  renderHome();
  openNameModal(true);   /* hard gate again — type your name */
}

/* ================= VIEWS ================= */
var curSec = null, curSet = null, curI = 0, answered = false;
var dock = $('nextbar');

function show(id) {
  var p = document.querySelectorAll('.pane');
  for (var i = 0; i < p.length; i++) p[i].classList.remove('active');
  $(id).classList.add('active');
  window.scrollTo(0, 0);
}
function goHome() {
  $('head-title').textContent = 'Class 7 · English Revision';
  dock.classList.remove('show');
  renderHome(); show('v-home');
}
function renderHome() {
  var path = $('path'); path.innerHTML = '';
  DATA.secs.forEach(function (sec, si) {
    var total = 0, att = 0, ok = 0;
    sec.sets.forEach(function (set) { var st = setStats(sec.id, set.id, set.units.length); total += st.total; att += st.att; ok += st.ok; });
    var pct = total ? Math.round(att / total * 100) : 0;
    var node = el('div', 'node');
    node.innerHTML =
      '<div class="node-dot" style="border-color:var(--' + sec.cvar + ')">' + sec.icon + '</div>' +
      '<div class="node-body">' +
        '<div class="node-step">' + sec.step + '</div>' +
        '<div class="node-name">' + esc(sec.name) + '</div>' +
        '<div class="node-sub">' + sec.sub + '</div>' +
        '<div class="node-bar"><div class="node-bar-fill" style="width:' + pct + '%;background:var(--' + sec.cvar + ')"></div></div>' +
        '<div class="node-actions">' +
          '<button class="node-btn practice" onclick="openPick(\'' + sec.id + '\')">Practice</button>' +
          '<button class="node-btn" onclick="openNotes(\'' + sec.id + '\')">Notes</button>' +
        '</div></div>';
    path.appendChild(node);
  });
  var T = 0, A = 0, O = 0;
  DATA.secs.forEach(function (sec) { sec.sets.forEach(function (set) { var st = setStats(sec.id, set.id, set.units.length); T += st.total; A += st.att; O += st.ok; }); });
  var hi = $('hero-hi');
  if (student) {
    hi.innerHTML = esc('Hi ' + student + ' — ' + A + ' of ' + T + ' attempted') +
      ' <span class="rename-hint" title="Tap to rename">✎</span>';
  } else {
    hi.innerHTML = 'Annual exam revision — open &amp; free';
  }
  hi.onclick = function () { openNameModal(false); };
  $('hero-sub').textContent = T ? (O + ' correct so far · Progress saves on this phone.')
                               : 'Practice one question at a time. Your progress saves on this phone.';
}

/* ---------- pick ---------- */
function openPick(secId) {
  var sec = DATA.secs.filter(function (s) { return s.id === secId; })[0];
  curSec = secId;
  $('head-title').textContent = sec.name;
  $('pick-title').textContent = sec.name + ' — choose a set';
  var list = $('pick-list'); list.innerHTML = '';
  var group = null, num = 0;
  sec.sets.forEach(function (set) {
    if (set.group !== group) {
      group = set.group; num = 0;
      if (group) list.appendChild(el('div', 'pick-group', esc(group)));
    }
    num++;
    var st = setStats(secId, set.id, set.units.length);
    var pct = st.total ? Math.round(st.att / st.total * 100) : 0;
    var card = el('div', 'set-card');
    card.innerHTML =
      '<div class="set-num">' + num + '</div>' +
      '<div class="set-body">' +
        '<div class="set-name">' + esc(set.name) + '</div>' +
        '<div class="set-sub">' + esc(set.sub || (set.units.length + ' questions')) + '</div>' +
        '<div class="set-bar"><div class="set-bar-fill" style="width:' + pct + '%;background:var(--' + sec.cvar + ')"></div></div>' +
      '</div>' +
      '<div class="set-stat">' + (st.att ? (st.att + '/' + st.total + ' · ' + st.ok + ' ✓') : 'start') + '</div>' +
      (st.att ? '<button class="reset-btn" title="Reset this set" onclick="event.stopPropagation();resetSet(\'' + secId + '\',\'' + set.id + '\')">↺</button>' : '');
    card.onclick = function () { startSet(secId, set.id); };
    list.appendChild(card);
  });
  show('v-pick');
}
function resetSet(secId, setId) {
  if (!confirm('Reset progress for this set?')) return;
  var sec = DATA.secs.filter(function (s) { return s.id === secId; })[0];
  var set = sec.sets.filter(function (s) { return s.id === setId; })[0];
  for (var i = 0; i < set.units.length; i++) delete progress[unitKey(secId, setId, i)];
  saveProgress(); openPick(secId);
}

/* ---------- practice ---------- */
function startSet(secId, setId) {
  var sec = DATA.secs.filter(function (s) { return s.id === secId; })[0];
  var set = sec.sets.filter(function (s) { return s.id === setId; })[0];
  curSec = secId; curSet = set; curI = 0;
  for (var i = 0; i < set.units.length; i++) { if (progress[unitKey(secId, setId, i)] === undefined) { curI = i; break; } }
  $('head-title').textContent = set.name;
  $('pr-sec').textContent = sec.name + ' · ' + set.name;
  $('pr-sec').style.color = 'var(--' + sec.cvar + ')';
  $('pr-fill').style.background = 'var(--' + sec.cvar + ')';
  show('v-practice'); dock.classList.add('show');
  renderUnit();
}
function exitPractice() {
  if (curSet) openPick(curSec); else goHome();
}
function nextUnit() {
  if (!answered) return;
  if (curI < curSet.units.length - 1) { curI++; renderUnit(); }
  else renderDone();
}
function renderUnit() {
  answered = false;
  var sec = DATA.secs.filter(function (s) { return s.id === curSec; })[0];
  var u = curSet.units[curI];
  $('pr-count').textContent = 'Question ' + (curI + 1) + ' of ' + curSet.units.length;
  $('pr-fill').style.width = ((curI) / curSet.units.length * 100) + '%';
  var st = setStats(curSec, curSet.id, curSet.units.length);
  $('pr-count').textContent = 'Question ' + (curI + 1) + ' of ' + curSet.units.length + ' · ' + st.ok + ' ✓';
  $('big-btn').textContent = curI === curSet.units.length - 1 ? 'Finish ✓' : 'Next →';
  $('big-btn').disabled = true;
  var card = $('q-card'); card.innerHTML = '';
  var r = RENDERERS[u.kind];
  r(card, u, sec);
  card.scrollIntoView({ block: 'start' });
}

/* finish card */
function renderDone() {
  var st = setStats(curSec, curSet.id, curSet.units.length);
  var card = $('q-card');
  card.innerHTML =
    '<div class="done-card">' +
      '<div class="big">' + (st.ok === st.total ? '🏆' : st.ok >= st.total * 0.7 ? '🎉' : '💪') + '</div>' +
      '<h2>' + esc(student || 'You') + ' scored ' + st.ok + '/' + st.total + '</h2>' +
      '<div class="done-score">' + (st.total ? Math.round(st.ok / st.total * 100) : 0) + '%</div>' +
      '<p>' + (st.ok === st.total ? 'Perfect — this set is exam-ready.' : 'Redo any time; a fresh attempt replaces the old score.') + '</p>' +
      '<div class="done-actions">' +
        '<button onclick="startSet(\'' + curSec + '\',\'' + curSet.id + '\')">Practice again</button>' +
        '<button class="prime" onclick="openPick(\'' + curSec + '\')">More sets</button>' +
      '</div></div>';
  $('pr-count').textContent = 'Done';
  $('pr-fill').style.width = '100%';
  $('big-btn').disabled = true;
}

/* ================= QUESTION RENDERERS ================= */
var RENDERERS = {};

function addFb(card, ok, why) {
  var fb = el('div', 'fb ' + (ok ? 'win' : 'lose'));
  fb.innerHTML = (ok ? '✓ Correct. ' : '✗ ') + (why ? esc(why) : '');
  card.appendChild(fb);
}

/* MCQ + True/False */
RENDERERS.mcq = function (card, u) {
  if (u.passage) addPassage(card, u.passage);
  card.appendChild(el('div', 'chip', u.chip || 'MCQ'));
  card.appendChild(el('div', 'q-text', u.q));
  var wrap = el('div');
  u.options.forEach(function (optText, i) {
    var o = el('div', 'opt');
    o.innerHTML = '<div class="opt-key">' + 'ABCD'[i] + '</div><div>' + optText + '</div>';
    o.onclick = function () {
      if (answered) return; answered = true;
      var kids = wrap.children;
      for (var j = 0; j < kids.length; j++) {
        kids[j].classList.add('off');
        if (j === u.answer) kids[j].className = 'opt right';
      }
      o.classList.remove('off');
      if (i === u.answer) { o.className = 'opt right'; addFb(card, true, u.why); }
      else { o.className = 'opt miss'; addFb(card, false, u.why); }
      markUnit(unitKey(curSec, curSet.id, curI), i === u.answer ? 1 : 0);
      $('big-btn').disabled = false;
    };
    wrap.appendChild(o);
  });
  card.appendChild(wrap);
};

/* typed answer(s) */
RENDERERS.text = function (card, u) {
  if (u.passage) addPassage(card, u.passage);
  card.appendChild(el('div', 'chip', 'Type the answer'));
  card.appendChild(el('div', 'q-text', u.q));
  var parts = u.parts || [{ label: '', a: [].concat(u.answers || u.answer) }];
  var inputs = [];
  parts.forEach(function (p) {
    if (p.label) card.appendChild(el('span', 'text-label', esc(p.label)));
    var inp = el('input', 'text-in');
    inp.autocapitalize = 'off'; inp.autocomplete = 'off'; inp.spellcheck = false;
    card.appendChild(inp); inputs.push(inp);
  });
  var btn = el('button', 'check-btn', 'Check');
  btn.onclick = function () {
    if (answered) return;
    var allOk = true, anyFilled = false;
    inputs.forEach(function (inp, i) {
      var v = inp.value.trim();
      if (v) anyFilled = true;
      var ok = false;
      var acc = parts[i].a || String(parts[i].answer || '').split('|');
      for (var k = 0; k < acc.length; k++) if (norm(v) === norm(acc[k])) ok = true;
      inp.classList.add(ok ? 'right' : 'miss');
      inp.disabled = true;
      if (!ok) allOk = false;
    });
    if (!anyFilled) return;
    answered = true;
    addFb(card, allOk, u.why);
    markUnit(unitKey(curSec, curSet.id, curI), allOk ? 1 : 0);
    btn.disabled = true;
    $('big-btn').disabled = false;
  };
  card.appendChild(btn);
};

/* passage / extract box */
function addPassage(card, p) {
  var box = el('div', 'passage');
  var h = p.title ? '<b>' + esc(p.title) + '</b><br>' : '';
  box.innerHTML = h + p.paras.map(function (t) { return '<p style="margin:.35rem 0">' + t + '</p>'; }).join('');
  card.appendChild(box);
}

/* tiles fill (literature identify) */
RENDERERS.fill = function (card, u) {
  if (u.passage) addPassage(card, u.passage);
  card.appendChild(el('div', 'chip', 'Tap tiles to fill'));
  card.appendChild(el('div', 'q-text', u.q));
  var slots = [], state = [];
  var slotWrap = el('div');
  u.parts.forEach(function (p, pi) {
    state.push(null);
    var row = el('div', 'part-row');
    row.innerHTML = '<span class="part-label">' + esc(p.label) + '</span>';
    var s = el('button', 'slot', '&nbsp;');
    s.onclick = function () {
      if (answered) return;
      if (state[pi] !== null) { /* clear: return tile */ used[state[pi]] = false; tiles[state[pi]].classList.remove('used'); state[pi] = null; s.innerHTML = '&nbsp;'; }
      else { if (selSlot) selSlot.classList.remove('sel'); selSlot = s; s.classList.add('sel'); }
    };
    slots.push(s); row.appendChild(s); slotWrap.appendChild(row);
  });
  var selSlot = null;
  var tileTexts = []; u.parts.forEach(function (p) { p.tiles.forEach(function (t) { tileTexts.push(t); }); });
  var pool = shuffle(tileTexts);
  var used = pool.map(function () { return false; });
  var tiles = [];
  var tileWrap = el('div', 'tiles');
  pool.forEach(function (t, ti) {
    var b = el('button', 'tile', esc(t));
    b.onclick = function () {
      if (answered) return;
      var target = -1;
      if (selSlot) { for (var i = 0; i < slots.length; i++) if (slots[i] === selSlot) target = i; selSlot.classList.remove('sel'); selSlot = null; }
      else { for (var i = 0; i < state.length; i++) if (state[i] === null) { target = i; break; } }
      if (target === -1) return;
      if (state[target] !== null) { used[state[target]] = false; tiles[state[target]].classList.remove('used'); }
      state[target] = ti; used[ti] = true; tiles[ti].classList.add('used');
      slots[target].textContent = t;
    };
    tiles.push(b); tileWrap.appendChild(b);
  });
  var btn = el('button', 'check-btn', 'Check');
  btn.onclick = function () {
    if (answered) return;
    var allOk = true;
    u.parts.forEach(function (p, pi) {
      if (state[pi] === null) { allOk = false; slots[pi].classList.add('miss'); return; }
      var ok = norm(pool[state[pi]]) === norm(p.answer);
      slots[pi].classList.add(ok ? 'right' : 'miss');
      if (!ok) allOk = false;
    });
    answered = true;
    addFb(card, allOk, u.why);
    markUnit(unitKey(curSec, curSet.id, curI), allOk ? 1 : 0);
    btn.disabled = true; $('big-btn').disabled = false;
  };
  card.appendChild(slotWrap); card.appendChild(tileWrap); card.appendChild(btn);
};

/* cloze (tap blank, tap option) & writing builder share this engine */
function makeBlankEngine(card, cfg) {
  /* cfg: { lines: [{html}] or custom, blanks: {key:{answer, label?}}, bank: [strings], grade: map key->answerText, onGrade } */
  var blanks = {};       /* key -> button */
  var values = {};       /* key -> chosen text */
  var selKey = null;
  var wrap = el('div');

  function blankBtn(key, hint) {
    var b = el('button', 'cblank', '&nbsp;______&nbsp;');
    b.dataset.key = key;
    b.onclick = function () {
      if (cfg.locked) return;
      if (values[key]) { /* clear */ cfg.bankUsed(values[key], false); delete values[key]; b.innerHTML = '&nbsp;______&nbsp;'; b.classList.remove('right','miss'); }
      else { if (selKey && blanks[selKey]) blanks[selKey].classList.remove('sel'); selKey = key; b.classList.add('sel'); }
    };
    blanks[key] = b; return b;
  }

  var bankWrap = null;
  if (cfg.bank && cfg.bank.length) {
    bankWrap = el('div', 'bank');
    var usedMap = {};
    cfg.bank.forEach(function (item) {
      var chip = el('button', 'tile', esc(item));
      chip.onclick = function () {
        if (cfg.locked) return;
        var key = selKey;
        if (!key) { for (var k in blanks) if (!values[k]) { key = k; break; } }
        if (!key) return;
        if (values[key]) cfg.bankUsed(values[key], false);
        values[key] = item; usedMap[item] = true;
        blanks[key].textContent = item; blanks[key].classList.remove('sel'); blanks[key].classList.remove('right','miss');
        selKey = null;
        cfg.bankUsed(item, true);
      };
      chip.dataset.item = item;
      bankWrap.appendChild(chip);
    });
  }
  cfg.bankUsed = function (item, isUsed) {
    var chips = bankWrap ? bankWrap.children : [];
    for (var i = 0; i < chips.length; i++) if (chips[i].dataset.item === item) chips[i].classList.toggle('used', isUsed);
  };

  cfg.build(wrap, blankBtn);   /* renderer fills lines using blankBtn(key) */

  var btn = null;
  if (cfg.check) {
    btn = el('button', 'check-btn', 'Check');
    btn.onclick = function () {
      if (answered || cfg.locked) return;
      var allOk = true, anyEmpty = false;
      for (var k in blanks) {
        if (!values[k]) { anyEmpty = true; blanks[k].classList.add('miss'); continue; }
        var ok = norm(values[k]) === norm(cfg.grade[k]);
        blanks[k].classList.add(ok ? 'right' : 'miss');
        if (!ok) allOk = false;
      }
      if (anyEmpty) { /* allow check anyway but fail empties */ }
      answered = true; cfg.locked = true;
      addFb(card, allOk, cfg.why);
      markUnit(unitKey(curSec, curSet.id, curI), allOk ? 1 : 0);
      btn.disabled = true; $('big-btn').disabled = false;
    };
  }
  card.appendChild(wrap);
  if (bankWrap) card.appendChild(bankWrap);
  if (btn) card.appendChild(btn);
}

/* cloze literature (Q10 / Q11-12) */
RENDERERS.cloze = function (card, u) {
  card.appendChild(el('div', 'chip', esc(u.src ? u.src + ' · fill the blanks' : 'Fill the blanks')));
  card.appendChild(el('div', 'q-text', u.q));
  makeBlankEngine(card, {
    bank: u.bank,
    grade: u.grade,
    why: u.why,
    check: true,
    build: function (wrap, blankBtn) {
      var line = el('div', 'c-line');
      u.parts.forEach(function (p) {
        if (p.text !== undefined) line.appendChild(document.createTextNode(p.text));
        else line.appendChild(blankBtn(p.key));
      });
      wrap.appendChild(line);
    }
  });
};

/* writing builder (Q4–Q7) */
RENDERERS.builder = function (card, u) {
  card.appendChild(el('div', 'chip', 'Writing task · tap & fill'));
  var sc = el('div', 'scenario', '<b>Scenario:</b> ' + esc(u.scenario));
  card.appendChild(sc);
  makeBlankEngine(card, {
    bank: u.bank,
    grade: u.grade,
    check: true,
    build: function (wrap, blankBtn) {
      u.template.forEach(function (t) {
        if (t.hr) { wrap.appendChild(el('hr', 'w-hr')); return; }
        if (t.cls === 'ttl') {
          var line = el('div', 'w-ttl');
          t.parts.forEach(function (f) { if (typeof f === 'string') line.appendChild(document.createTextNode(f)); else if (f.k) line.appendChild(blankBtn(f.k)); });
          wrap.appendChild(line); return;
        }
        var div = el('div', 'w-line');
        if (t.type) {
          if (t.type === 'label') { div.className = 'w-line w-label'; div.textContent = 'NOTICE'; }
          else if (t.type === 'contact') { div.className = 'w-line w-fixed'; div.textContent = 'For further details, contact the undersigned.'; }
          else if (t.type === 'sign') { div.className = 'w-line w-right w-fixed'; div.textContent = '(Signature)'; }
          else if (t.type === 'inst') { div.className = 'w-line w-center'; div.appendChild(blankBtn(t.key)); }
          else if (t.type === 'date') { div.className = 'w-line w-fixed'; div.appendChild(document.createTextNode('Date: ')); div.appendChild(blankBtn(t.key)); }
          else if (t.type === 'heading') { div.className = 'w-line w-center'; div.appendChild(blankBtn(t.key)); }
          else if (t.type === 'name') { div.className = 'w-line w-right'; div.appendChild(document.createTextNode('Name: ')); div.appendChild(blankBtn(t.key)); }
          else if (t.type === 'desig') { div.className = 'w-line w-right'; div.appendChild(document.createTextNode('Designation: ')); div.appendChild(blankBtn(t.key)); }
          else if (t.type === 'body' && t.parts) {
            t.parts.forEach(function (f) {
              if (typeof f === 'string') div.appendChild(document.createTextNode(f));
              else if (f.k) div.appendChild(blankBtn(f.k));
            });
          }
        } else if (t.parts) {
          t.parts.forEach(function (f) {
            if (typeof f === 'string') div.appendChild(document.createTextNode(f));
            else if (f.k) div.appendChild(blankBtn(f.k));
          });
          if (t.tag === 'p') div.classList.add('w-line');
        }
        wrap.appendChild(div);
      });
    }
  });
};

/* sequence (notice format) */
RENDERERS.seq = function (card, u) {
  card.appendChild(el('div', 'chip', 'Arrange in correct order'));
  card.appendChild(el('div', 'q-text', esc(u.q)));
  var order = shuffle(u.items.map(function (_, i) { return i; }));
  var list = el('div');
  function render() {
    list.innerHTML = '';
    order.forEach(function (itemIdx, pos) {
      var row = el('div', 'seq-item');
      row.innerHTML = '<span class="seq-num">' + (pos + 1) + '.</span><span class="seq-text">' + esc(u.items[itemIdx]) + '</span>';
      var up = el('button', 'seq-btn', '▲'); up.onclick = function () { if (pos > 0 && !answered) { var t = order[pos - 1]; order[pos - 1] = order[pos]; order[pos] = t; render(); } };
      var dn = el('button', 'seq-btn', '▼'); dn.onclick = function () { if (pos < order.length - 1 && !answered) { var t = order[pos + 1]; order[pos + 1] = order[pos]; order[pos] = t; render(); } };
      row.appendChild(up); row.appendChild(dn);
      list.appendChild(row);
    });
  }
  render();
  var btn = el('button', 'check-btn', 'Check');
  btn.onclick = function () {
    if (answered) return;
    answered = true;
    var allOk = true;
    order.forEach(function (itemIdx, pos) {
      var ok = itemIdx === pos;
      list.children[pos].classList.add(ok ? 'right' : 'miss');
      if (!ok) allOk = false;
    });
    addFb(card, allOk, u.why);
    markUnit(unitKey(curSec, curSet.id, curI), allOk ? 1 : 0);
    btn.disabled = true; $('big-btn').disabled = false;
  };
  card.appendChild(list); card.appendChild(btn);
};

/* ================= NOTES ================= */
function openNotes(secId) {
  var prevPane = document.querySelector('.pane.active').id;
  var sec = DATA.secs.filter(function (s) { return s.id === secId; })[0];
  $('head-title').textContent = sec.name + ' · Notes';
  $('notes-title').textContent = sec.name + ' — Notes';
  var body = $('notes-body'); body.innerHTML = '';
  DATA.notes[secId].forEach(function (n) {
    if (n.html) {
      /* rich markdown card — collapsible since chapters are long */
      var d = el('details', 'note-card');
      d.innerHTML = '<summary>' + esc(n.title) + '</summary><div class="note-rich">' + n.html + '</div>';
      body.appendChild(d);
      return;
    }
    var c = el('div', 'note-card');
    var h = '<h3>' + esc(n.title) + '</h3>';
    if (n.lines) h += '<ul>' + n.lines.map(function (l) { return '<li>' + l + '</li>'; }).join('') + '</ul>';
    if (n.text) h += '<p>' + n.text + '</p>';
    c.innerHTML = h; body.appendChild(c);
  });
  notesReturn = prevPane === 'v-practice' ? 'practice' : (prevPane === 'v-pick' ? 'pick' : 'home');
  show('v-notes');
}
var notesReturn = 'home';
function notesBack() {
  if (notesReturn === 'practice' && curSet) { show('v-practice'); }
  else if (notesReturn === 'pick' && curSec) { openPick(curSec); }
  else goHome();
}

/* ================= INIT ================= */
goHome();
if (!student) openNameModal(true);   /* hard gate: no name, no app */
