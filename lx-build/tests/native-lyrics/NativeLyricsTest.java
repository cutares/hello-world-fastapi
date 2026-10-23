import android.os.Bundle;
import android.os.Handler;
import android.support.v4.media.session.MediaSessionCompat;
import com.guichaguri.trackplayer.service.MusicService;
import com.guichaguri.trackplayer.service.MusicManager;
import com.guichaguri.trackplayer.service.metadata.MetadataManager;
import java.util.Arrays;

public class NativeLyricsTest {
 static void check(boolean b,String message){if(!b)throw new AssertionError(message);}
 static Bundle entry(String id){Bundle b=new Bundle();b.putString("id",id);return b;}
 static String text(MediaSessionCompat session){return session.delivered.get(session.delivered.size()-1).getString("vivomusicmix.extra.key.lyric");}
 public static void main(String[] args){
  MusicManager manager=new MusicManager();
  MetadataManager metadata=new MetadataManager(new MusicService(),manager);manager.metadata=metadata;
  MediaSessionCompat session=metadata.getSession();
  manager.playback.track.systemMediaId="A";manager.playback.track.systemGeneration=1;
  metadata.setSystemQueueContext(Arrays.asList(entry("A")),"A",1);
  metadata.updateMetadata(manager.playback,manager.playback.track,true);
  metadata.setActive(true);
  metadata.setSystemLyrics("A",1,"[00:00.00]first");
  check(session.delivered.isEmpty(),"No remote listener existed for first push");
  check(session.getController().getExtras().getString("vivomusicmix.extra.key.lyric").contains("first"),"Extras retain full lyrics");
  session.listening=true;
  Handler.advance(199);check(session.delivered.isEmpty(),"Replay waits 200ms after update");
  Handler.advance(1);check(session.delivered.size()==1&&text(session).contains("first"),"Late subscriber receives delayed first LRC");
  // Same-content updates must replay even after an earlier successful local-ready publication.
  metadata.refreshSystemTiming(manager.playback);metadata.refreshSystemTiming(manager.playback);
  metadata.replaySystemLyrics(); // browser list load
  Handler.advance(200);check(session.delivered.size()==2,"Events coalesce but do not suppress identical cached lyrics");
  Handler.advance(10000);check(session.delivered.size()==2,"No periodic retry loop");
  manager.playback.state=2;metadata.refreshSystemTiming(manager.playback);
  Handler.advance(200);check(session.delivered.size()==3,"Paused same-context replay allowed");
  metadata.replaySystemLyrics();Runnable stale=Handler.snapshot().get(0);
  metadata.setSystemQueueContext(Arrays.asList(entry("B")),"B",2);
  check(!metadata.setSystemLyrics("A",1,"stale"),"Stale ID/generation rejected");
  int afterSwitch=session.delivered.size();stale.run();
  check(session.delivered.size()==afterSwitch,"Captured old runnable cannot publish after switch");
  metadata.setSystemQueueContext(Arrays.asList(entry("A")),"A",3);
  check(!metadata.setSystemLyrics("A",1,"stale-again"),"A-B-A stale generation rejected");
  manager.playback.track.systemGeneration=3;
  metadata.updateMetadata(manager.playback,manager.playback.track,false);
  metadata.setSystemLyrics("A",3,"[00:00.00]new");
  Handler.advance(200);check(text(session).contains("new"),"Current generation remains publishable");
  // Repeated metadata events must not keep moving the deadline indefinitely.
  int beforeContinuous=session.delivered.size();
  metadata.replaySystemLyrics();
  for(int i=0;i<4;i++){metadata.refreshSystemTiming(manager.playback);Handler.advance(50);}
  check(session.delivered.size()==beforeContinuous+1,"Continuous equal-payload events cannot starve replay");
  // A scheduled placeholder must never replace newer genuine lyrics.
  metadata.setSystemLyrics("A",3,"");Runnable placeholder=Handler.snapshot().get(0);
  metadata.setSystemLyrics("A",3,"[00:00.00]latest");int beforeOldPlaceholder=session.delivered.size();
  placeholder.run();check(session.delivered.size()==beforeOldPlaceholder,"Cancelled placeholder cannot overwrite genuine lyrics");
  Handler.advance(200);check(text(session).contains("latest"),"New genuine lyrics win");
  // Limitation: attaching long after all events does not itself generate an extras callback.
  session.listening=false;metadata.setSystemLyrics("A",3,"[00:00.00]retained");Handler.advance(200);
  int beforeLate=session.delivered.size();session.listening=true;Handler.advance(10000);
  check(session.delivered.size()==beforeLate,"No invented subscription acknowledgement or periodic retry");
  check(session.getController().getExtras().getString("vivomusicmix.extra.key.lyric").contains("retained"),"Late controller can still query persistent extras");
  metadata.refreshSystemTiming(manager.playback);Handler.advance(200);
  check(session.delivered.size()==beforeLate+1,"Next real event replays retained extras to late controller");
  metadata.replaySystemLyrics();int beforeDestroy=session.delivered.size();metadata.destroy();
  Handler.advance(200);check(session.delivered.size()==beforeDestroy,"Destroy cancels pending replay");
  System.out.println("PASS: actual native methods: late attach, delayed/coalesced identical replay, no timer loop, pause, stale runnable/ID/A-B-A, latest lyrics and destroy cancellation (platform fakes, not device test).");
 }
}
