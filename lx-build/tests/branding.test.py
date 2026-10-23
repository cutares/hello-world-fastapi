from pathlib import Path
import json
import struct
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2] / 'source'
RES = ROOT / 'android/app/src/main/res'
subprocess.run(['python3', str(ROOT / 'scripts/generate-branding.py'), '--check'], check=True)
for density, size in [('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)]:
    for suffix in ['', '_round']:
        data = (RES / f'mipmap-{density}/ic_launcher{suffix}.png').read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II', data[16:24]) == (size, size)
ns = '{http://schemas.android.com/apk/res/android}'
foreground = ET.parse(RES / 'drawable/ic_launcher_foreground.xml').getroot()
assert foreground.attrib[ns + 'width'] == '108dp'
assert foreground.attrib[ns + 'viewportWidth'] == '108'
group = foreground.find('group')
scale, offset = float(group.attrib[ns + 'scaleX']), float(group.attrib[ns + 'translateX'])
assert offset + 2 * scale >= 21 and offset + 98 * scale <= 87, 'disc must fit central 66dp safe zone'
for path in RES.glob('values*/strings.xml'):
    for item in ET.parse(path).getroot().findall('string'):
        if item.attrib.get('name') == 'app_name': assert item.text == 'Music'
app = json.loads((ROOT / 'app.json').read_text())
assert app['name'] == 'LX Music', 'internal RN identity must not change'
assert app['displayName'] == 'Music'
pkg = json.loads((ROOT / 'package.json').read_text())
assert pkg['version'] == '1.9.1' and pkg['versionCode'] == 85
manifest = ET.parse(ROOT / 'android/app/src/main/AndroidManifest.xml').getroot().find('application')
assert manifest.attrib[ns + 'icon'] == '@mipmap/ic_launcher'
assert manifest.attrib[ns + 'roundIcon'] == '@mipmap/ic_launcher_round'
assert manifest.attrib[ns + 'label'] == '@string/app_name'
assert 'applicationId "com.luna.music"' in (ROOT / 'android/app/build.gradle').read_text()
for file in ['Vertical/DrawerNav.tsx', 'Horizontal/Aside.tsx']:
    text = (ROOT / 'src/screens/Home' / file).read_text()
    assert '<MusicLogo size=' in text and '>Music</Text>' in text
    assert '<Icon name="logo"' not in text
logo = (ROOT / 'src/components/common/MusicLogo.tsx').read_text()
assert 'borderColor: vinyl.cream' in logo, 'keep dark-theme disc edge contrast'
assert 'importantForAccessibility="no-hide-descendants"' in logo
assert (ROOT / 'LICENSE').exists()
print('PASS branding: reproducible 10 PNGs, adaptive safe zone, menu variants, Music labels, preserved internal identity and license')
