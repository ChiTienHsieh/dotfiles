#!/usr/bin/env node
// Regression tests for diagram-editor dirty-code protection (A09).
// Runs the editor script in a Node VM with a minimal DOM stub — no browser.

import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, '..');
const EDITOR_HTML = path.join(
  REPO_ROOT,
  'skills/shared/diagram-editor/assets/editor.html',
);

function loadEditor() {
  const html = fs.readFileSync(EDITOR_HTML, 'utf8');
  const match = html.match(/<script>([\s\S]*?)<\/script>/);
  if (!match) throw new Error('editor.html: embedded <script> not found');
  const js = match[1];

  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) {
      elements.set(id, {
        id,
        value: '',
        hidden: false,
        textContent: '',
        style: {},
        dataset: {},
        classList: { add() {}, remove() {}, toggle() {} },
        events: {},
        addEventListener(n, fn) { this.events[n] = fn; },
        querySelectorAll() { return []; },
        getBoundingClientRect() {
          return { width: 1200, height: 800, left: 0, top: 0 };
        },
        setAttribute() {},
        appendChild() {},
        remove() {},
        focus() {},
        select() {},
        getContext() {
          return {
            font: '',
            measureText(s) { return { width: String(s).length * 8 }; },
          };
        },
      });
    }
    return elements.get(id);
  }

  const sandbox = {
    console,
    document: {
      getElementById: element,
      createElement(tag) {
        const el = element(`anon-${tag}-${Math.random()}`);
        return el;
      },
      querySelectorAll() { return []; },
      addEventListener() {},
      body: { appendChild() {} },
    },
    window: { addEventListener() {} },
    localStorage: { getItem() { return null; }, setItem() {} },
    setTimeout() {},
    confirm() { return true; },
    navigator: { clipboard: { writeText: async () => {} } },
  };

  vm.createContext(sandbox);
  vm.runInContext(js, sandbox);

  // Replace toast with a recorder (no DOM side effects needed for these tests).
  vm.runInContext(
    'var __toasts = []; toast = function(msg, warn) { __toasts.push({ msg: String(msg), warn: !!warn }); };',
    sandbox,
  );

  return sandbox;
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function setDirtyPending(s, marker = 'UNAPPLIED') {
  vm.runInContext(
    [
      '__toasts = [];',
      `codeEl.value = "flowchart TD\\n${marker}[Do not lose this edit]\\n";`,
      'setDirty(true);',
    ].join('\n'),
    s,
  );
}

function snapshotPending(s) {
  return vm.runInContext(
    `({
      dirty: codeDirty,
      code: codeEl.value,
      nodeCount: doc.nodes.length,
      edgeCount: doc.edges.length,
      dir: doc.dir,
      selDir: document.getElementById('selDir').value,
      selection: selection && JSON.parse(JSON.stringify(selection)),
      posKeys: [...positions.keys()].sort().join(','),
      firstId: doc.nodes[0] && doc.nodes[0].id,
      toast: (__toasts || []).map(t => t.msg).join(' | '),
    })`,
    s,
  );
}

function run() {
  const results = [];

  // Built-in round-trip self-test must still pass.
  {
    const s = loadEditor();
    const pass = vm.runInContext('runRoundTripTest().pass', s);
    assert(pass === true, 'runRoundTripTest().pass should be true');
    results.push('ok roundtrip');
  }

  // A09: mutateSel must refuse while dirty (low-level guard).
  {
    const s = loadEditor();
    vm.runInContext(
      [
        '__toasts = [];',
        'const pending = "flowchart TD\\nUNAPPLIED[Do not lose this edit]\\n";',
        'codeEl.value = pending;',
        'setDirty(true);',
        'selection = { kind: "node", id: doc.nodes[0].id };',
        'const mutated = mutateSel(n => { n.comment = "GUI comment change"; });',
        'globalThis.__a09 = {',
        '  mutated,',
        '  afterDirty: codeDirty,',
        '  stillHasUnapplied: codeEl.value.includes("UNAPPLIED"),',
        '  commentChanged: !!(doc.nodes[0].comment && doc.nodes[0].comment.includes("GUI comment")),',
        '  toast: (__toasts || []).map(t => t.msg).join(" | "),',
        '};',
      ].join('\n'),
      s,
    );
    const a09 = vm.runInContext('globalThis.__a09', s);
    assert(a09.mutated === false, 'mutateSel should refuse while dirty');
    assert(a09.afterDirty === true, 'codeDirty must remain true');
    assert(a09.stillHasUnapplied === true, 'pending UNAPPLIED text must survive');
    assert(a09.commentChanged === false, 'doc must not mutate before the guard');
    assert(/未套用/.test(a09.toast), `expected dirty toast, got: ${a09.toast}`);
    results.push('ok gui-mutation-blocked');
  }

  // A09: createNodeAt handler — no phantom positions/selection on reject.
  {
    const s = loadEditor();
    vm.runInContext(
      [
        'const id0 = doc.nodes[0].id;',
        'positions.set(id0, { x: 10, y: 20 });',
        'selection = { kind: "node", id: id0 };',
      ].join('\n'),
      s,
    );
    setDirtyPending(s, 'UNAPPLIED_NEW');
    const before = snapshotPending(s);
    const created = vm.runInContext('createNodeAt(100, 200, "rect", true)', s);
    const after = snapshotPending(s);
    assert(created === null, 'createNodeAt must return null while dirty');
    assert(after.dirty === true, 'createNodeAt reject keeps dirty');
    assert(after.code.includes('UNAPPLIED_NEW'), 'createNodeAt must not wipe buffer');
    assert(after.nodeCount === before.nodeCount, 'no node added on reject');
    assert(after.selection && after.selection.id === before.firstId, 'selection must stay on real node');
    assert(after.posKeys === before.posKeys, 'positions must not gain phantom ids');
    assert(/未套用/.test(after.toast), `createNodeAt toast missing: ${after.toast}`);
    results.push('ok createNodeAt-blocked');
  }

  // A09: duplicateSelection handler — no phantom copy on reject.
  {
    const s = loadEditor();
    vm.runInContext(
      [
        'const id0 = doc.nodes[0].id;',
        'positions.set(id0, { x: 10, y: 20 });',
        'selection = { kind: "node", id: id0 };',
      ].join('\n'),
      s,
    );
    setDirtyPending(s, 'UNAPPLIED_DUP');
    const before = snapshotPending(s);
    vm.runInContext('duplicateSelection()', s);
    const after = snapshotPending(s);
    assert(after.nodeCount === before.nodeCount, 'duplicateSelection must not add node');
    assert(after.selection && after.selection.id === before.firstId, 'selection unchanged');
    assert(after.posKeys === before.posKeys, 'no phantom duplicate position');
    assert(after.code.includes('UNAPPLIED_DUP'), 'dup reject keeps buffer');
    assert(/未套用/.test(after.toast), `dup toast missing: ${after.toast}`);
    results.push('ok duplicateSelection-blocked');
  }

  // A09: deleteSelection handler — selection/doc unchanged on reject.
  {
    const s = loadEditor();
    vm.runInContext(
      [
        'const id0 = doc.nodes[0].id;',
        'positions.set(id0, { x: 10, y: 20 });',
        'selection = { kind: "node", id: id0 };',
      ].join('\n'),
      s,
    );
    setDirtyPending(s, 'UNAPPLIED_DEL');
    const before = snapshotPending(s);
    vm.runInContext('deleteSelection()', s);
    const after = snapshotPending(s);
    assert(after.nodeCount === before.nodeCount, 'deleteSelection must not delete');
    assert(after.selection && after.selection.id === before.firstId, 'selection must remain');
    assert(after.code.includes('UNAPPLIED_DEL'), 'delete reject keeps buffer');
    assert(/未套用/.test(after.toast), `delete toast missing: ${after.toast}`);
    results.push('ok deleteSelection-blocked');
  }

  // A09: pId change handler — restore displayed id; no selection/pos rewrite.
  {
    const s = loadEditor();
    vm.runInContext(
      [
        'const id0 = doc.nodes[0].id;',
        'positions.set(id0, { x: 10, y: 20 });',
        'selection = { kind: "node", id: id0 };',
        'renderProps();',
      ].join('\n'),
      s,
    );
    setDirtyPending(s, 'UNAPPLIED_PID');
    vm.runInContext(
      [
        'const el = document.getElementById("pId");',
        'const oldId = doc.nodes[0].id;',
        'el.value = "RenamedId";',
        'el.events.change({ target: el });',
        'globalThis.__pid = {',
        '  oldId,',
        '  docId: doc.nodes[0].id,',
        '  inputValue: el.value,',
        '  selectionId: selection && selection.id,',
        '  hasOldPos: positions.has(oldId),',
        '  hasNewPos: positions.has("RenamedId"),',
        '  stillHasUnapplied: codeEl.value.includes("UNAPPLIED_PID"),',
        '  dirty: codeDirty,',
        '  toast: (__toasts || []).map(t => t.msg).join(" | "),',
        '};',
      ].join('\n'),
      s,
    );
    const p = vm.runInContext('globalThis.__pid', s);
    assert(p.docId === p.oldId, 'pId reject must not rename doc node');
    assert(p.inputValue === p.oldId, 'pId input must be restored from doc');
    assert(p.selectionId === p.oldId, 'selection id unchanged');
    assert(p.hasOldPos === true && p.hasNewPos === false, 'positions must not move to new id');
    assert(p.stillHasUnapplied && p.dirty, 'pId reject keeps pending buffer');
    assert(/未套用/.test(p.toast), `pId toast missing: ${p.toast}`);
    results.push('ok pId-blocked-restored');
  }

  // A09: selDir change handler — restore select display; doc.dir unchanged.
  {
    const s = loadEditor();
    vm.runInContext('document.getElementById("selDir").value = doc.dir;', s);
    setDirtyPending(s, 'UNAPPLIED_DIR');
    vm.runInContext(
      [
        'const dirBefore = doc.dir;',
        'const el = document.getElementById("selDir");',
        'el.value = "LR";',
        'el.events.change({ target: el });',
        'globalThis.__dir = {',
        '  dirBefore,',
        '  docDir: doc.dir,',
        '  selValue: el.value,',
        '  stillHasUnapplied: codeEl.value.includes("UNAPPLIED_DIR"),',
        '  dirty: codeDirty,',
        '  toast: (__toasts || []).map(t => t.msg).join(" | "),',
        '};',
      ].join('\n'),
      s,
    );
    const d = vm.runInContext('globalThis.__dir', s);
    assert(d.docDir === d.dirBefore, 'doc.dir must stay put');
    assert(d.selValue === d.dirBefore, 'selDir display must be restored');
    assert(d.stillHasUnapplied && d.dirty, 'selDir reject keeps buffer');
    assert(/未套用/.test(d.toast), `selDir toast missing: ${d.toast}`);
    results.push('ok selDir-blocked-restored');
  }

  // A09: btnNew handler — positions/selection survive reject.
  {
    const s = loadEditor();
    vm.runInContext(
      [
        'const id0 = doc.nodes[0].id;',
        'positions.set(id0, { x: 10, y: 20 });',
        'selection = { kind: "node", id: id0 };',
      ].join('\n'),
      s,
    );
    setDirtyPending(s, 'UNAPPLIED_BTNNEW');
    s.confirm = () => { throw new Error('dirty New must not ask for confirmation'); };
    const before = snapshotPending(s);
    vm.runInContext('document.getElementById("btnNew").events.click()', s);
    const after = snapshotPending(s);
    assert(after.nodeCount === before.nodeCount, 'btnNew reject must not empty doc');
    assert(after.posKeys === before.posKeys, 'btnNew reject must not clear positions');
    assert(after.selection && after.selection.id === before.firstId, 'btnNew reject keeps selection');
    assert(after.code.includes('UNAPPLIED_BTNNEW'), 'btnNew reject keeps buffer');
    assert(/未套用/.test(after.toast), `btnNew toast missing: ${after.toast}`);
    results.push('ok btnNew-blocked');
  }

  // A09: Undo / Redo must refuse while dirty.
  {
    const s = loadEditor();
    vm.runInContext(
      [
        '__toasts = [];',
        'selection = { kind: "node", id: doc.nodes[0].id };',
        'mutateSel(n => { n.comment = "committed comment"; });',
        'const undoLenBefore = undoStack.length;',
        'codeEl.value = "flowchart TD\\nUNAPPLIED_UNDO[keep me]\\n";',
        'setDirty(true);',
        'const codeBefore = codeEl.value;',
        'undo();',
        'const afterUndo = {',
        '  undoLenAfter: undoStack.length,',
        '  stillHasUnapplied: codeEl.value.includes("UNAPPLIED_UNDO"),',
        '  codeUnchanged: codeEl.value === codeBefore,',
        '  stillDirty: codeDirty,',
        '  toast: (__toasts || []).map(t => t.msg).join(" | "),',
        '};',
        '__toasts = [];',
        'redo();',
        'globalThis.__ur = Object.assign(afterUndo, {',
        '  undoLenBefore,',
        '  redoToast: (__toasts || []).map(t => t.msg).join(" | "),',
        '  stillDirtyAfterRedo: codeDirty,',
        '  stillHasAfterRedo: codeEl.value.includes("UNAPPLIED_UNDO"),',
        '});',
      ].join('\n'),
      s,
    );
    const u = vm.runInContext('globalThis.__ur', s);
    assert(u.undoLenBefore > 0, 'setup: undo stack should have an entry');
    assert(u.undoLenAfter === u.undoLenBefore, 'undo must not pop while dirty');
    assert(u.stillHasUnapplied && u.codeUnchanged && u.stillDirty, 'undo must preserve buffer');
    assert(/未套用/.test(u.toast), `expected dirty undo toast, got: ${u.toast}`);
    assert(/未套用/.test(u.redoToast), `expected dirty redo toast, got: ${u.redoToast}`);
    assert(u.stillDirtyAfterRedo && u.stillHasAfterRedo, 'redo must preserve buffer');
    results.push('ok undo-redo-blocked');
  }

  // A09: after successful apply, real handlers work again.
  {
    const s = loadEditor();
    vm.runInContext(
      [
        '__toasts = [];',
        'codeEl.value = "flowchart TD\\nKeepMe[hello]\\n";',
        'setDirty(true);',
        'applyCode({ quiet: true });',
        'const afterApplyDirty = codeDirty;',
        'const n0 = doc.nodes[0].id;',
        'positions.set(n0, { x: 10, y: 20 });',
        'selection = { kind: "node", id: n0 };',
        'const created = createNodeAt(50, 60, "rect", false);',
        'const dirEl = document.getElementById("selDir");',
        'dirEl.value = "LR";',
        'dirEl.events.change({ target: dirEl });',
        'globalThis.__ok = {',
        '  afterApplyDirty,',
        '  created,',
        '  hasCreated: !!created && doc.nodes.some(n => n.id === created),',
        '  posHasCreated: !!created && positions.has(created),',
        '  dir: doc.dir,',
        '  selDir: dirEl.value,',
        '  dirty: codeDirty,',
        '};',
      ].join('\n'),
      s,
    );
    const ok = vm.runInContext('globalThis.__ok', s);
    assert(ok.afterApplyDirty === false, 'applyCode should clear dirty');
    assert(typeof ok.created === 'string' && ok.created.length > 0, 'createNodeAt works after apply');
    assert(ok.hasCreated && ok.posHasCreated, 'created node and position exist');
    assert(ok.dir === 'LR' && ok.selDir === 'LR', 'selDir works after apply');
    assert(ok.dirty === false, 'successful GUI edits leave code clean');
    results.push('ok apply-then-handlers-work');
  }

  // Copy dirty protection still works (pre-existing contract).
  {
    const s = loadEditor();
    vm.runInContext(
      [
        '__toasts = [];',
        'codeEl.value = "flowchart TD\\nX[y]\\n";',
        'setDirty(true);',
        'document.getElementById("btnCopy").events.click();',
        'globalThis.__copy = {',
        '  toast: (__toasts || []).map(t => t.msg).join(" | "),',
        '  stillDirty: codeDirty,',
        '};',
      ].join('\n'),
      s,
    );
    const c = vm.runInContext('globalThis.__copy', s);
    assert(/未套用/.test(c.toast), `copy dirty guard toast missing: ${c.toast}`);
    assert(c.stillDirty === true, 'copy must not clear dirty');
    results.push('ok copy-dirty-preserved');
  }

  console.log(results.join('\n'));
  console.log(`PASS ${results.length} diagram-editor checks`);
}

try {
  run();
} catch (err) {
  console.error('FAIL', err && err.stack ? err.stack : err);
  process.exit(1);
}
