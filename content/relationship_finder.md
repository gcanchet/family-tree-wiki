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

<script>
let familyData = {};
let nameToIdMap = {};

// Use a relative path to fetch the JSON from the root
fetch('wiki/outputs/family_data.json')
    .then(response => response.json())
    .then(data => {
        familyData = data;
        populateDropdowns();
    })
    .catch(err => {
        document.getElementById('result').innerHTML = "Error: Could not load family_data.json. Ensure Action [1] was run and the file was pushed.";
    });

function populateDropdowns() {
    const datalist = document.getElementById('peopleList');
    if (!datalist) return;
    datalist.innerHTML = '';
    nameToIdMap = {};

    const sortedIds = Object.keys(familyData).sort((a, b) => familyData[a].name.localeCompare(familyData[b].name));
    
    sortedIds.forEach(id => {
        const name = familyData[id].name;
        nameToIdMap[name] = id;
        const opt = document.createElement('option');
        opt.value = name;
        datalist.appendChild(opt);
    });
}

function findRelationship() {
    const nameA = document.getElementById('personA').value;
    const nameB = document.getElementById('personB').value;
    const start = nameToIdMap[nameA];
    const end = nameToIdMap[nameB];
    const resDiv = document.getElementById('result');

    if (!start || !end) { resDiv.innerHTML = "Please select valid names from the list."; return; }
    if (start === end) { resDiv.innerHTML = "You selected the same person twice."; return; }

    let queue = [[start, []]];
    let visited = new Set([start]);

    while (queue.length > 0) {
        let [currentId, path] = queue.shift();
        if (currentId === end) {
            displayPath(path);
            return;
        }
        const person = familyData[currentId];
        if (!person) continue;
        const connections = [
            ...(person.parents || []).map(id => ({id, rel: "is the child of", type: "UP"})),
            ...(person.children || []).map(id => ({id, rel: "is the parent of", type: "DOWN"})),
            ...(person.spouse || []).map(id => ({id, rel: "is the spouse of", type: "SIDE"})),
            ...(person.siblings || []).map(id => ({id, rel: "is the sibling of", type: "SIB"}))
        ];
        for (let conn of connections) {
            if (!visited.has(conn.id) && familyData[conn.id]) {
                visited.add(conn.id);
                queue.push([conn.id, [...path, {from: currentId, to: conn.id, label: conn.rel, type: conn.type}]]);
            }
        }
    }
    resDiv.innerHTML = "No direct genealogical path found.";
}

function getRelationshipTerm(path) {
    let types = path.map(p => p.type);
    let prefix = "";
    let suffix = "";
    if (types[0] === 'SIDE') { prefix = "Spouse's "; types.shift(); }
    if (types.length > 0 && types[types.length - 1] === 'SIDE') { suffix = "-in-law"; types.pop(); }
    const pattern = types.join('-');
    const staticMap = {
        '': 'Spouse', 'UP': 'Parent', 'UP-UP': 'Grandparent', 'UP-UP-UP': 'Great-Grandparent',
        'DOWN': 'Child', 'DOWN-DOWN': 'Grandchild', 'DOWN-DOWN-DOWN': 'Great-Grandchild',
        'SIDE': 'Spouse', 'SIB': 'Sibling', 'UP-SIDE': 'Step-Parent', 'SIDE-UP': 'Parent-in-law',
        'SIDE-DOWN': 'Step-Child', 'DOWN-SIDE': 'Child-in-law', 'SIDE-SIB': 'Sibling-in-law',
        'SIB-SIDE': 'Sibling-in-law', 'UP-SIB': 'Uncle / Aunt', 'SIB-DOWN': 'Nephew / Niece',
        'UP-SIDE-DOWN': 'Step-Sibling'
    };
    let result = staticMap[pattern] || null;
    const sibIndex = types.indexOf('SIB');
    if (!result && sibIndex !== -1) {
        const upCount = types.slice(0, sibIndex).filter(t => t === 'UP').length;
        const downCount = types.slice(sibIndex + 1).filter(t => t === 'DOWN').length;
        if (upCount > 1 && downCount === 0) {
            let p = "Grand "; for (let i = 0; i < upCount - 2; i++) p = "Great-" + p;
            result = p + "Uncle / Aunt";
        } else if (downCount > 1 && upCount === 0) {
            let p = "Grand "; for (let i = 0; i < downCount - 2; i++) p = "Great-" + p;
            result = p + "Nephew / Niece";
        } else if (upCount > 0 && downCount > 0) {
            const k = Math.min(upCount, downCount), m = Math.abs(upCount - downCount);
            const getOrdinal = (n) => { const s = ["th", "st", "nd", "rd"], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); };
            result = `${getOrdinal(k)} Cousin`; if (m > 0) result += ` ${m}x removed`;
        }
    }
    if (!result) {
        const totalUps = types.filter(t => t === 'UP').length;
        const totalDowns = types.filter(t => t === 'DOWN').length;
        if (totalUps > 3 && types.every(t => t === 'UP')) result = `${totalUps - 2}x Great-Grandparent`;
        else if (totalDowns > 3 && types.every(t => t === 'DOWN')) result = `${totalDowns - 2}x Great-Grandchild`;
    }
    if (!result) result = `Distant Relative (${path.length} degrees)`;
    if (suffix === "-in-law" && (result.includes("in-law") || result.includes("Step-"))) { suffix = ""; prefix = "Spouse's "; }
    return prefix + result + suffix;
}

function displayPath(path) {
    const term = getRelationshipTerm(path);
    const startPerson = familyData[path[0].from].name;
    const endPerson = familyData[path[path.length - 1].to].name;
    let html = `<h3>Result: <span class="highlight-name">${endPerson}</span> is the <span class="highlight-name">${term}</span> of <span class="highlight-name">${startPerson}</span></h3>`;
    html += "<h4>Path Analysis:</h4>";
    path.forEach((step, index) => {
        const fromName = familyData[step.from] ? familyData[step.from].name : step.from;
        const toName = familyData[step.to] ? familyData[step.to].name : step.to;
        html += `<span class="path-step">${index + 1}. <span class="highlight-name">${fromName}</span> ${step.label} <span class="highlight-name">${toName}</span></span>`;
    });
    document.getElementById('result').innerHTML = html;
}
</script>