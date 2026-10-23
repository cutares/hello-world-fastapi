const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../../source');
const ts = require(root + '/node_modules/typescript');
const spec = JSON.parse(fs.readFileSync(root + '/src/resources/branding/vinyl.json'));
const source = fs.readFileSync(root + '/src/components/common/MusicLogo.tsx', 'utf8');
const moduleObject = { exports: {} };
const jsx = (type, props) => ({ type, props });
vm.runInNewContext(ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX } }).outputText, {
  exports: moduleObject.exports, module: moduleObject,
  require(name) {
    if (name === 'react') return { memo: fn => fn };
    if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx };
    if (name === 'react-native') return { View: 'View', StyleSheet: { create: styles => styles } };
    if (name === '@/utils/pixelRatio') return { scaleSizeW: size => size * 1.25 };
    if (name === '@/resources/branding/vinyl.json') return { default: spec };
    throw Error(name);
  },
});
for (const size of [22, 28, 48]) {
  const tree = moduleObject.exports.default({ size });
  assert.equal(tree.props.style[1].width, size * 1.25);
  assert.equal(tree.props.accessible, false);
  assert.equal(tree.props.pointerEvents, 'none');
  const art = tree.props.children;
  assert.equal(art.props.style[1].transform[0].scale, size * 1.25 / 100);
  const [disc, clip, start, end, hole] = art.props.children;
  assert.equal(disc.props.style.width / 2, spec.discRadius);
  assert.equal(disc.props.style.backgroundColor, spec.disc);
  assert.equal(disc.props.style.borderColor, spec.cream);
  assert.equal(clip.props.style.overflow, 'hidden');
  const ring = clip.props.children.props.style;
  assert.equal(ring.width / 2 - ring.borderWidth / 2, spec.arcRadius);
  assert.equal(ring.borderWidth, spec.arcWidth);
  assert.equal(start.props.style.left + start.props.style.width / 2, 50);
  assert.equal(start.props.style.top + start.props.style.height / 2, 50 - spec.arcRadius);
  assert.equal(end.props.style.left + end.props.style.width / 2, 50 + spec.arcRadius);
  assert.equal(end.props.style.top + end.props.style.height / 2, 50);
  assert.equal(hole.props.style.width / 2, spec.holeRadius);
}
console.log('PASS native Logo render tree: sizes/scale, quarter-ring geometry, round caps, center hole, dark-outline and decorative accessibility');
