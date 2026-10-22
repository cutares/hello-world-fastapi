const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../../source');
const ts = require(root + '/node_modules/typescript');
const code = fs.readFileSync(root + '/src/core/player/player.ts', 'utf8');
const snippet = code.slice(code.indexOf('const handleRestorePlay ='), code.indexOf('// 处理音乐播放')) + '\nexports.restore = handleRestorePlay; exports.normal = debouncePlay;';
function fixture() {
  const music = { id: 'a' }; const playerState = { playMusicInfo: { listId: 'main', musicInfo: music }, musicInfo: { id: 'a', pic: null } };
  let resolve; const updates = [];
  const ctx = { exports: {}, playerState, setTimeout: fn => fn(), settingState: { setting: { 'player.togglePlayMethod': 'listLoop' } },
    global: { app_event: { setProgress() {}, picUpdated() {}, lyricUpdated() {} }, i18n: { t: x => x } },
    initTrackInfo() {}, setMusicUrl() {}, getPicPath: async() => null, getLyricInfo: () => new Promise(r => { resolve = r }),
    setMusicInfo: info => updates.push(info), setStatusText() {}, addPlayedList() {}, debounceBackgroundTimer: fn => fn, console: { log() {} },
  };
  vm.runInNewContext(ts.transpileModule(snippet, { compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS } }).outputText, ctx);
  return { ctx, music, updates, finish: () => resolve({ lyric: 'OLD_A', rawlrcInfo: { lyric: '' } }) };
}
const flush = () => new Promise(resolve => setTimeout(resolve, 0));
(async() => {
  for (const type of ['restore', 'normal']) {
    const f = fixture();
    if (type === 'restore') await f.ctx.exports.restore({ time: 0, maxTime: 10 }); else f.ctx.exports.normal(f.music);
    f.ctx.playerState.playMusicInfo = { listId: 'main', musicInfo: { id: 'b' } };
    f.ctx.playerState.playMusicInfo = { listId: 'main', musicInfo: { id: 'a' } };
    f.finish(); await flush(); assert.equal(f.updates.some(x => x.lrc === 'OLD_A'), false);
    const current = fixture();
    if (type === 'restore') await current.ctx.exports.restore({ time: 0, maxTime: 10 }); else current.ctx.exports.normal(current.music);
    current.finish(); await flush(); assert.equal(current.updates.some(x => x.lrc === 'OLD_A'), true);
  }
  console.log('PASS: restored/normal lyric callbacks reject old A-B-A contexts and accept current results');
})().catch(error => { console.error(error); process.exitCode = 1 });
