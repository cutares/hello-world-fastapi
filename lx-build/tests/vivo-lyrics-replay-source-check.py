"""Cold-start lyric delivery invariants; source-level only."""
from pathlib import Path
r=Path(__file__).resolve().parents[2]/'track-player/android/src/main/java/com/guichaguri/trackplayer'
m=(r/'service/metadata/MetadataManager.java').read_text()
s=(r/'service/MusicService.java').read_text()
b=(r/'service/MusicBinder.java').read_text()
def method(text, signature):
 start=text.index(signature); brace=text.index('{',start); depth=1; end=brace+1
 while depth:
  depth += (text[end]=='{')-(text[end]=='}'); end+=1
 return text[brace:end]
cache=method(m,'private void publishLyrics')
for x in ['cachedLyricId = mediaId','cachedLyricGeneration = lyricGeneration','cachedLyric = lyric','sendLyricExtras(mediaId, lyric)']:
 assert x in cache
check=method(m,'private boolean canReplaySystemLyrics')
for x in ['destroyed','cachedLyricGeneration != lyricGeneration','cachedLyricId.equals(systemQueueIds.get(activeSystemQueueId))','!session.isActive()','metadata.getString(MediaMetadataCompat.METADATA_KEY_MEDIA_ID)','matchesSystemContext(playback.getCurrentTrack())','publishedState.getState() == state','publishedState.getActiveQueueItemId() == activeSystemQueueId']:
 assert x in check,x
replay=method(m,'public void replaySystemLyrics')
assert replay.index('if (!canReplaySystemLyrics())') < replay.index('sendLyricExtras')
assert 'lyricHandler.postDelayed(pendingLyricReplay, 200)' in replay
assert 'if (pendingLyricReplay != this) return' in replay
assert 'generation == pendingLyricGeneration' in replay
assert 'lyricsAwaitingReady' not in m
state=method(m,'private void updatePlaybackState')
assert state.index('session.setPlaybackState(pb.build())') < state.index('replaySystemLyrics()')
active=method(m,'public void setActive')
assert active.index('this.session.setActive(active)') < active.index('if (active) replaySystemLyrics()')
assert 'if (knownRoot && manager != null) manager.getMetadata().replaySystemLyrics()' in s
assert 'metadata.setActive(true)' in method(b,'public void updateNowPlayingTitles')
assert 'cachedLyric = null' in method(m,'public void destroy')
assert 'lyricHandler.removeCallbacks(pendingLyricReplay)' in method(m,'public void destroy')
assert 'Timer' not in replay
print('PASS: cold-start cached LRC replays only for matching ID/generation/metadata/ready state after activation or browser request; event-driven bounded delay, no polling (source-level).')
