const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const clip = vm.createContext({});
vm.runInContext(fs.readFileSync(`${__dirname}/../Clip.js`, 'utf8'), clip);
const history = clip.parse(JSON.stringify([
  {type:'text', text:'hello\nworld'}, {type:'unknown'},
  {type:'text', text:'https://example.org'},
  {type:'image', path:'/tmp/test.png'},
  {type:'text', text:'file:///tmp/a%20b.txt'},
  {type:'text', text:'#abc'}
]));
assert.equal(clip.rows(history, [], 'All', 'example')[0].historyIndex, 2);
assert.equal(clip.rows(history, [], 'Files', '')[0].chip, 'path');
assert.equal(clip.rows(history, [], 'Images', '').length, 1);
assert.equal(clip.rows(history, ['text:#abc'], 'Pins', '')[0].chip, 'color');
assert.equal(clip.rows(history, [], 'Text', 'hello world').length, 1);
assert.equal(clip.paths('file:///tmp/a%20b.txt')[0], '/tmp/a b.txt');
assert.equal(clip.rows(history, [], 'All', 'nothing').length, 0);
assert.throws(() => clip.parse('{broken'));
console.log('8 clipboard classification, filtering and index checks passed');
