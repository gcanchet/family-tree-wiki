---
title: Relationship Finder
---
<style>
.finder-container { background: var(--highlight); padding: 25px; border-radius: 8px; border: 1px solid var(--gray); margin-top: 20px; }
.controls { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
input { padding: 10px; border-radius: 4px; border: 1px solid var(--gray); flex: 1; min-width: 200px; background: var(--light); color: var(--dark); }
button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
button:hover { background: #2980b9; }
#result { margin-top: 20px; padding: 20px; border-radius: 4px; background: var(--light); min-height: 50px; border-left: 5px solid #3498db; }
.path-step { display: block; margin-bottom: 10px; font-size: 1.1em; }
.highlight-name { font-weight: bold; color: #e67e22; }
</style>
<div class="finder-container">
<p>Select two family members to trace their relationship path.</p>
<div class="controls">
<input type="text" id="personA" list="peopleList" placeholder="Type first person's name...">
<input type="text" id="personB" list="peopleList" placeholder="Type second person's name...">
<datalist id="peopleList"></datalist>
<button onclick="findRelationship()">Trace Path</button>
</div>
<div id="result">Results will appear here...</div>
</div>
<script type="text/javascript">
//<![CDATA[

if (!window.familyData) { window.familyData = {}; }
if (!window.nameToIdMap) { window.nameToIdMap = {}; }
function initFinder() {
const resDiv = document.getElementById('result');
if (!resDiv) return;
if (Object.keys(window.familyData).length > 0) {
populateDropdowns();
return;
}
const isGitHub = window.location.hostname.indexOf('github.io') !== -1;
const dataPath = (isGitHub ? '/family-tree-wiki' : '') + '/wiki/outputs/family_data.json';
fetch(dataPath)
.then(function(response) {
if (!response.ok) throw new Error('File not found');
return response.json();
})
.then(function(data) {
window.familyData = data;
populateDropdowns();
})
.catch(function(err) {
resDiv.innerHTML = 'Error loading family data. Ensure the processing script was run.';
});
}
function populateDropdowns() {
const datalist = document.getElementById('peopleList');
if (!datalist) return;
datalist.innerHTML = '';
window.nameToIdMap = {};
const sortedIds = Object.keys(window.familyData).sort(function(a, b) { return window.familyData[a].name.localeCompare(window.familyData[b].name); });
sortedIds.forEach(function(id) {
const name = window.familyData[id].name;
window.nameToIdMap[name] = id;
const opt = document.createElement('option');
opt.value = name;
datalist.appendChild(opt);
});
}
function findRelationship() {
const nameA = document.getElementById('personA').value;
const nameB = document.getElementById('personB').value;
const start = window.nameToIdMap[nameA];
const end = window.nameToIdMap[nameB];
const resDiv = document.getElementById('result');
if (!start || !end) { resDiv.innerHTML = 'Select valid names.'; return; }
if (start === end) { resDiv.innerHTML = 'Same person selected.'; return; }
let queue = [[start, []]];
let visited = new Set([start]);
while (queue.length !== 0) {
let [currentId, path] = queue.shift();
if (currentId === end) { displayPath(path); return; }
const person = window.familyData[currentId];
if (!person) continue;
const connections = [
...(person.parents ? person.parents : []).map(function(id) { return {id:id, rel:'is child of', type:'UP'}; }),
...(person.children ? person.children : []).map(function(id) { return {id:id, rel:'is parent of', type:'DOWN'}; }),
...(person.spouse ? person.spouse : []).map(function(id) { return {id:id, rel:'is spouse of', type:'SIDE'}; }),
...(person.siblings ? person.siblings : []).map(function(id) { return {id:id, rel:'is sibling of', type:'SIB'}; })
];
for (let i = 0; i < connections.length; i++) {
const conn = connections[i];
if (!visited.has(conn.id)) {
if (window.familyData[conn.id]) {
visited.add(conn.id);
queue.push([conn.id, [...path, {from: currentId, to: conn.id, label: conn.rel, type: conn.type}]]);
}}}}}
function getRelationshipTerm(path) {
let types = path.map(function(p) { return p.type; });
let prefix = '';
let suffix = '';
if (types[0] === 'SIDE') { prefix = "Spouse's "; types.shift(); }
if (types.length !== 0) { if (types[types.length - 1] === 'SIDE') { suffix = '-in-law'; types.pop(); } }
const pattern = types.join('-');
const staticMap = { '': 'Spouse', 'UP': 'Parent', 'UP-UP': 'Grandparent', 'UP-UP-UP': 'Great-Grandparent', 'DOWN': 'Child', 'DOWN-DOWN': 'Grandchild', 'DOWN-DOWN-DOWN': 'Great-Grandchild', 'SIDE': 'Spouse', 'SIB': 'Sibling', 'UP-SIDE': 'Step-Parent', 'SIDE-UP': 'Parent-in-law', 'SIDE-DOWN': 'Step-Child', 'DOWN-SIDE': 'Child-in-law', 'SIDE-SIB': 'Sibling-in-law', 'SIB-SIDE': 'Sibling-in-law', 'UP-SIB': 'Uncle / Aunt', 'SIB-DOWN': 'Nephew / Niece', 'UP-SIDE-DOWN': 'Step-Sibling' };
let result = staticMap[pattern];
if (!result) {
const sibIndex = types.indexOf('SIB');
if (sibIndex !== -1) {
const upCount = types.slice(0, sibIndex).filter(function(t) { return t === 'UP'; }).length;
const downCount = types.slice(sibIndex + 1).filter(function(t) { return t === 'DOWN'; }).length;
if (upCount > 1 && downCount === 0) {
let p = 'Grand ';
for (let i = 0; i < upCount - 2; i++) { p = 'Grand ' + p; }
result = p + 'Uncle / Aunt';
} else if (downCount > 1 && upCount === 0) {
let p = 'Grand ';
for (let i = 0; i < downCount - 2; i++) { p = 'Grand ' + p; }
result = p + 'Nephew / Niece';
} else if (upCount > 0 && downCount > 0) {
const k = Math.min(upCount, downCount), m = Math.abs(upCount - downCount);
const s = ['th', 'st', 'nd', 'rd'], v = k % 100;
let su = s[(v - 20) % 10] || s[v] || s[0];
result = k + su + ' Cousin';
if (m > 0) { result += ' ' + m + 'x removed'; }
}}}
if (!result) {
const tu = types.filter(function(t) { return t === 'UP'; }).length;
const td = types.filter(function(t) { return t === 'DOWN'; }).length;
if (tu > 3 && types.every(function(t) { return t === 'UP'; })) { result = (tu - 2) + 'x Great-Grandparent'; }
else if (td > 3 && types.every(function(t) { return t === 'DOWN'; })) { result = (td - 2) + 'x Great-Grandchild'; }
}
if (!result) { result = 'Relative (' + path.length + ' degrees)'; }
if (suffix === '-in-law' && (result.indexOf('in-law') !== -1 || result.indexOf('Step-') !== -1)) { suffix = ''; prefix = "Spouse's "; }
return prefix + result + suffix;
}
function displayPath(path) {
const term = getRelationshipTerm(path);
const startPerson = window.familyData[path[0].from].name;
const endPerson = window.familyData[path[path.length - 1].to].name;
let h = '<h3>' + endPerson + ' is the ' + term + ' of ' + startPerson + '</h3><h4>Path:</h4>';
path.forEach(function(step, i) {
const f = window.familyData[step.from] ? window.familyData[step.from].name : step.from;
const t = window.familyData[step.to] ? window.familyData[step.to].name : step.to;
h += '<span class="path-step">' + (i + 1) + '. ' + f + ' ' + step.label + ' ' + t + '</span>';
});
document.getElementById('result').innerHTML = h;
}
initFinder();
document.removeEventListener('nav', initFinder);
document.addEventListener('nav', initFinder);
</script>
//]]>