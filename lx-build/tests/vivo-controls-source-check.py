"""Native regression invariants; source-level only, not Android runtime tests."""
from pathlib import Path
r=Path(__file__).resolve().parents[2]/'track-player/android/src/main/java/com/guichaguri/trackplayer'
m=(r/'service/metadata/MetadataManager.java').read_text()
b=(r/'service/metadata/ButtonEvents.java').read_text()
n=(r/'module/MusicModule.java').read_text()
binder=(r/'service/MusicBinder.java').read_text()
def method(text, signature):
 start=text.index(signature); brace=text.index('{',start); depth=1; end=brace+1
 while depth:
  depth += (text[end]=='{')-(text[end]=='}'); end+=1
 return text[brace:end]
for name in ['setSystemQueueContext','setSystemLyrics','setSystemFavorite','setSystemRepeatMode']:
 assert '@ReactMethod\n    public void '+name in n
 assert name in binder
 assert 'waitForConnection' in method(n, 'public void '+name)
for name in ['setSystemLyrics','setSystemFavorite']:
 body=method(m, 'public boolean '+name)
 assert 'generation < lyricGeneration' in body and 'generation <=' not in body
 assert '!mediaId.equals(activeId)' in body and 'destroyed' in body
 assert body.index('return false') < body.index('lyricGeneration = generation')
 assert 'controlMediaId = mediaId' in body
 assert '9007199254740991D' in method(n, 'public void '+name)
assert 'MAX_LYRIC_CHARS = 65536' in m and 'lyric.length() > MAX_LYRIC_CHARS ? NO_LYRICS' in m
assert '[00:00.00]暂无歌词' in m
for key in ['vivomusicmix.meida.extra.key.action','vivomusicmix.extra.lrc_change','vivomusicmix.extra.key.meidia_id','vivomusicmix.extra.key.lyric']:
 assert key in m
lyric=method(m,'private void sendLyricExtras')
assert 'session.getController().getExtras()' in lyric and 'new Bundle(current)' in lyric
assert 'session.setExtras(extras)' in lyric
queue=method(m,'public void setSystemQueue')
assert 'TextUtils.equals(previousActiveId, activeId)' in queue
assert 'controlMediaId = null' in queue and 'systemFavorite = false' in queue
assert 'publishLyrics(activeId, NO_LYRICS)' in queue
assert 'lyricGeneration =' not in queue
request=method(m,'public void requestSystemFavorite')
assert '!activeId.equals(controlMediaId)' in request and 'lyricGeneration < 0' in request
for x in ['request.putDouble("generation", lyricGeneration)','request.putBoolean("favorite", favorite)','remote-favorite-change']:
 assert x in request
meta=method(m,'private void publishMetadata')
assert 'metadata = new MediaMetadataCompat.Builder(metadata.build())' in meta
assert 'systemRepeatMode >= 1 && systemRepeatMode <= 3' in meta
assert 'if (systemRepeatMode != 0) metadata.putLong(VIVO_LOOP_MODE, systemRepeatMode)' in meta
assert 'METADATA_KEY_USER_RATING, RatingCompat.newHeartRating(systemFavorite)' in meta
assert 'METADATA_KEY_RATING, RatingCompat.newHeartRating(systemFavorite)' in meta
assert m.count('session.setMetadata(')==1
assert 'destroyed || prevMetadata != metadata' in m
assert 'new Handler(Looper.getMainLooper())' in m
assert 'vivomusicmix.media.action.PLAY_MODE' in b and 'remote-play-mode-change' in b
assert 'rating.getRatingStyle() == RatingCompat.RATING_HEART && rating.isRated()' in b
assert 'requestSystemFavorite(rating.hasHeart())' in b
assert 'getSystemQueueDiagnostics' not in n+m+b and 'LXSystemQueue' not in n+m+b
context=method(m,'public boolean setSystemQueueContext')
assert context.index('generation < lyricGeneration') < context.index('setSystemQueue(entries')
assert context.index('lyricGeneration = generation') < context.index('setSystemQueue(entries')
assert 'generation > lyricGeneration' in context
assert 'controlMediaId = null' in context and 'systemFavorite = false' in context
assert 'if (changedGeneration) publishLyrics' in context
print('PASS: native controls protocol, bounds, identity/generation guards, atomic queue context, fresh metadata and stale artwork protection (source-level).')
