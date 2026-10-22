const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '../../source');
const ts = require(root + '/node_modules/typescript');
const text = fs.readFileSync(root + '/src/plugins/player/playList.ts', 'utf8');
function fixture() {
  const music = { id: 'a', name: 'A', singer: 'Singer', meta: {} };
  const state = { playMusicInfo: { musicInfo: music }, musicInfo: { id: 'a', name: 'A' }, lastLyric: null };
  const tracks = []; const metadata = []; const order = []; let waitQueue = null; let waitState = null; let identity = 'queue-a'; let generation = 100;
  const api = { getCurrentTrack: async() => null, add: async items => { order.push('add'); tracks.push(...items) }, getQueue: async() => tracks, skip: async() => {}, play: async() => {}, pause: async() => {}, seekTo: async() => {}, remove: async() => {}, getState: async() => { if (waitState) await waitState; return 3 }, updateNowPlayingMetadata: async data => { metadata.push(data) } };
  const module = { exports: {} };
  vm.runInNewContext(ts.transpileModule(text + '\nexport { handlePlayMusic, updateMetaInfo, buildTracks };', { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText, {
    module, exports: module.exports, console, global: { lx: { restorePlayInfo: null } }, require(name) {
      if (name === 'react-native-track-player') return { default: api, State: { Playing: 3 } };
      if (name === 'react-native-background-timer') return { default: { setTimeout, clearTimeout } };
      if (name === '@/config') return { defaultUrl: 'placeholder' };
      if (name === '@/store/setting/state') return { default: { setting: {} } };
      if (name === '@/store/player/state') return { default: state };
      if (name === './systemQueue') return { syncSystemQueue: async() => { order.push('queue'); if (waitQueue) await waitQueue }, getCurrentSystemMediaId: () => identity, getSystemMediaGeneration: () => generation };
      throw Error(name);
    },
  });
  return { exports: module.exports, music, state, tracks, metadata, order, setWaitQueue: p => { waitQueue = p }, setWaitState: p => { waitState = p }, setIdentity: id => { identity = id }, advance: () => { generation++ } };
}
const flush = () => new Promise(resolve => setTimeout(resolve, 0));
(async() => {
  const f = fixture(); await f.exports.handlePlayMusic(f.music, 'https://example.invalid/audio', 0);
  assert.deepEqual(f.order.slice(0, 2), ['queue', 'add']);
  assert.equal(f.tracks[0].systemMediaId, 'queue-a'); assert.equal(f.tracks[0].systemGeneration, 100);
  assert.equal(f.tracks[1].systemMediaId, undefined, 'placeholder must not masquerade as real engine');
  await f.exports.updateMetaInfo(f.state.musicInfo); assert.equal(f.metadata[0].systemMediaId, 'queue-a'); assert.equal(f.metadata[0].systemGeneration, 100);
  f.state.lastLyric = 'Bluetooth lyric'; await f.exports.updateMetaInfo(f.state.musicInfo); assert.equal(f.metadata.at(-1).title, 'Bluetooth lyric');
  const race = fixture(); let release; race.setWaitQueue(new Promise(r => { release = r })); const pending = race.exports.handlePlayMusic(race.music, 'url', 0); await flush();
  race.state.playMusicInfo = { musicInfo: { id: 'b' } }; release(); await pending; assert.equal(race.tracks.length, 0);
  const stale = fixture(); let resume; stale.setWaitState(new Promise(r => { resume = r })); const old = stale.exports.updateMetaInfo(stale.state.musicInfo); await flush(); stale.advance(); resume(); await old; assert.equal(stale.metadata.length, 0);
  const failedQueue = fixture(); failedQueue.setIdentity(''); await failedQueue.exports.handlePlayMusic(failedQueue.music, 'url', 0); assert.equal(failedQueue.tracks.length, 2, 'queue publication failure must not break LX playback');
  console.log('PASS timing identity: publish before track, real vs placeholder, stale context/generation rejection, bluetooth title preserved and playback independent of queue publication');
})().catch(error => { console.error(error); process.exitCode = 1 });
