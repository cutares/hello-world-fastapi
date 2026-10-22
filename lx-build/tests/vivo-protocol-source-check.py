from pathlib import Path
import xml.etree.ElementTree as ET
r=Path(__file__).resolve().parents[2]/'track-player/android/src/main'
manifest=ET.parse(r/'AndroidManifest.xml')
ns='{http://schemas.android.com/apk/res/android}'
marker=next(e for e in manifest.findall('./application/meta-data') if e.get(ns+'name')=='support_vivo_musicwidgetmix_value')
assert marker.get(ns+'value')=='1001'
assert not any('token' in (e.get(ns+'name') or '').lower() for e in manifest.findall('.//meta-data'))
svc=next(e for e in manifest.findall('.//service') if e.get(ns+'name')=='.service.MusicService')
actions=[e.get(ns+'name') for e in svc.findall('./intent-filter/action')]
assert 'android.media.browse.MediaBrowserService' in actions
assert 'com.vivo.musicwidgetmix.support.service' in actions
s=(r/'java/com/guichaguri/trackplayer/service/MusicService.java').read_text()
for text in ['VIVO_MUSIC_MIX_ROOT','vivomusicmix_current_list','com.vivo.musicwidgetmix','parentId.contains(VIVO_CURRENT_LIST)','parentId.length() <= 256','vivoSubscribedParents.size() < 16','getBrowserItems(vivoList)','MediaBrowserCompat.MediaItem.FLAG_PLAYABLE']:
 assert text in s,text
assert 'if (!trusted) return null;' in s
assert 'isTrustedForMediaControl' in s and 'getPackagesForUid(uid)' in s
assert 'new Intent(intent)' in s and 'browserIntent.setAction("android.media.browse.MediaBrowserService")' in s
m=(r/'java/com/guichaguri/trackplayer/service/metadata/MetadataManager.java').read_text()
assert 'VIVO_BASIC_SUPPORT = 1L | 2L | 4L | 8L | 16L | 64L' in m
assert 'VIVO_QUEUE_SUPPORT = 256L | 2048L' in m
assert 'systemQueue.isEmpty() ? 0L : VIVO_QUEUE_SUPPORT' in m
assert 'metadata.putLong(VIVO_SUPPORT_EVENT, support)' in m
assert 'metadata.putString(MediaMetadataCompat.METADATA_KEY_MEDIA_ID, systemQueueIds.get(activeSystemQueueId))' in m
assert m.count('session.setMetadata(')==1,'All metadata writers must use centralized protocol merge'
assert 'if (prevMetadata != null) publishMetadata(prevMetadata);' in m
assert 'systemQueue.subList(start, systemQueue.size())' in m
b=(r/'java/com/guichaguri/trackplayer/service/metadata/ButtonEvents.java').read_text()
assert 'onPlayFromMediaId(String mediaId, Bundle extras)' in b
assert 'hasSystemQueueMediaId(mediaId)' in b and 'BUTTON_PLAY_FROM_ID' in b
print('PASS: verified vivo discovery/root/list contract, supported capability mask/type, centralized metadata merge, active ID and current-first browsing, existing trust preserved; source-level only.')
