"""Structural regression checks, not Android runtime or compilation tests."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
r = Path(__file__).resolve().parents[2] / 'track-player/android/src/main'
s = (r / 'java/com/guichaguri/trackplayer/service/MusicService.java').read_text()
h = (r / 'java/com/guichaguri/trackplayer/service/HeadlessJsTaskService.java').read_text()
m = (r / 'java/com/guichaguri/trackplayer/service/metadata/MetadataManager.java').read_text()
b = (r / 'java/com/guichaguri/trackplayer/service/MusicBinder.java').read_text()
e = (r / 'java/com/guichaguri/trackplayer/service/metadata/ButtonEvents.java').read_text()
def method(text, name, params=r'[^)]*'):
    hit = re.search(r'\b' + name + r'\(' + params + r'\)\s*\{', text)
    assert hit, name
    start = hit.end(); depth = 1
    for i in range(start, len(text)):
        if text[i] == '{': depth += 1
        if text[i] == '}':
            depth -= 1
            if depth == 0: return text[start:i]
    raise AssertionError(name)
assert 'extends MediaBrowserServiceCompat' in h
assert 'return super.onBind(intent)' in method(h, 'onBind')
assert 'Utils.CONNECT_INTENT' in method(s, 'onBind') and 'return super.onBind(intent)' in method(s, 'onBind')
assert s.count('new MusicManager(this)') == 1 and s.count('setSessionToken(') == 1
assert 'new MusicManager' in method(s, 'onCreate') and 'setSessionToken' in method(s, 'onCreate')
assert 'startForeground' not in method(s, 'onCreate')
assert 'new MusicManager' not in method(s, 'onStartCommand')
assert 'manager.destroy()' in method(s, 'releaseResources')
assert 'releaseResources()' in method(s, 'onDestroy')
assert 'releaseResources()' not in method(s, 'stopPlayer') and 'manager = null' not in method(s, 'stopPlayer')
assert 'service.stopPlayer()' in method(b, 'destroy')
assert 'getPackagesForUid(uid)' in method(s, 'isTrustedBrowser')
assert 'if (!ownsPackage) return false' in method(s, 'isTrustedBrowser')
assert 'isTrustedForMediaControl' in method(s, 'isTrustedBrowser')
assert 'if (!trusted) return null' in method(s, 'onGetRoot')
assert 'BROWSER_ROOT.equals(parentId)' in method(s, 'onLoadChildren')
assert 'FLAG_PLAYABLE' in method(s, 'getBrowserItems', 'boolean currentFirst')
assert 'notifyChildrenChanged(BROWSER_ROOT)' in method(s, 'onSystemQueueChanged')
assert 'service.onSystemQueueChanged()' in method(m, 'setSystemQueue')
assert 'queue.size() >= 200' in m and 'mediaId.length() > 512' in m
assert 'logSystemQueue' not in s
assert 'if (!known) return' in method(e, 'onPlayFromMediaId')
assert 'getPlayback' not in method(e, 'onSkipToQueueItem')
manifest = ET.parse(r / 'AndroidManifest.xml').getroot()
a = '{http://schemas.android.com/apk/res/android}'
service = manifest.find('./application/service')
assert service.get(a + 'exported') == 'true'
actions = [x.get(a + 'name') for x in service.findall('./intent-filter/action')]
assert 'android.media.browse.MediaBrowserService' in actions
assert 'android.intent.action.MEDIA_BUTTON' in actions
print('PASS: browser inheritance/binding, single session lifetime, bind-only idle, stop-vs-destroy, UID/package trust, bounded browse queue, notifications, clean release without diagnostic logs, stale selection rejection, manifest actions.')
