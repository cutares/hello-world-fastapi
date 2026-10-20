"""Clean release must contain no native queue diagnostic API or instrumentation."""
from pathlib import Path
r=Path(__file__).resolve().parents[2]/'track-player/android/src/main/java/com/guichaguri/trackplayer'
sources={p.name:p.read_text() for p in r.rglob('*.java')}
all_source='\n'.join(sources.values())
for forbidden in ['getSystemQueueDiagnostics', 'logSystemQueue', 'LXSystemQueue', 'diagnosticEvents', 'diagnosticCount', 'diagnostic_failed', 'nativeQueueUpdates', 'browserBindCalls', 'browserRootCalls', 'browserAccepted', 'browserRejected', 'browserChildrenCalls', 'lastChildrenCount', 'lastBrowserPackage', 'lastBrowserUid']:
    assert forbidden not in all_source, forbidden
# Ensure instrumentation removal cannot accidentally strip the working bridge/protocol.
assert 'public void setSystemQueue(' in sources['MusicModule.java']
assert 'VIVO_DISCOVERY_ACTION' in sources['MusicService.java']
assert 'vivoSubscribedParents' in sources['MusicService.java']
assert 'isTrustedForMediaControl' in sources['MusicService.java']
assert 'publishMetadata(prevMetadata)' in sources['MetadataManager.java']
assert 'VIVO_QUEUE_SUPPORT = 256L | 2048L' in sources['MetadataManager.java']
assert 'hasSystemQueueMediaId(mediaId)' in sources['ButtonEvents.java']
print('PASS: native diagnostic API, logs, counters, event buffers and retained client identities removed; functional queue/vivo bridge preserved.')
