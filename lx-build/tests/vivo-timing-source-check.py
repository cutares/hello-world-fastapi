"""Native timing wiring/race invariants. Not a device/runtime test."""
from pathlib import Path
r=Path(__file__).resolve().parents[2]/'track-player'
a=r/'android/src/main/java/com/guichaguri/trackplayer'
m=(a/'service/metadata/MetadataManager.java').read_text()
e=(a/'service/player/ExoPlayback.java').read_text()
b=(a/'service/MusicBinder.java').read_text()
t=(a/'service/models/TrackMetadata.java').read_text()
def method(text, signature):
 start=text.index(signature); brace=text.index('{',start); depth=1; end=brace+1
 while depth:
  depth += (text[end]=='{')-(text[end]=='}'); end+=1
 return text[brace:end]
for field in ['systemMediaId','systemGeneration']:
 assert field in t and field in (r/'src/interfaces.ts').read_text()
check=method(m,'private boolean matchesSystemContext')
assert 'activeId.equals(track.systemMediaId)' in check and 'track.systemGeneration == lyricGeneration' in check
assert '!destroyed && track != null && activeId != null' in check
accept=method(m,'public boolean acceptsSystemMetadata')
assert 'track.systemMediaId == null && track.systemGeneration < 0' in accept
body=method(b,'public void updateNowPlayingMetadata')
assert body.index('acceptsSystemMetadata(nowPlaying)') < body.index('metadata.updateMetadata')
body=method(m,'public void updateMetadata')
assert body.index('acceptsSystemMetadata(track)') < body.index('prevMetadata = metadata')
refresh=method(m,'public void refreshSystemTiming')
assert 'playback != manager.getPlayback()' in refresh and 'matchesSystemContext(playback.getCurrentTrack())' in refresh
assert refresh.index('publishMetadata(prevMetadata)') < refresh.index('updatePlaybackState(playback)')
assert 'updateMetadata(' not in refresh and 'updateNotification' not in refresh
meta=method(m,'private void publishMetadata')
assert 'metadata = withoutDuration(metadata.build())' in meta
assert meta.index('matchesSystemContext(playback.getCurrentTrack())') < meta.index('getTimelineDuration()')
assert 'if (duration > 0) metadata.putLong(METADATA_KEY_DURATION, duration)' in meta
assert 'if (METADATA_KEY_DURATION.equals(key)) continue' in m
assert 'prevMetadata != metadata' in m, 'Keep previous stale-artwork guard'
events=method(e,'public void onEvents')
for event in ['EVENT_TIMELINE_CHANGED','EVENT_PLAYBACK_STATE_CHANGED','EVENT_PLAY_WHEN_READY_CHANGED','EVENT_IS_PLAYING_CHANGED','EVENT_POSITION_DISCONTINUITY','EVENT_MEDIA_ITEM_TRANSITION','EVENT_PLAYBACK_PARAMETERS_CHANGED']:
 assert event in events
assert 'manager.getMetadata().refreshSystemTiming(this)' in events
assert 'shouldAutoUpdateMetadata' not in events and 'setTimeout' not in events
raw=method(e,'public long getTimelineDuration')
assert 'player.getDuration()' in raw and 'C.TIME_UNSET' in raw and 'duration <= 0' in raw
assert 'current.duration' not in raw
state=method(m,'private void updatePlaybackState')
assert 'matchesSystemContext(playback.getCurrentTrack())' in state
assert 'pb.setActions(actions)' in state and 'playback.getPosition()' in state
assert 'PlaybackStateCompat.STATE_BUFFERING' in state and 'PlaybackStateCompat.STATE_NONE' in state
assert m.count('session.setMetadata(')==1
print('PASS: event-driven native timing, real-engine duration with ID/generation guard, no stale JS duration overwrite, placeholder exclusion, latest position/actions, custom titles retained (source-level).')
