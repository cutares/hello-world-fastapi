const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('../../source/node_modules/typescript');
const file = fs.readFileSync(require('node:path').join(__dirname, '../../source/src/core/player/player.ts'), 'utf8');
const source = file.slice(file.indexOf('export const playSystemQueueItem ='));
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
function fixture() {
  let selected;
  const state = { playInfo: { playerListId: 'main' }, playMusicInfo: { listId: 'main', musicInfo: { id: 'cur' } }, tempPlayList: [{ listId: 'temp', musicInfo: { id: 't1' } }, { listId: 'temp', musicInfo: { id: 't2' } }] };
  const actions = [];
  const module = { exports: {} };
  vm.runInNewContext(compiled, { module, exports: module.exports, getSystemQueueSelection: () => selected, playerState: state,
    getList: () => [{ id: 'target' }], syncSystemQueue: () => actions.push('sync'), play: () => actions.push('resume'),
    handlePlay: async() => actions.push('play'), settingState: { setting: { 'player.isAutoCleanPlayedList': true } },
    clearPlayedList: () => actions.push('clearHistory'), removeTempPlayList: index => state.tempPlayList.splice(index, 1),
    setPlayMusicInfo: (...args) => actions.push(args),
  });
  return { state, actions, api: module.exports, select: s => { selected = s } };
}
(async() => {
  let f = fixture(); await f.api.playSystemQueueItem('unknown'); assert.equal(f.actions.length, 0);
  f.select({ kind: 'list', listId: 'main', musicInfo: { id: 'target' } }); await f.api.playSystemQueueItem('id');
  assert.deepEqual(f.actions, [['main', { id: 'target' }, false], 'clearHistory', 'play']); assert.equal(f.state.tempPlayList.length, 2);
  f = fixture(); f.select({ kind: 'list', listId: 'old', musicInfo: { id: 'target' } }); await f.api.playSystemQueueItem('id'); assert.equal(f.actions.length, 0);
  f = fixture(); f.select({ kind: 'list', listId: 'main', musicInfo: { id: 'removed' } }); await f.api.playSystemQueueItem('id'); assert.deepEqual(f.actions, ['sync']);
  f = fixture(); f.select({ kind: 'temp', listId: 'temp', musicInfo: { id: 't2' } }); await f.api.playSystemQueueItem('id');
  assert.equal(f.state.tempPlayList.length, 1); assert.equal(f.state.tempPlayList[0].musicInfo.id, 't1'); assert.deepEqual(f.actions, [['temp', { id: 't2' }, true], 'play']);
  f = fixture(); f.select({ kind: 'current', listId: 'main', musicInfo: { id: 'cur' } }); await f.api.playSystemQueueItem('id'); assert.deepEqual(f.actions, ['resume']);
  console.log('PASS: unknown IDs, normal selection, history parity, pending-temp preservation, stale list/item rejection, temp selection, current resume.');
})().catch(error => { console.error(error); process.exitCode = 1 });
