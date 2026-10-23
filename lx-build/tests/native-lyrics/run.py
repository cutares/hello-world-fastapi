"""Compile actual MetadataManager/ButtonEvents against minimal platform fakes.
Tests observable delivery and identity logic, not Android Binder/platform integration.
"""
from pathlib import Path
import tempfile, subprocess, re, atexit, shutil
root=Path(__file__).resolve().parents[3]/'track-player/android/src/main/java'
# Local standalone layout fallback.
if not root.exists(): root=Path(__file__).resolve().parents[4]/'track-player/android/src/main/java'
work=Path(tempfile.mkdtemp(prefix='lx-native-lyrics-'))
atexit.register(shutil.rmtree,work)
src=work/'src'; out=work/'classes'
def put(name, code):
 p=src/(name.replace('.','/')+'.java');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(code)
def stub(name,body):
 pkg,cls=name.rsplit('.',1);put(name,'package '+pkg+';\n'+body)
for name in ['android.annotation.SuppressLint','androidx.annotation.NonNull','androidx.annotation.Nullable','androidx.media3.common.util.UnstableApi']:
 stub(name,'public @interface '+name.rsplit('.',1)[1]+' { String[] value() default {}; }')
stub('android.os.Bundle','''public class Bundle extends java.util.HashMap<String,Object> {
 public Bundle(){} public Bundle(Bundle b){super(b);} public void putString(String k,String v){put(k,v);} public String getString(String k){return (String)get(k);} public void putDouble(String k,double v){put(k,v);} public double getDouble(String k){return ((Number)get(k)).doubleValue();} public void putBoolean(String k,boolean v){put(k,v);} public void putInt(String k,int v){put(k,v);} public void putLong(String k,long v){put(k,v);} public Bundle getBundle(String k){return (Bundle)get(k);} public java.util.ArrayList<Integer> getIntegerArrayList(String k){return (java.util.ArrayList<Integer>)get(k);}
}''')
stub('android.os.Handler','''public class Handler {
 static long now;static java.util.Map<Runnable,Long> tasks=new java.util.LinkedHashMap<>();
 public Handler(Looper l){} public void postDelayed(Runnable r,long delay){tasks.put(r,now+delay);}public void removeCallbacks(Runnable r){tasks.remove(r);}
 public static java.util.List<Runnable> snapshot(){return new java.util.ArrayList<>(tasks.keySet());}
 public static void advance(long n){now+=n;for(Runnable r:new java.util.ArrayList<>(tasks.keySet()))if(tasks.containsKey(r)&&tasks.get(r)<=now){tasks.remove(r);r.run();}}
}''')
stub('android.os.Looper','public class Looper { public static Looper getMainLooper(){return new Looper();} }')
stub('android.os.Build','public class Build { public static String MANUFACTURER="test"; public static class VERSION { public static int SDK_INT=33; } public static class VERSION_CODES { public static int M=23; } }')
stub('android.text.TextUtils','public class TextUtils {public static boolean equals(CharSequence a,CharSequence b){return java.util.Objects.equals(a,b);}}')
stub('android.graphics.Bitmap','public class Bitmap {}')
stub('android.graphics.drawable.Drawable','public class Drawable {}')
stub('android.net.Uri','public class Uri { public static Uri parse(String s){return new Uri();} }')
stub('android.content.Intent','public class Intent {public static String CATEGORY_LAUNCHER="launcher",ACTION_VIEW="view"; public static int FLAG_ACTIVITY_CLEAR_TOP=1,FLAG_ACTIVITY_SINGLE_TOP=2; public void setPackage(String p){} public void addCategory(String s){} public void setFlags(int n){} public void setAction(String s){} public void setData(android.net.Uri u){} }')
stub('android.content.pm.PackageManager','public class PackageManager {public android.content.Intent getLaunchIntentForPackage(String s){return new android.content.Intent();}}')
stub('android.content.Context','public class Context {public static String NOTIFICATION_SERVICE="notification"; public Context getApplicationContext(){return this;} public String getPackageName(){return "test";} public android.content.pm.PackageManager getPackageManager(){return new android.content.pm.PackageManager();} public Object getSystemService(String s){return new android.app.NotificationManager();}}')
stub('android.app.NotificationManager','public class NotificationManager {public void cancelAll(){}}')
stub('android.app.PendingIntent','public class PendingIntent {public static int FLAG_CANCEL_CURRENT=1; public static PendingIntent getActivity(android.content.Context c,int i,android.content.Intent n,int f){return new PendingIntent();}}')
stub('android.support.v4.media.RatingCompat','public class RatingCompat { public static int RATING_NONE=0,RATING_HEART=1; boolean heart; public static RatingCompat newHeartRating(boolean b){RatingCompat r=new RatingCompat();r.heart=b;return r;} public int getRatingStyle(){return RATING_HEART;} public boolean isRated(){return true;} public boolean hasHeart(){return heart;} }')
metadata=(root/'com/guichaguri/trackplayer/service/metadata/MetadataManager.java').read_text()
keys=sorted(set(re.findall(r'METADATA_KEY_\w+',metadata)))
stub('android.support.v4.media.MediaMetadataCompat','''public class MediaMetadataCompat {
'''+''.join('public static final String '+k+'="'+k+'";\n' for k in keys)+'''
 android.os.Bundle b; MediaMetadataCompat(android.os.Bundle x){b=new android.os.Bundle(x);} public android.os.Bundle getBundle(){return new android.os.Bundle(b);} public String getString(String k){return b.getString(k);} public RatingCompat getRating(String k){return (RatingCompat)b.get(k);} public static class Builder {android.os.Bundle b=new android.os.Bundle(); public Builder(){} public Builder(MediaMetadataCompat m){b=m.getBundle();} public Builder putString(String k,String v){b.putString(k,v);return this;} public Builder putText(String k,CharSequence v){b.put(k,v);return this;} public Builder putLong(String k,long v){b.putLong(k,v);return this;} public Builder putBitmap(String k,android.graphics.Bitmap v){b.put(k,v);return this;} public Builder putRating(String k,RatingCompat v){b.put(k,v);return this;} public MediaMetadataCompat build(){return new MediaMetadataCompat(b);} }
}''')
stub('android.support.v4.media.MediaDescriptionCompat','public class MediaDescriptionCompat {String id; public String getMediaId(){return id;} public static class Builder {MediaDescriptionCompat d=new MediaDescriptionCompat(); public Builder setMediaId(String s){d.id=s;return this;} public Builder setTitle(String s){return this;} public Builder setSubtitle(String s){return this;} public Builder setDescription(String s){return this;} public MediaDescriptionCompat build(){return d;}}}')
stub('android.support.v4.media.session.PlaybackStateCompat','''public class PlaybackStateCompat {
 public static final int STATE_NONE=0,STATE_PAUSED=2,STATE_PLAYING=3,STATE_BUFFERING=6;
 public static final long ACTION_PLAY=1,ACTION_PAUSE=2,ACTION_STOP=4,ACTION_SKIP_TO_PREVIOUS=8,ACTION_SKIP_TO_NEXT=16,ACTION_REWIND=32,ACTION_FAST_FORWARD=64;
 int state;long id;public int getState(){return state;}public long getActiveQueueItemId(){return id;}
 public static class Builder {PlaybackStateCompat p=new PlaybackStateCompat();public Builder setActions(long a){return this;}public Builder setState(int s,long pos,float rate){p.state=s;return this;}public Builder setActiveQueueItemId(long id){p.id=id;return this;}public Builder setBufferedPosition(long n){return this;}public PlaybackStateCompat build(){return p;}}
}''')
stub('android.support.v4.media.session.MediaSessionCompat','''public class MediaSessionCompat {
 public static int FLAG_HANDLES_QUEUE_COMMANDS=1; boolean active; android.os.Bundle extras; android.support.v4.media.MediaMetadataCompat metadata; PlaybackStateCompat state; public Callback callback;
 public java.util.List<android.os.Bundle> delivered=new java.util.ArrayList<>(); public boolean listening=false;
 public MediaSessionCompat(android.content.Context c,String tag,Object a,Object b){} public void setFlags(int f){} public void setCallback(Callback c,android.os.Handler h){callback=c;} public void setRatingType(int n){} public void setQueueTitle(String s){} public void setQueue(java.util.List<QueueItem> q){} public void setMetadata(android.support.v4.media.MediaMetadataCompat m){metadata=m;} public void setExtras(android.os.Bundle e){extras=new android.os.Bundle(e);if(listening)delivered.add(new android.os.Bundle(e));} public void setPlaybackState(PlaybackStateCompat p){state=p;} public boolean isActive(){return active;}public void setActive(boolean a){active=a;}public void release(){}public Object getSessionToken(){return this;}public Controller getController(){return new Controller();}
 public class Controller {public android.os.Bundle getExtras(){return extras;}public android.support.v4.media.MediaMetadataCompat getMetadata(){return metadata;}public PlaybackStateCompat getPlaybackState(){return state;}}
 public static class QueueItem {public static final long UNKNOWN_ID=-1;long id;android.support.v4.media.MediaDescriptionCompat d;public QueueItem(android.support.v4.media.MediaDescriptionCompat d,long id){this.id=id;this.d=d;}public long getQueueId(){return id;}public android.support.v4.media.MediaDescriptionCompat getDescription(){return d;}}
 public static class Callback {public void onPlay(){}public void onPause(){}public void onStop(){}public void onPlayFromMediaId(String s,android.os.Bundle b){}public void onPlayFromSearch(String s,android.os.Bundle b){}public void onSkipToQueueItem(long n){}public void onSkipToPrevious(){}public void onSkipToNext(){}public void onRewind(){}public void onFastForward(){}public void onSeekTo(long n){}public void onSetRating(android.support.v4.media.RatingCompat r){}public void onCustomAction(String a,android.os.Bundle e){}}
}''')
stub('androidx.core.app.NotificationCompat','''public class NotificationCompat {
 public static int COLOR_DEFAULT=0,VISIBILITY_PUBLIC=1;public static String CATEGORY_TRANSPORT="transport";
 public static class Action {public Action(int i,String s,Object p){}}
 public static class Builder { public java.util.List<Action> mActions=new java.util.ArrayList<>();public Builder(android.content.Context c,String s){} public Builder setContentIntent(Object p){return this;}public Builder setSmallIcon(int i){return this;}public Builder setCategory(String s){return this;}public Builder setDeleteIntent(Object p){return this;}public Builder setVisibility(int i){return this;}public Builder setColor(int i){return this;}public Builder setLargeIcon(android.graphics.Bitmap b){return this;}public Builder setContentTitle(String s){return this;}public Builder setContentText(String s){return this;}public Builder setSubText(String s){return this;}public Builder setStyle(Object s){return this;}public Object build(){return this;}}
}''')
stub('androidx.media.app.NotificationCompat','public class NotificationCompat {public static class MediaStyle {public void setShowCancelButton(boolean b){}public void setCancelButtonIntent(Object o){}public void setMediaSession(Object o){}public void setShowActionsInCompactView(int[] a){}}}')
stub('androidx.media.session.MediaButtonReceiver','public class MediaButtonReceiver {public static Object buildMediaButtonPendingIntent(android.content.Context c,long a){return null;}}')
stub('com.bumptech.glide.Glide','public class Glide {public static RequestManager with(android.content.Context c){return new RequestManager();}}')
stub('com.bumptech.glide.RequestManager','public class RequestManager {public void clear(Object o){}public RequestManager asBitmap(){return this;}public RequestManager load(Object o){return this;}public RequestManager override(int a,int b){return this;}public RequestManager centerCrop(){return this;}public <T> com.bumptech.glide.request.target.CustomTarget<T> into(com.bumptech.glide.request.target.CustomTarget<T> t){return t;}}')
stub('com.bumptech.glide.request.target.CustomTarget','public abstract class CustomTarget<T> {public abstract void onResourceReady(T r,com.bumptech.glide.request.transition.Transition<? super T> t);public abstract void onLoadCleared(android.graphics.drawable.Drawable d);}')
stub('com.bumptech.glide.request.transition.Transition','public interface Transition<T> {}')
stub('com.facebook.react.views.imagehelper.ResourceDrawableIdHelper','public class ResourceDrawableIdHelper {public static ResourceDrawableIdHelper getInstance(){return new ResourceDrawableIdHelper();}public int getResourceDrawableId(android.content.Context c,String s){return 1;}}')
stub('com.guichaguri.trackplayer.R','public class R {public static class drawable {public static int play=1,pause=2,stop=3,previous=4,next=5,rewind=6,forward=7;}}')
stub('com.guichaguri.trackplayer.service.MusicService','public class MusicService extends android.content.Context {public void stopForeground(boolean b){}public void startForeground(int n,Object o){}public void onSystemQueueChanged(){}public void emit(String s,android.os.Bundle b){}}')
stub('com.guichaguri.trackplayer.service.MusicManager','public class MusicManager {public com.guichaguri.trackplayer.service.metadata.MetadataManager metadata;public com.guichaguri.trackplayer.service.player.ExoPlayback playback=new com.guichaguri.trackplayer.service.player.ExoPlayback();public com.guichaguri.trackplayer.service.player.ExoPlayback getPlayback(){return playback;}public com.guichaguri.trackplayer.service.metadata.MetadataManager getMetadata(){return metadata;}}')
stub('com.guichaguri.trackplayer.service.Utils','public class Utils {public static String getNotificationChannel(android.content.Context c){return "test";}public static int getInt(android.os.Bundle b,String k,int d){return d;}public static double toSeconds(long n){return n/1000.0;}public static void setRating(android.os.Bundle b,String k,android.support.v4.media.RatingCompat r){}}')
stub('com.guichaguri.trackplayer.service.models.TrackMetadata','public class TrackMetadata {public String systemMediaId,title,artist,album;public long systemGeneration=-1;public android.net.Uri artwork;public android.support.v4.media.MediaMetadataCompat.Builder toMediaMetadata(){return new android.support.v4.media.MediaMetadataCompat.Builder();}}')
stub('com.guichaguri.trackplayer.service.models.Track','public class Track extends TrackMetadata {}')
stub('com.guichaguri.trackplayer.service.player.ExoPlayback','public class ExoPlayback {public com.guichaguri.trackplayer.service.models.Track track=new com.guichaguri.trackplayer.service.models.Track();public int state=3;public com.guichaguri.trackplayer.service.models.Track getCurrentTrack(){return track;}public long getTimelineDuration(){return 120000;}public long getPosition(){return 1000;}public long getBufferedPosition(){return 5000;}public float getRate(){return 1;}public int getState(){return state;}}')
button=(root/'com/guichaguri/trackplayer/service/metadata/ButtonEvents.java').read_text()
events=sorted(set(re.findall(r'MusicEvents\.(\w+)',button)))
stub('com.guichaguri.trackplayer.module.MusicEvents','public class MusicEvents {'+''.join('public static String '+e+'="'+e+'";' for e in events)+'}')
extras=sorted(set(re.findall(r'MediaStore\.(EXTRA_\w+)',button)))
stub('android.provider.MediaStore','public class MediaStore {'+''.join('public static String '+e+'="'+e+'";' for e in extras)+'public static class Audio {'+''.join('public static class '+e+' {public static String ENTRY_CONTENT_TYPE="'+e+'";}' for e in ['Artists','Albums','Playlists','Genres','Media'])+'}}')
for name in ['MetadataManager','ButtonEvents']:
 put('com.guichaguri.trackplayer.service.metadata.'+name,(root/('com/guichaguri/trackplayer/service/metadata/'+name+'.java')).read_text())
put('NativeLyricsTest',(Path(__file__).parent/'NativeLyricsTest.java').read_text())
subprocess.run(['java','com.sun.tools.javac.Main','-nowarn','-d',str(out)]+[str(p) for p in src.rglob('*.java')],check=True)
subprocess.run(['java','-cp',str(out),'NativeLyricsTest'],check=True)
