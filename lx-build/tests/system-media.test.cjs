const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '../../source');
const ts = require(root + '/node_modules/typescript');
const source = fs.readFileSync(root + '/src/plugins/player/systemMedia.ts', 'utf8');
function fixture() {
  const callbacks = {};
  const events = { on: (name, fn) => { (callbacks[name] ||= []).push(fn) } };
  const emit = (name, ...args) => { for (const fn of callbacks[name] || []) fn(...args) };
  const state = { playMusicInfo: { musicInfo: { id: 'a' } }, musicInfo: { id: 'a', lrc: '[00:01.00]A' } };
  let queueContext = state.playMusicInfo; let queueGeneration = Date.now();
  const getGeneration = () => { if (queueContext !== state.playMusicInfo) { queueContext = state.playMusicInfo; queueGeneration++ } return queueGeneration };
  const settings = { setting: { 'player.togglePlayMethod': 'listLoop', 'list.addMusicLocationType': 'bottom' } };
  const calls = []; const modes = []; const favoriteCalls = []; const favorites = []; const otherList = [{ id: 'a' }, { id: 'unrelated' }]; const writes = [];
  const warnings = []; let fail = false; let waitQueue = null; let waitWrite = null;
  const module = { exports: {} };
  const sandbox = { module, exports: module.exports, Date, console: { warn: x => warnings.push(x) }, global: { lx: { playerStatus: { isInitialized: true } }, state_event: events, app_event: events }, require(name) {
    if (name === 'react-native') return { Platform: { OS: 'android' }, DeviceEventEmitter: { addListener: events.on }, NativeModules: { TrackPlayerModule: {
      setSystemFavorite: async(...args) => { favoriteCalls.push(args); return true },
      setSystemRepeatMode: async mode => { modes.push(mode); return true },
      setSystemLyrics: async(...args) => { if (fail) throw Error('SECRET'); calls.push(args); return true },
    } } };
    if (name === '@/store/player/state') return { default: state };
    if (name === '@/store/setting/state') return { default: settings };
    if (name === '@/config/constant') return { LIST_IDS: { LOVE: 'love' } };
    if (name === '@/utils/listManage') return { getListMusics: async id => { assert.equal(id, 'love'); return favorites } };
    if (name === '@/core/list') return {
      addListMusics: async(id, items) => { assert.equal(id, 'love'); writes.push(['add', items.map(x => x.id)]); if (waitWrite) await waitWrite; for (const music of items) if (!favorites.some(x => x.id === music.id)) favorites.push(music); emit('myListMusicUpdate', ['love']) },
      removeListMusics: async(id, ids) => { assert.equal(id, 'love'); writes.push(['remove', ids]); if (waitWrite) await waitWrite; for (let i = favorites.length - 1; i >= 0; i--) if (ids.includes(favorites[i].id)) favorites.splice(i, 1); emit('myListMusicUpdate', ['love']) },
    };
    if (name === '@/core/common') return { updateSetting: values => { Object.assign(settings.setting, values); emit('configUpdated', Object.keys(values), values) } };
    if (name === './systemQueue') return { getSystemMediaGeneration: getGeneration, getCurrentSystemMediaId: () => state.playMusicInfo.musicInfo?.id || '', syncSystemQueue: async() => { if (waitQueue) await waitQueue } };
    throw Error(name);
  } };
  vm.runInNewContext(ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText, sandbox);
  return { api: module.exports, state, settings, calls, modes, favoriteCalls, favorites, otherList, writes, warnings, emit, callbacks, sandbox, setFail: x => { fail = x }, setWait: x => { waitQueue = x }, setWriteWait: x => { waitWrite = x } };
}
const flush = () => new Promise(resolve => setTimeout(resolve, 10));
(async() => {
  // Lyrics may arrive before setup/listeners; initialization must publish retained state.
  const cold = fixture(); cold.sandbox.global.lx.playerStatus.isInitialized = false;
  cold.state.musicInfo.lrc = '[00:03.00]Loaded before player setup';
  await cold.api.syncSystemMedia(); assert.equal(cold.calls.length, 0);
  cold.sandbox.global.lx.playerStatus.isInitialized = true;
  cold.api.initializeSystemMedia(); await cold.api.syncSystemMedia(true);
  assert.equal(cold.calls.at(-1)[2], '[00:03.00]Loaded before player setup');
  // Restored first song: setup publishes empty state, lyric resolves while the
  // native placeholder is paused, then the real engine starts the same context.
  const restored = fixture(); restored.state.musicInfo.lrc = null;
  restored.api.initializeSystemMedia(); await restored.api.syncSystemMedia(true);
  const restoredGeneration = restored.calls.at(-1)[1];
  assert.equal(restored.calls.at(-1)[2], '');
  restored.emit('pause');
  restored.state.musicInfo.lrc = '[00:04.00]Restored first song';
  restored.emit('playerMusicInfoChanged', { ...restored.state.musicInfo });
  restored.emit('lyricUpdated'); await restored.api.syncSystemMedia();
  assert.equal(restored.calls.at(-1)[2], '[00:04.00]Restored first song');
  const published = restored.calls.length;
  restored.emit('play'); await restored.api.syncSystemMedia();
  assert.equal(restored.calls.at(-1)[1], restoredGeneration);
  assert.equal(restored.calls.at(-1)[2], '[00:04.00]Restored first song');
  assert.equal(restored.calls.length, published, 'unchanged JS payload relies on native late-subscriber delivery');
  // The inverse timing, lyric arriving after engine play, must also publish.
  const late = fixture(); late.state.musicInfo.lrc = null;
  late.api.initializeSystemMedia(); await late.api.syncSystemMedia(true);
  late.emit('play'); await late.api.syncSystemMedia();
  late.state.musicInfo.lrc = '[00:05.00]Late first-song lyric';
  late.emit('lyricUpdated'); await late.api.syncSystemMedia();
  assert.equal(late.calls.at(-1)[2], '[00:05.00]Late first-song lyric');
  const f = fixture(); f.api.initializeSystemMedia(); f.api.initializeSystemMedia();
  assert.equal(f.callbacks['remote-play-mode-change'].length, 1); assert.equal(f.callbacks['remote-favorite-change'].length, 1);
  await f.api.syncSystemMedia(true);
  assert.deepEqual(f.modes, [1]); assert.equal(f.calls[0][2], ''); assert.equal(f.calls[1][2], '[00:01.00]A');
  await f.api.syncSystemMedia(); assert.equal(f.calls.length, 2);
  for (const expected of ['singleLoop', 'random', 'listLoop']) { f.emit('remote-play-mode-change'); await flush(); assert.equal(f.settings.setting['player.togglePlayMethod'], expected); }
  for (const special of ['list', 'none']) { f.settings.setting['player.togglePlayMethod'] = special; await f.api.syncSystemMedia(); assert.equal(f.api.getSystemRepeatMode(), 0); }
  assert.equal(f.modes.at(-1), 0);
  const before = f.calls.length; f.emit('pause'); await flush(); assert.equal(f.calls.length, before);
  const engineGeneration = f.calls.at(-1)[1];
  f.emit('stop'); await flush(); assert.equal(f.calls.at(-1)[2], '');
  assert.equal(f.calls.at(-1)[1], engineGeneration, 'stop keeps reusable engine identity');
  f.emit('play'); await flush(); assert.equal(f.calls.at(-1)[2], '[00:01.00]A');
  assert.equal(f.calls.at(-1)[1], engineGeneration);
  f.emit('error'); await flush(); assert.equal(f.calls.at(-1)[2], '');
  assert.equal(f.calls.at(-1)[1], engineGeneration, 'temporary error must not detach native timing');
  f.emit('play'); await flush(); assert.equal(f.calls.at(-1)[2], '[00:01.00]A');
  assert.equal(f.calls.at(-1)[1], engineGeneration, 'same-track recovery retains generation');
  const oldGeneration = f.calls.at(-1)[1];
  f.state.playMusicInfo = { musicInfo: { id: 'b' } }; f.state.musicInfo = { id: 'b', lrc: null }; f.emit('playMusicInfoChanged'); await flush();
  assert.equal(f.calls.at(-1)[0], 'b'); assert.equal(f.calls.at(-1)[2], ''); assert.ok(f.calls.at(-1)[1] > oldGeneration);
  f.state.musicInfo.lrc = '[00:02.00]B'; f.emit('lyricUpdated'); await flush(); assert.equal(f.calls.at(-1)[2], '[00:02.00]B');
  f.state.musicInfo.lrc = 'x'.repeat(65537); f.emit('lyricUpdated'); await flush(); assert.equal(f.calls.at(-1)[2], '');
  f.state.playMusicInfo = { musicInfo: null }; f.state.musicInfo = { id: null, lrc: null }; f.emit('playMusicInfoChanged'); await flush(); assert.equal(f.calls.at(-1)[0], '');
  const count = f.calls.length; await f.api.syncSystemMedia(true); assert.ok(f.calls.length > count);
  const r = fixture(); r.setFail(true); await r.api.syncSystemMedia(); assert.deepEqual(r.warnings, ['System media sync failed']); r.setFail(false); await r.api.syncSystemMedia(); assert.equal(r.calls.at(-1)[2], '[00:01.00]A');
  const race = fixture(); race.api.initializeSystemMedia(); let release; race.setWait(new Promise(resolve => { release = resolve }));
  const pending = race.api.syncSystemMedia(); await flush(); race.state.playMusicInfo = { musicInfo: { id: 'b' } }; race.state.musicInfo = { id: 'b', lrc: '[00:02]B' }; race.emit('playMusicInfoChanged'); release(); race.setWait(null); await pending; await flush(); assert.ok(race.calls.every(x => x[0] === 'b'));
  const heart = fixture(); heart.api.initializeSystemMedia(); await heart.api.syncSystemMedia(true);
  const gen = heart.calls.at(-1)[1]; const event = favorite => ({ id: 'a', generation: gen, favorite });
  assert.equal(heart.favoriteCalls.at(-1)[2], false);
  await heart.api.changeSystemFavorite(event(true)); await heart.api.changeSystemFavorite(event(true));
  assert.equal(heart.favorites.length, 1); assert.equal(heart.favoriteCalls.at(-1)[2], true);
  heart.favorites.push({ id: 'unrelated' });
  await heart.api.changeSystemFavorite(event(false));
  assert.deepEqual(heart.favorites, [{ id: 'unrelated' }]); assert.equal(heart.favoriteCalls.at(-1)[2], false);
  await heart.api.changeSystemFavorite(event(false)); assert.deepEqual(heart.favorites, [{ id: 'unrelated' }], 'duplicate false is idempotent');
  assert.deepEqual(heart.otherList, [{ id: 'a' }, { id: 'unrelated' }], 'other lists remain untouched');
  const writes = heart.writes.length;
  heart.state.playMusicInfo = { musicInfo: { id: 'b' } }; heart.state.musicInfo = { id: 'b', lrc: null };
  await heart.api.changeSystemFavorite(event(false)); assert.equal(heart.writes.length, writes, 'stale unlike rejected');
  await heart.api.changeSystemFavorite(event(true)); assert.equal(heart.writes.length, writes, 'stale like rejected');
  await heart.api.changeSystemFavorite({ id: 'b', generation: gen, favorite: 'true' }); assert.equal(heart.writes.length, writes);
  const queued = fixture(); queued.api.initializeSystemMedia(); await queued.api.syncSystemMedia(true);
  let done; queued.setWriteWait(new Promise(resolve => { done = resolve })); const qgen = queued.calls.at(-1)[1];
  const add = queued.api.changeSystemFavorite({ id: 'a', generation: qgen, favorite: true }); await flush();
  const remove = queued.api.changeSystemFavorite({ id: 'a', generation: qgen, favorite: false });
  queued.state.playMusicInfo = { musicInfo: { id: 'b' } }; queued.state.musicInfo = { id: 'b', lrc: null }; queued.emit('playMusicInfoChanged'); done(); queued.setWriteWait(null); await add; await remove;
  assert.equal(queued.writes.length, 1, 'queued stale unlike does not mutate a newly selected song');
  assert.equal(queued.writes[0][1][0], 'a', 'in-flight authorized write uses captured music, not new selection');
  console.log('PASS system media: lyric lifecycle/races, mode semantics, add/remove target state, duplicate idempotence, other-list isolation and stale/queued favorite rejection');
})().catch(error => { console.error(error); process.exitCode = 1 });
