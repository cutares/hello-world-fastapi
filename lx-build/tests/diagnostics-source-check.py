from pathlib import Path
r=Path(__file__).resolve().parents[2]/'track-player/android/src/main/java/com/guichaguri/trackplayer'
module=(r/'module/MusicModule.java').read_text()
method=module.split('public void getSystemQueueDiagnostics(final Promise callback) {',1)[1].split('    @ReactMethod',1)[0]
assert 'UiThreadUtil.runOnUiThread' in method
assert 'waitForConnection' not in method and 'startService' not in method and 'setupPlayer' not in method
assert '"serviceAvailable", false' in method and '"bridgeAvailable", true' in method
assert 'error.getMessage' not in method and 'error.toString' not in method
service=(r/'service/MusicService.java').read_text()
assert 'diagnosticEvents.size() >= 24' in service and 'diagnosticEvents.removeFirst()' in service
assert 'safe.length() > 256' in service
assert "message.replace('\\n', ' ').replace('\\r', ' ')" in service
for k in ['browserBindCalls','browserRootCalls','browserAccepted','browserRejected','browserChildrenCalls','lastChildrenCount','lastBrowserPackage','lastBrowserUid','events','playbackPresent','playbackState']:
 assert f'"{k}"' in service
metadata=(r/'service/metadata/MetadataManager.java').read_text()
getter=metadata.split('public Bundle getSystemQueueDiagnostics() {',1)[1].split('    private void publishMetadata',1)[0]
for k in ['queueCount','activeItemPresent','sessionActive','actionSkipToQueue','actionPlayFromId','metadataMediaIdPresent','nativeQueueUpdates']:
 assert f'"{k}"' in getter
for bad in ['putString(', 'putParcelable', 'putStringArrayList', 'METADATA_KEY_TITLE', '.getMediaId()', '.getDescription()']:
 assert bad not in getter, bad
assert 'getState()' in service and 'getPlayback().getQueue()' not in service
print('PASS: diagnostics schema, bounded sanitized events, no playback initialization, no media details in snapshot; source-level only.')
