const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, '../../source/src');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
for (const removed of ['core/version.ts', 'utils/version.js', 'navigation/components/VersionModal.tsx']) {
  assert.equal(fs.existsSync(path.join(root, removed)), false, `${removed} must be removed, not just hidden`);
}
const forbidden = [
  /from\s+['"]@\/(?:core|utils)\/version['"]/, /\bcheckUpdate\s*\(/,
  /\bshowVersionModal\b/, /\bVERSION_MODAL\b/, /\bdownloadNewVersion\b/,
  /lx-music-mobile-version-info/, /publish\/version\.json/, /lx-music-mobile-versions\/raw/,
];
function scan(dir) {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const file = path.join(dir, item.name);
    if (item.isDirectory()) scan(file);
    else if (/\.(?:js|ts|tsx)$/.test(file)) {
      const content = fs.readFileSync(file, 'utf8');
      for (const pattern of forbidden) assert.equal(pattern.test(content), false, `${path.relative(root, file)}: ${pattern}`);
    }
  }
}
scan(root);
const version = read('screens/Home/Views/Setting/settings/Version.tsx');
assert.match(version, /process\.versions\.app/);
assert.match(version, /version_label_current_ver/);
assert.doesNotMatch(version, /store\/version|version_label_latest_ver|setting_version_show_ver_modal|version_btn_/);
assert.doesNotMatch(version, /Button|NativeModules|useEffect|系统播控诊断|复制诊断/);
assert.equal(fs.existsSync(path.join(root, 'plugins/player/systemQueueDiagnostics.ts')), false);
assert.doesNotMatch(read('plugins/player/systemQueue.ts'), /syncDiagnostics|getSystemQueueSyncDiagnostics/);
const about = read('screens/Home/Views/Setting/settings/About.tsx');
assert.doesNotMatch(about, /openGHReleasePage|GitHub Releases|最新版下载地址/);
assert.match(about, /openHomePage/);
assert.match(about, /openFAQPage/);
assert.match(about, /openPactModal/);
assert.match(read('core/init/index.ts'), /void initDeeplink\(\)/);
assert.match(read('navigation/components/PactModal.tsx'), /void initDeeplink\(\)/);
assert.match(read('navigation/components/PactModal.tsx'), /Apache License 2\.0/);
assert.match(read('navigation/registerScreens.tsx'), /PACT_MODAL/);
assert.match(read('navigation/utils.ts'), /showSyncModeModal/);
console.log('PASS: app update requests/downloads/modal removed; startup and consent paths clean; read-only version/about/license/deeplink preserved.');
